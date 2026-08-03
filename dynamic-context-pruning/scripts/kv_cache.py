"""
KV-Cache Optimization — Validation and fixing for KV-cache friendly context.
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class CacheIssueType(Enum):
    NON_DETERMINISTIC_JSON = "non_deterministic_json"
    TIMESTAMPS_IN_PREFIX = "timestamps_in_prefix"
    MODIFIED_PREVIOUS_MESSAGES = "modified_previous_messages"
    UNSTABLE_TOOL_DEFINITIONS = "unstable_tool_definitions"
    UNSTABLE_SYSTEM_PROMPT = "unstable_system_prompt"
    DYNAMIC_CONTENT_IN_PREFIX = "dynamic_content_in_prefix"


@dataclass
class CacheIssue:
    issue_type: CacheIssueType
    severity: str  # "critical", "warning", "info"
    message: str
    location: str  # e.g., "message[5].timestamp"
    suggestion: str


@dataclass
class KVCacheConfig:
    enforce_stable_prefix: bool = True
    append_only: bool = True
    deterministic_json: bool = True
    max_prefix_tokens: int = 50000


class KVCacheOptimizer:
    """Validates and fixes context for KV-cache efficiency."""

    def __init__(self, config: KVCacheConfig = None):
        self.config = config or KVCacheConfig()

    @classmethod
    def from_config(cls, config_path: str) -> "KVCacheOptimizer":
        with open(config_path) as f:
            config_data = json.load(f)
        kv_config = config_data.get("kv_cache", {})
        return cls(KVCacheConfig(
            enforce_stable_prefix=kv_config.get("enforce_stable_prefix", True),
            append_only=kv_config.get("append_only", True),
            deterministic_json=kv_config.get("deterministic_json", True),
            max_prefix_tokens=kv_config.get("max_prefix_tokens", 50000),
        ))

    def validate(self, context: List[Dict[str, Any]]) -> List[CacheIssue]:
        """Validate context for KV-cache efficiency. Returns list of issues."""
        issues = []

        # Check 1: Deterministic JSON serialization
        if self.config.deterministic_json:
            issues.extend(self._check_deterministic_json(context))

        # Check 2: Stable prefix (no timestamps, dynamic content)
        if self.config.enforce_stable_prefix:
            issues.extend(self._check_stable_prefix(context))

        # Check 3: Append-only (no modifications to previous messages)
        if self.config.append_only:
            issues.extend(self._check_append_only(context))

        # Check 4: Stable tool definitions
        issues.extend(self._check_tool_definitions(context))

        # Check 5: Stable system prompt
        issues.extend(self._check_system_prompt(context))

        return issues

    def _check_deterministic_json(self, context: List[Dict[str, Any]]) -> List[CacheIssue]:
        """Check for non-deterministic JSON (unordered dicts, sets, etc.)."""
        issues = []
        for i, entry in enumerate(context):
            # Check for dict keys that might be unordered in serialization
            serialized = json.dumps(entry, sort_keys=False)
            serialized_sorted = json.dumps(entry, sort_keys=True)
            if serialized != serialized_sorted:
                issues.append(CacheIssue(
                    issue_type=CacheIssueType.NON_DETERMINISTIC_JSON,
                    severity="warning",
                    message="Entry serialization is non-deterministic (keys not sorted)",
                    location=f"context[{i}]",
                    suggestion="Use json.dumps(data, sort_keys=True) for all serialization",
                ))
        return issues

    def _check_stable_prefix(self, context: List[Dict[str, Any]]) -> List[CacheIssue]:
        """Check for timestamps or dynamic content in prefix."""
        issues = []
        # Check first ~30% of context for dynamic content
        prefix_end = max(1, len(context) // 3)
        
        for i in range(min(prefix_end, len(context))):
            entry = context[i]
            entry_str = json.dumps(entry, sort_keys=True)
            
            # Look for timestamps
            import re
            timestamp_patterns = [
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
                r"\d{10,13}",  # Unix timestamps
                r"timestamp",
                r"created_at",
                r"updated_at",
            ]
            
            for pattern in timestamp_patterns:
                if re.search(pattern, entry_str, re.IGNORECASE):
                    issues.append(CacheIssue(
                        issue_type=CacheIssueType.TIMESTAMPS_IN_PREFIX,
                        severity="critical",
                        message=f"Timestamp/dynamic content detected in prefix: {pattern}",
                        location=f"context[{i}]",
                        suggestion="Move timestamps to metadata or remove from context prefix",
                    ))
                    break  # One issue per entry is enough
        return issues

    def _check_append_only(self, context: List[Dict[str, Any]]) -> List[CacheIssue]:
        """Check for modifications to previous messages."""
        issues = []
        # Track message IDs/content hashes
        seen_hashes = {}
        
        for i, entry in enumerate(context):
            # Create hash of entry content (excluding metadata fields)
            content = {k: v for k, v in entry.items() 
                      if not k.startswith("_") and k not in ("timestamp", "id")}
            content_hash = hash(json.dumps(content, sort_keys=True))
            
            if content_hash in seen_hashes:
                # Check if content actually changed
                prev_idx = seen_hashes[content_hash]
                prev_entry = context[prev_idx]
                if entry != prev_entry:
                    issues.append(CacheIssue(
                        issue_type=CacheIssueType.MODIFIED_PREVIOUS_MESSAGES,
                        severity="critical",
                        message=f"Message at index {i} appears to be modified version of index {prev_idx}",
                        location=f"context[{i}] (duplicate of context[{prev_idx}])",
                        suggestion="Never modify previous messages. Append corrections as new entries.",
                    ))
            else:
                seen_hashes[content_hash] = i
        return issues

    def _check_tool_definitions(self, context: List[Dict[str, Any]]) -> List[CacheIssue]:
        """Check for unstable tool definitions."""
        issues = []
        tool_defs = {}
        
        for i, entry in enumerate(context):
            if entry.get("type") == "tool_definition" or "tools" in entry:
                tools = entry.get("tools", entry.get("function_declarations", []))
                if isinstance(tools, list):
                    for tool in tools:
                        name = tool.get("name", tool.get("function", {}).get("name"))
                        if name:
                            tool_str = json.dumps(tool, sort_keys=True)
                            if name in tool_defs:
                                if tool_defs[name] != tool_str:
                                    issues.append(CacheIssue(
                                        issue_type=CacheIssueType.UNSTABLE_TOOL_DEFINITIONS,
                                        severity="critical",
                                        message=f"Tool '{name}' definition changed",
                                        location=f"context[{i}]",
                                        suggestion="Tool definitions must be stable. Define once at start, never modify.",
                                    ))
                            else:
                                tool_defs[name] = tool_str
        return issues

    def _check_system_prompt(self, context: List[Dict[str, Any]]) -> List[CacheIssue]:
        """Check for unstable system prompt."""
        issues = []
        system_prompts = []
        
        for i, entry in enumerate(context):
            if entry.get("role") == "system" or entry.get("type") == "system_prompt":
                content = entry.get("content", entry.get("prompt", ""))
                system_prompts.append((i, content))
        
        if len(system_prompts) > 1:
            first_content = system_prompts[0][1]
            for idx, content in system_prompts[1:]:
                if content != first_content:
                    issues.append(CacheIssue(
                        issue_type=CacheIssueType.UNSTABLE_SYSTEM_PROMPT,
                        severity="critical",
                        message="System prompt changed during conversation",
                        location=f"context[{idx}]",
                        suggestion="System prompt must be stable. Define once at start.",
                    ))
        return issues

    def fix(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Automatically fix common KV-cache issues."""
        fixed = copy.deepcopy(context)
        
        # Fix 1: Ensure deterministic JSON by sorting keys in all entries
        if self.config.deterministic_json:
            for i, entry in enumerate(fixed):
                fixed[i] = self._sort_dict_recursively(entry)
        
        # Fix 2: Remove timestamps from prefix entries
        if self.config.enforce_stable_prefix:
            prefix_end = max(1, len(fixed) // 3)
            for i in range(min(prefix_end, len(fixed))):
                fixed[i] = self._remove_timestamps(fixed[i])
        
        # Fix 3: Stabilize tool definitions (keep first occurrence only)
        tool_defs = {}
        for i, entry in enumerate(fixed):
            if entry.get("type") == "tool_definition" or "tools" in entry:
                tools = entry.get("tools", entry.get("function_declarations", []))
                if isinstance(tools, list):
                    stable_tools = []
                    for tool in tools:
                        name = tool.get("name", tool.get("function", {}).get("name"))
                        if name and name not in tool_defs:
                            tool_defs[name] = tool
                            stable_tools.append(tool)
                        elif name and name in tool_defs:
                            # Use first definition
                            stable_tools.append(tool_defs[name])
                    fixed[i]["tools"] = stable_tools
        
        # Fix 4: Stabilize system prompt (keep first only)
        system_prompt_idx = None
        for i, entry in enumerate(fixed):
            if entry.get("role") == "system" or entry.get("type") == "system_prompt":
                if system_prompt_idx is None:
                    system_prompt_idx = i
                    entry.get("content", entry.get("prompt", ""))
                else:
                    # Remove duplicate system prompts
                    fixed[i] = {"type": "system_prompt_removed", "original_index": i}
        
        return fixed

    def _sort_dict_recursively(self, obj: Any) -> Any:
        """Recursively sort dictionary keys."""
        if isinstance(obj, dict):
            return {k: self._sort_dict_recursively(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [self._sort_dict_recursively(item) for item in obj]
        return obj

    def _remove_timestamps(self, obj: Any) -> Any:
        """Remove timestamp fields from object."""
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                if not any(t in k.lower() for t in ["timestamp", "time", "date", "created", "updated"]):
                    result[k] = self._remove_timestamps(v)
            return result
        elif isinstance(obj, list):
            return [self._remove_timestamps(item) for item in obj]
        return obj


def main():
    import argparse
    parser = argparse.ArgumentParser(description="KV-Cache Optimizer CLI")
    parser.add_argument("--config", default=".agent_context_config.json")
    parser.add_argument("--input", required=True, help="Input context JSON file")
    parser.add_argument("--output", help="Output fixed context JSON file")
    parser.add_argument("--validate", action="store_true", help="Validate context for cache issues")
    parser.add_argument("--fix", action="store_true", help="Fix context cache issues")
    args = parser.parse_args()

    optimizer = KVCacheOptimizer.from_config(args.config)

    with open(args.input) as f:
        context = json.load(f)

    if args.validate:
        issues = optimizer.validate(context)
        if issues:
            print(f"Found {len(issues)} cache issues:")
            for issue in issues:
                print(f"  [{issue.severity.upper()}] {issue.issue_type.value}: {issue.message}")
                print(f"    Location: {issue.location}")
                print(f"    Suggestion: {issue.suggestion}")
        else:
            print("No cache issues found ✓")

    if args.fix:
        fixed = optimizer.fix(context)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(fixed, f, indent=2)
            print(f"Fixed context written to {args.output}")
        else:
            print(json.dumps(fixed, indent=2))

    if not args.validate and not args.fix:
        parser.error("Either --validate or --fix required")


if __name__ == "__main__":
    import copy
    main()