from typing import Dict, Any

class ContextMonitor:
    def __init__(self, hard_limit: int, pre_rot_threshold: int, compaction_trigger: int, summarization_trigger: int):
        self.hard_limit = hard_limit
        self.pre_rot_threshold = pre_rot_threshold
        self.compaction_trigger = compaction_trigger
        self.summarization_trigger = summarization_trigger

    def check_context(self, context_tokens: int) -> Dict[str, Any]:
        action = "none"
        if context_tokens >= self.hard_limit:
            action = "critical"
        elif context_tokens >= self.summarization_trigger:
            action = "summarize"
        elif context_tokens >= self.compaction_trigger:
            action = "compact"

        percent = (context_tokens / self.hard_limit) * 100
        return {"action": action, "tokens": context_tokens, "percent": percent}

    def get_metrics(self) -> Dict[str, int]:
        return {
            "hard_limit": self.hard_limit,
            "pre_rot_threshold": self.pre_rot_threshold,
            "compaction_trigger": self.compaction_trigger,
            "summarization_trigger": self.summarization_trigger,
        }

    @classmethod
    def from_config(cls, config_path: str):
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        thresholds = config.get("thresholds", {})
        return cls(
            hard_limit=thresholds.get("hard_limit"),
            pre_rot_threshold=thresholds.get("pre_rot_threshold"),
            compaction_trigger=thresholds.get("compaction_trigger"),
            summarization_trigger=thresholds.get("summarization_trigger"),
        )
