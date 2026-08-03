"""
Compaction — Reversible context reduction with multiple strategies.
Supports both Generic (4 strategies) and OpenCode (4 strategies) modes.
"""

import json
import copy
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from enum import Enum
from abc import ABC, abstractmethod


class CompactionStrategy(Enum):
    # Generic strategies
    TOKEN_BUDGET = "token_budget"
    AGE_BASED = "age_based"
    IMPORTANCE_BASED = "importance_based"
    HYBRID = "hybrid"
    # OpenCode strategies
    TIMESTAMP_HIDING = "timestamp_hiding"
    HEAD_TAIL_PROTECTION = "head_tail_protection"
    REPEATED_TOOL_PRUNING = "repeated_tool_pruning"
    ERROR_PRESERVATION = "error_preservation"


@dataclass
class CompactionConfig:
    strategy: CompactionStrategy = CompactionStrategy.HYBRID
    keep_recent_full: int = 5
    compact_ratio: float = 0.5
    preserve_structure: bool = True
    protect_zones: List[str] = field(default_factory=lambda: ["head", "tail"])
    max_tool_output_tokens: int = 2000
    importance_weights: Dict[str, float] = field(default_factory=lambda: {
        "user_goals": 1.0,
        "errors": 0.9,
        "key_decisions": 0.8,
        "tool_outputs": 0.5,
        "intermediate_steps": 0.3,
    })


@dataclass
class CompactionResult:
    compacted_context: List[Dict[str, Any]]
    offloaded_data: List[Dict[str, Any]]
    strategy_used: CompactionStrategy
    tokens_saved: int
    entries_compacted: int
    entries_preserved: int


class BaseCompactor(ABC):
    """Base class for compaction strategies."""

    def __init__(self, config: CompactionConfig):
        self.config = config

    @abstractmethod
    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        pass

    def restore(self, compacted: List[Dict[str, Any]], offload_path: str) -> List[Dict[str, Any]]:
        """Restore full context from compacted + offloaded data."""
        with open(offload_path) as f:
            offloaded = json.load(f)
        # Simple restoration: replace context_reference entries with full data
        restored = []
        offloaded_idx = 0
        for entry in compacted:
            if entry.get("type") == "context_reference" and "ref" in entry:
                entry["ref"]
                if offloaded_idx < len(offloaded):
                    restored.extend(offloaded[offloaded_idx])
                    offloaded_idx += 1
            else:
                restored.append(entry)
        return restored


class TokenBudgetCompactor(BaseCompactor):
    """Generic: Allocate token budget across history segments."""

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        # Estimate tokens per entry (simplified)
        def estimate_tokens(entry):
            return len(json.dumps(entry, sort_keys=True)) // 4

        total_tokens = sum(estimate_tokens(e) for e in context)
        budget = int(total_tokens * (1 - self.config.compact_ratio))

        # Keep recent entries fully
        recent = context[-self.config.keep_recent_full:]
        recent_tokens = sum(estimate_tokens(e) for e in recent)
        remaining_budget = budget - recent_tokens

        if remaining_budget <= 0:
            # Budget too tight, just keep recent
            compacted = recent
            offloaded = context[:-self.config.keep_recent_full]
        else:
            # Fill remaining budget with oldest entries
            older = context[:-self.config.keep_recent_full]
            compacted_older = []
            offloaded = []
            used = 0
            for entry in older:
                est = estimate_tokens(entry)
                if used + est <= remaining_budget:
                    compacted_older.append(entry)
                    used += est
                else:
                    offloaded.append(entry)
            compacted = compacted_older + recent
            offloaded = offloaded

        return CompactionResult(
            compacted_context=compacted,
            offloaded_data=offloaded,
            strategy_used=CompactionStrategy.TOKEN_BUDGET,
            tokens_saved=sum(estimate_tokens(e) for e in offloaded),
            entries_compacted=len(offloaded),
            entries_preserved=len(compacted),
        )


