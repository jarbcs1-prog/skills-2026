"""
Summarization — Structured irreversible summarization with explicit schemas.
Never use free-form summarization. Always use structured outputs.
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path


@dataclass
class SummarySchema:
    """Defines the structure for structured summaries."""
    fields: List[str]
    required: List[str]
    description: str = ""

    def validate(self, summary: Dict[str, Any]) -> List[str]:
        """Validate summary against schema. Returns list of errors."""
        errors = []
        for field in self.required:
            if field not in summary:
                errors.append(f"Missing required field: {field}")
        for field in summary:
            if field not in self.fields:
                errors.append(f"Unknown field: {field}")
        return errors


# Predefined schemas
SCHEMAS = {
    "agent_default": SummarySchema(
        fields=[
            "files_modified",
            "user_goals",
            "current_state",
            "pending_actions",
            "errors_encountered",
            "key_decisions",
        ],
        required=["user_goals", "current_state"],
        description="General agent summary with 6 fields",
    ),
    "opencode_5_heading": SummarySchema(
        fields=[
            "current_state",
            "completed_actions",
            "pending_actions",
            "key_decisions",
            "errors_encountered",
        ],
        required=["current_state", "pending_actions"],
        description="OpenCode standard 5-heading summary",
    ),
    "minimal": SummarySchema(
        fields=[
            "current_state",
            "pending_actions",
        ],
        required=["current_state", "pending_actions"],
        description="Minimal 2-field summary for token-critical situations",
    ),
}


@dataclass
class SummarizationConfig:
    schema: SummarySchema
    keep_recent_full: int = 3
    model: str = "opencode/big-pickle"
    max_summary_tokens: int = 2000


@dataclass
class SummarizationResult:
    summary: Dict[str, Any]
    schema_used: str
    tokens_estimated: int
    entries_summarized: int
    entries_preserved: int
    validation_errors: List[str]


class Summarizer:
    """Structured summarizer that produces schema-compliant summaries."""

    def __init__(self, config: SummarizationConfig):
        self.config = config

    @classmethod
    def from_config(cls, config_path: str, platform: str = "auto") -> "Summarizer":
        with open(config_path) as f:
            config_data = json.load(f)
        
        summ_config = config_data.get("summarization", {})
        schema_name = summ_config.get("schema", "auto")
        
        # Auto-select schema based on platform
        if schema_name == "auto":
            if platform == "opencode":
                schema_name = "opencode_5_heading"
            else:
                schema_name = "agent_default"
        
        schema = SCHEMAS.get(schema_name, SCHEMAS["agent_default"])
        
        config = SummarizationConfig(
            schema=schema,
            keep_recent_full=summ_config.get("keep_recent_full", 3),
            model=summ_config.get("model", "opencode/big-pickle"),
            max_summary_tokens=summ_config.get("max_summary_tokens", 2000),
        )
        return cls(config)

    def summarize(self, context_history: List[Dict[str, Any]]) -> SummarizationResult:
        """Generate structured summary from context history."""
        # Keep recent entries verbatim
        recent = context_history[-self.config.keep_recent_full:] if self.config.keep_recent_full > 0 else []
        to_summarize = context_history[:-self.config.keep_recent_full] if self.config.keep_recent_full > 0 else context_history

        if not to_summarize:
            # Nothing to summarize
            empty_summary = {field: [] for field in self.config.schema.fields}
            return SummarizationResult(
                summary=empty_summary,
                schema_used=self.config.schema.description,
                tokens_estimated=0,
                entries_summarized=0,
                entries_preserved=len(recent),
                validation_errors=[],
            )

        # Build summary according to schema
        summary = self._build_summary(to_summarize)
        
        # Validate
        errors = self.config.schema.validate(summary)
        
        # Estimate tokens
        tokens = len(json.dumps(summary, sort_keys=True)) // 4
        
        return SummarizationResult(
            summary=summary,
            schema_used=self.config.schema.description,
            tokens_estimated=tokens,
            entries_summarized=len(to_summarize),
            entries_preserved=len(recent),
            validation_errors=errors,
        )

    def _build_summary(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build summary dict according to schema fields."""
        summary = {}
        
        # Track data for each field
        files_modified = set()
        user_goals = []
        current_state_parts = []
        pending_actions = []
        errors_encountered = []
        key_decisions = []
        completed_actions = []

        for entry in context:
            entry_type = entry.get("type", "")
            
            # Track file modifications
            if entry_type in ("tool_call", "file_edit") and "path" in entry:
                files_modified.add(entry["path"])
            if "file" in entry:
                files_modified.add(entry["file"])
            
            # Extract goals from user messages
            if entry_type == "user_message" or entry.get("role") == "user":
                content = entry.get("content", entry.get("message", ""))
                if content:
                    user_goals.append(content[:200])  # Truncate
            
            # Build current state
            if entry_type in ("tool_call", "assistant_message", "action"):
                desc = entry.get("description", entry.get("content", entry.get("summary", "")))
                if desc:
                    current_state_parts.append(f"{entry_type}: {desc[:150]}")
            
            # Track pending actions
            if entry_type == "todo" or entry.get("status") == "pending":
                action = entry.get("content", entry.get("description", ""))
                if action:
                    pending_actions.append(action[:200])
            
            # Track errors
            if entry.get("error") or entry_type == "error":
                error_msg = entry.get("error", entry.get("message", "Unknown error"))
                errors_encountered.append(str(error_msg)[:200])
            
            # Track decisions
            if entry_type in ("decision", "choice") or "decision" in entry:
                decision = entry.get("decision", entry.get("content", ""))
                if decision:
                    key_decisions.append(decision[:200])
            
            # Track completed actions
            if entry_type in ("completed", "done") or entry.get("status") == "completed":
                action = entry.get("content", entry.get("description", ""))
                if action:
                    completed_actions.append(action[:200])

        # Populate summary fields
        if "files_modified" in self.config.schema.fields:
            summary["files_modified"] = list(files_modified)[:20]
        if "user_goals" in self.config.schema.fields:
            summary["user_goals"] = user_goals[-5:]  # Last 5 goals
        if "current_state" in self.config.schema.fields:
            summary["current_state"] = " | ".join(current_state_parts[-10:])
        if "pending_actions" in self.config.schema.fields:
            summary["pending_actions"] = pending_actions[-10:]
        if "errors_encountered" in self.config.schema.fields:
            summary["errors_encountered"] = errors_encountered[-10:]
        if "key_decisions" in self.config.schema.fields:
            summary["key_decisions"] = key_decisions[-10:]
        if "completed_actions" in self.config.schema.fields:
            summary["completed_actions"] = completed_actions[-10:]

        return summary

    def validate(self, summary: Dict[str, Any], original_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate summary quality against original context."""
        errors = self.config.schema.validate(summary)
        
        # Check coverage
        coverage = {}
        if "files_modified" in summary:
            coverage["files_modified"] = len(summary["files_modified"])
        if "user_goals" in summary:
            coverage["user_goals"] = len(summary["user_goals"])
        if "pending_actions" in summary:
            coverage["pending_actions"] = len(summary["pending_actions"])
        if "errors_encountered" in summary:
            coverage["errors_encountered"] = len(summary["errors_encountered"])
        if "key_decisions" in summary:
            coverage["key_decisions"] = len(summary["key_decisions"])

        return {
            "valid": len(errors) == 0,
            "schema_errors": errors,
            "coverage": coverage,
            "summary_tokens": len(json.dumps(summary, sort_keys=True)) // 4,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Structured Summarization CLI")
    parser.add_argument("--config", default=".agent_context_config.json")
    parser.add_argument("--input", required=True, help="Input context JSON file")
    parser.add_argument("--output", required=True, help="Output summary JSON file")
    parser.add_argument("--schema", choices=list(SCHEMAS.keys()) + ["auto"], default="auto")
    parser.add_argument("--platform", choices=["generic", "opencode", "auto"], default="auto")
    parser.add_argument("--validate", action="store_true", help="Validate summary against original")
    args = parser.parse_args()

    # Load context
    with open(args.input) as f:
        context = json.load(f)

    # Determine platform
    platform = args.platform
    if platform == "auto":
        import os
        if os.environ.get("OPENCODE_SESSION_ID") or Path(".opencode").exists():
            platform = "opencode"
        else:
            platform = "generic"

    # Select schema
    if args.schema == "auto":
        schema_name = "opencode_5_heading" if platform == "opencode" else "agent_default"
    else:
        schema_name = args.schema

    schema = SCHEMAS[schema_name]
    config = SummarizationConfig(
        schema=schema,
        keep_recent_full=3,
        model="opencode/big-pickle",
    )

    summarizer = Summarizer(config)
    result = summarizer.summarize(context)

    # Write summary
    with open(args.output, "w") as f:
        json.dump(result.summary, f, indent=2)

    print(f"Summary generated: {result.entries_summarized} entries summarized, {result.entries_preserved} preserved")
    print(f"Schema: {result.schema_used}")
    print(f"Estimated tokens: {result.tokens_estimated}")
    if result.validation_errors:
        print(f"Validation errors: {result.validation_errors}")

    if args.validate:
        validation = summarizer.validate(result.summary, context)
        print(f"Validation: {'PASS' if validation['valid'] else 'FAIL'}")
        print(f"Coverage: {validation['coverage']}")


if __name__ == "__main__":
    main()