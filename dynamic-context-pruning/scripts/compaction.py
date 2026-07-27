from typing import List, Dict, Any

class Compactor:
    def __init__(self, keep_recent_full: int, compact_ratio: float, preserve_structure: bool):
        self.keep_recent_full = keep_recent_full
        self.compact_ratio = compact_ratio
        self.preserve_structure = preserve_structure

    def compact(self, context_history: List[Dict[str, Any]]) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
        if len(context_history) <= self.keep_recent_full:
            return context_history, []

        recent_context = context_history[-self.keep_recent_full:]
        old_context = context_history[:-self.keep_recent_full]

        # Simulate compaction: for simplicity, we'll just take a ratio of the old context
        # In a real scenario, this would involve more sophisticated logic (e.g. summarizing, removing less important items)
        compacted_old_context_len = int(len(old_context) * (1 - self.compact_ratio))
        compacted_old_context = old_context[:compacted_old_context_len]
        offloaded_data = old_context[compacted_old_context_len:]

        return compacted_old_context + recent_context, offloaded_data

    def restore(self, compacted_context: List[Dict[str, Any]], offloaded_file_path: str) -> List[Dict[str, Any]]:
        # In a real scenario, this would involve reading from the offloaded_file_path
        # and merging it back with the compacted_context.
        # For this mock, we'll just return the compacted context as is.
        return compacted_context

    @classmethod
    def from_config(cls, config_path: str):
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        compaction_config = config.get("compaction", {})
        return cls(
            keep_recent_full=compaction_config.get("keep_recent_full"),
            compact_ratio=compaction_config.get("compact_ratio"),
            preserve_structure=compaction_config.get("preserve_structure"),
        )