class AgeBasedCompactor(BaseCompactor):
    """Generic: Compact oldest N% of tool calls."""

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        num_to_compact = int(len(context) * self.config.compact_ratio)
        # Protect recent entries
        protect_count = min(self.config.keep_recent_full, len(context) - num_to_compact)
        if protect_count < 0:
            protect_count = 0

        offloaded = context[:len(context) - num_to_compact - protect_count]
        compacted = context[len(context) - num_to_compact - protect_count:]

        return CompactionResult(
            compacted_context=compacted,
            offloaded_data=offloaded,
            strategy_used=CompactionStrategy.AGE_BASED,
            tokens_saved=sum(len(json.dumps(e)) // 4 for e in offloaded),
            entries_compacted=len(offloaded),
            entries_preserved=len(compacted),
        )


class ImportanceBasedCompactor(BaseCompactor):
    """Generic: Score tool calls by relevance, compact lowest."""

    def _score_entry(self, entry: Dict[str, Any]) -> float:
        """Score entry based on importance weights."""
        score = 0.5  # base score
        entry_type = entry.get("type", "")
        if entry_type in self.config.importance_weights:
            score = self.config.importance_weights[entry_type]
        # Boost recent entries
        if "timestamp" in entry:
            score *= 1.1
        return score

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        # Score all entries
        scored = [(self._score_entry(e), i, e) for i, e in enumerate(context)]
        scored.sort(key=lambda x: x[0])  # lowest importance first

        num_to_compact = int(len(context) * self.config.compact_ratio)
        # Always protect recent
        recent_indices = set(range(len(context) - self.config.keep_recent_full, len(context)))
        
        to_compact_indices = set()
        for score, idx, entry in scored:
            if len(to_compact_indices) >= num_to_compact:
                break
            if idx not in recent_indices:
                to_compact_indices.add(idx)

        compacted = []
        offloaded = []
        for i, entry in enumerate(context):
            if i in to_compact_indices:
                offloaded.append(entry)
            else:
                compacted.append(entry)

        return CompactionResult(
            compacted_context=compacted,
            offloaded_data=offloaded,
            strategy_used=CompactionStrategy.IMPORTANCE_BASED,
            tokens_saved=sum(len(json.dumps(e)) // 4 for e in offloaded),
            entries_compacted=len(offloaded),
            entries_preserved=len(compacted),
        )


class HybridCompactor(BaseCompactor):
    """Generic: Combine age + importance (default)."""

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        # Use 70% age-based, 30% importance-based
        age_compactor = AgeBasedCompactor(self.config)
        imp_compactor = ImportanceBasedCompactor(self.config)
        
        # Get results from both
        age_result = age_compactor.compact(context)
        imp_result = imp_compactor.compact(context)
        
        # Merge: entries compacted by either strategy
        offloaded_ids = set()
        for e in age_result.offloaded_data:
            offloaded_ids.add(id(e))
        for e in imp_result.offloaded_data:
            offloaded_ids.add(id(e))
        
        # Build final result preserving original order
        compacted = []
        offloaded = []
        for entry in context:
            if id(entry) in offloaded_ids:
                offloaded.append(entry)
            else:
                compacted.append(entry)

        return CompactionResult(
            compacted_context=compacted,
            offloaded_data=offloaded,
            strategy_used=CompactionStrategy.HYBRID,
            tokens_saved=sum(len(json.dumps(e)) // 4 for e in offloaded),
            entries_compacted=len(offloaded),
            entries_preserved=len(compacted),
        )


# OpenCode-specific compactors

class TimestampHidingCompactor(BaseCompactor):
    """OpenCode: Native non-destructive timestamp-based message hiding."""

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        # Hide entries older than threshold by marking them hidden
        # Keep last N fully visible
        visible_count = self.config.keep_recent_full
        
        compacted = []
        offloaded = []
        
        for i, entry in enumerate(context):
            if i < len(context) - visible_count:
                # Hide older entries
                hidden_entry = copy.deepcopy(entry)
                hidden_entry["_hidden"] = True
                hidden_entry["_hidden_reason"] = "timestamp_hiding"
                offloaded.append(entry)  # Full data offloaded
                compacted.append(hidden_entry)  # Marked as hidden
            else:
                compacted.append(entry)
        
        return CompactionResult(
            compacted_context=compacted,
            offloaded_data=offloaded,
            strategy_used=CompactionStrategy.TIMESTAMP_HIDING,
            tokens_saved=sum(len(json.dumps(e)) // 4 for e in offloaded),
            entries_compacted=len(offloaded),
            entries_preserved=len(compacted),
        )


class HeadTailProtectionCompactor(BaseCompactor):
    """OpenCode: Token budgeting per tool output, keeping head/tail, pruning middle."""

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        compacted = []
        offloaded = []
        
        for entry in context:
            if entry.get("type") == "tool_call" and "output" in entry:
                output = entry["output"]
                if isinstance(output, str) and len(output) > self.config.max_tool_output_tokens * 4:
                    # Prune middle, keep head and tail
                    head = output[:self.config.max_tool_output_tokens * 2]
                    tail = output[-self.config.max_tool_output_tokens * 2:]
                    
                    compacted_entry = copy.deepcopy(entry)
                    compacted_entry["output"] = head + "\n... [pruned] ...\n" + tail
                    compacted_entry["_pruned"] = True
                    compacted_entry["_original_length"] = len(output)
                    
                    offloaded.append(entry)  # Full output offloaded
                    compacted.append(compacted_entry)
                else:
                    compacted.append(entry)
            else:
                compacted.append(entry)
        
        return CompactionResult(
            compacted_context=compacted,
            offloaded_data=offloaded,
            strategy_used=CompactionStrategy.HEAD_TAIL_PROTECTION,
            tokens_saved=sum(len(json.dumps(e)) // 4 for e in offloaded),
            entries_compacted=len(offloaded),
            entries_preserved=len(compacted),
        )


class RepeatedToolPruningCompactor(BaseCompactor):
    """OpenCode: Identify repeated tool calls, keep only most recent output."""

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        # Group by tool name + arguments
        tool_groups: Dict[str, List[Tuple[int, Dict]]] = {}
        
        for i, entry in enumerate(context):
            if entry.get("type") == "tool_call":
                tool_name = entry.get("tool", "")
                args = entry.get("arguments", {})
                key = f"{tool_name}:{json.dumps(args, sort_keys=True)}"
                if key not in tool_groups:
                    tool_groups[key] = []
                tool_groups[key].append((i, entry))
        
        # Find repeated calls
        to_hide = set()
        for key, calls in tool_groups.items():
            if len(calls) > 1:
                # Hide all but the most recent
                for idx, _ in calls[:-1]:
                    to_hide.add(idx)
        
        compacted = []
        offloaded = []
        
        for i, entry in enumerate(context):
            if i in to_hide:
                hidden_entry = copy.deepcopy(entry)
                hidden_entry["_hidden"] = True
                hidden_entry["_hidden_reason"] = "repeated_tool_pruning"
                offloaded.append(entry)
                compacted.append(hidden_entry)
            else:
                compacted.append(entry)
        
        return CompactionResult(
            compacted_context=compacted,
            offloaded_data=offloaded,
            strategy_used=CompactionStrategy.REPEATED_TOOL_PRUNING,
            tokens_saved=sum(len(json.dumps(e)) // 4 for e in offloaded),
            entries_compacted=len(offloaded),
            entries_preserved=len(compacted),
        )


class ErrorPreservationCompactor(BaseCompactor):
    """OpenCode: Prune errored tool call inputs after N turns, always preserve error messages."""

    def __init__(self, config: CompactionConfig):
        super().__init__(config)
        self.error_turns_to_keep = 3  # Keep error context for 3 turns

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        compacted = []
        offloaded = []
        recent_errors = []  # Track recent error indices
        
        for i, entry in enumerate(context):
            is_error = entry.get("type") == "tool_call" and entry.get("error") is not None
            
            if is_error:
                recent_errors.append(i)
                compacted.append(entry)  # Always preserve errors
            elif recent_errors and i - recent_errors[-1] <= self.error_turns_to_keep:
                # Keep context around recent errors
                compacted.append(entry)
            elif entry.get("type") == "tool_call" and "input" in entry:
                # Prune input for older tool calls
                compacted_entry = copy.deepcopy(entry)
                compacted_entry["input"] = "[pruned]"
                compacted_entry["_input_pruned"] = True
                offloaded.append(entry)
                compacted.append(compacted_entry)
            else:
                compacted.append(entry)
        
        return CompactionResult(
            compacted_context=compacted,
            offloaded_data=offloaded,
            strategy_used=CompactionStrategy.ERROR_PRESERVATION,
            tokens_saved=sum(len(json.dumps(e)) // 4 for e in offloaded),
            entries_compacted=len(offloaded),
            entries_preserved=len(compacted),
        )


# Factory

class Compactor:
    """Main compactor factory and facade."""

    STRATEGIES = {
        CompactionStrategy.TOKEN_BUDGET: TokenBudgetCompactor,
        CompactionStrategy.AGE_BASED: AgeBasedCompactor,
        CompactionStrategy.IMPORTANCE_BASED: ImportanceBasedCompactor,
        CompactionStrategy.HYBRID: HybridCompactor,
        CompactionStrategy.TIMESTAMP_HIDING: TimestampHidingCompactor,
        CompactionStrategy.HEAD_TAIL_PROTECTION: HeadTailProtectionCompactor,
        CompactionStrategy.REPEATED_TOOL_PRUNING: RepeatedToolPruningCompactor,
        CompactionStrategy.ERROR_PRESERVATION: ErrorPreservationCompactor,
    }

    def __init__(self, config: CompactionConfig):
        self.config = config
        self._compactor = self.STRATEGIES[config.strategy](config)

    @classmethod
    def from_config(cls, config_path: str) -> "Compactor":
        with open(config_path) as f:
            config_data = json.load(f)
        
        compaction_config = config_data.get("compaction", {})
        strategy_str = compaction_config.get("strategy", "hybrid")
        strategy = CompactionStrategy(strategy_str)
        
        config = CompactionConfig(
            strategy=strategy,
            keep_recent_full=compaction_config.get("keep_recent_full", 5),
            compact_ratio=compaction_config.get("compact_ratio", 0.5),
            preserve_structure=compaction_config.get("preserve_structure", True),
            protect_zones=compaction_config.get("protect_zones", ["head", "tail"]),
            max_tool_output_tokens=compaction_config.get("max_tool_output_tokens", 2000),
            importance_weights=compaction_config.get("importance_weights", {}),
        )
        return cls(config)

    def compact(self, context: List[Dict[str, Any]]) -> CompactionResult:
        return self._compactor.compact(context)

    def restore(self, compacted: List[Dict[str, Any]], offload_path: str) -> List[Dict[str, Any]]:
        return self._compactor.restore(compacted, offload_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Context Compaction CLI")
    parser.add_argument("--config", default=".agent_context_config.json")
    parser.add_argument("--input", required=True, help="Input context JSON file")
    parser.add_argument("--output", required=True, help="Output compacted context file")
    parser.add_argument("--offload", help="Offload data output file")
    parser.add_argument("--restore", action="store_true", help="Restore from compacted + offload")
    parser.add_argument("--offload-path", help="Offload file path for restore")
    args = parser.parse_args()

    compactor = Compactor.from_config(args.config)

    with open(args.input) as f:
        context = json.load(f)

    if args.restore:
        if not args.offload_path:
            parser.error("--offload-path required for restore")
        restored = compactor.restore(context, args.offload_path)
        with open(args.output, "w") as f:
            json.dump(restored, f, indent=2)
    else:
        result = compactor.compact(context)
        with open(args.output, "w") as f:
            json.dump(result.compacted_context, f, indent=2)
        if args.offload:
            with open(args.offload, "w") as f:
                json.dump(result.offloaded_data, f, indent=2)
        print(f"Compacted: {result.entries_preserved} entries preserved, {result.entries_compacted} offloaded")
        print(f"Tokens saved: ~{result.tokens_saved}")


if __name__ == "__main__":
    main()