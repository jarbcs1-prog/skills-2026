"""
Context Monitor — Threshold monitoring & alerts for dynamic context pruning.
"""

import json
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ContextAction(Enum):
    NONE = "none"
    COMPACT = "compact"
    SUMMARIZE = "summarize"
    CRITICAL = "critical"


@dataclass
class ContextThresholds:
    hard_limit: int = 256_000
    pre_rot_threshold: int = 100_000
    compaction_trigger: int = 150_000
    summarization_trigger: int = 175_000


@dataclass
class ContextStatus:
    action: ContextAction
    tokens: int
    percent: float
    message: str


@dataclass
class ContextMetrics:
    tokens_used: int
    percent: float
    trend: str  # "increasing", "stable", "decreasing"
    predicted_exhaustion: Optional[int]  # tokens until hard limit
    time_to_compaction: Optional[int]  # tokens until compaction trigger
    time_to_summarization: Optional[int]  # tokens until summarization trigger
    history: list  # recent token counts


class ContextMonitor:
    """Monitors context length against configured thresholds."""

    def __init__(
        self,
        hard_limit: int = 256_000,
        pre_rot_threshold: int = 100_000,
        compaction_trigger: int = 150_000,
        summarization_trigger: int = 175_000,
    ):
        self.thresholds = ContextThresholds(
            hard_limit=hard_limit,
            pre_rot_threshold=pre_rot_threshold,
            compaction_trigger=compaction_trigger,
            summarization_trigger=summarization_trigger,
        )
        self._history = []

    @classmethod
    def from_config(cls, config_path: str) -> "ContextMonitor":
        """Create monitor from .agent_context_config.json"""
        with open(config_path) as f:
            config = json.load(f)
        t = config.get("thresholds", {})
        return cls(
            hard_limit=t.get("hard_limit", 256_000),
            pre_rot_threshold=t.get("pre_rot_threshold", 100_000),
            compaction_trigger=t.get("compaction_trigger", 150_000),
            summarization_trigger=t.get("summarization_trigger", 175_000),
        )

    def check_context(self, context_tokens: int) -> ContextStatus:
        """Check current context health against thresholds."""
        self._history.append(context_tokens)
        if len(self._history) > 100:
            self._history = self._history[-100:]

        percent = (context_tokens / self.thresholds.hard_limit) * 100

        if context_tokens >= self.thresholds.hard_limit:
            return ContextStatus(
                action=ContextAction.CRITICAL,
                tokens=context_tokens,
                percent=percent,
                message=f"CRITICAL: Exceeded hard limit ({self.thresholds.hard_limit})",
            )
        elif context_tokens >= self.thresholds.summarization_trigger:
            return ContextStatus(
                action=ContextAction.SUMMARIZE,
                tokens=context_tokens,
                percent=percent,
                message=f"Summarization trigger reached ({self.thresholds.summarization_trigger})",
            )
        elif context_tokens >= self.thresholds.compaction_trigger:
            return ContextStatus(
                action=ContextAction.COMPACT,
                tokens=context_tokens,
                percent=percent,
                message=f"Compaction trigger reached ({self.thresholds.compaction_trigger})",
            )
        elif context_tokens >= self.thresholds.pre_rot_threshold:
            return ContextStatus(
                action=ContextAction.NONE,
                tokens=context_tokens,
                percent=percent,
                message=f"Pre-rot threshold reached ({self.thresholds.pre_rot_threshold}) — attention degradation begins",
            )
        else:
            return ContextStatus(
                action=ContextAction.NONE,
                tokens=context_tokens,
                percent=percent,
                message="Context healthy",
            )

    def get_metrics(self) -> ContextMetrics:
        """Get detailed context metrics."""
        if not self._history:
            return ContextMetrics(
                tokens_used=0,
                percent=0.0,
                trend="stable",
                predicted_exhaustion=None,
                time_to_compaction=None,
                time_to_summarization=None,
                history=[],
            )

        current = self._history[-1]
        percent = (current / self.thresholds.hard_limit) * 100

        # Calculate trend
        if len(self._history) >= 3:
            recent = self._history[-3:]
            if recent[-1] > recent[0]:
                trend = "increasing"
            elif recent[-1] < recent[0]:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # Predictions
        avg_growth = 0
        if len(self._history) >= 2:
            diffs = [self._history[i] - self._history[i-1] for i in range(1, len(self._history))]
            avg_growth = sum(diffs) / len(diffs)

        predicted_exhaustion = None
        time_to_compaction = None
        time_to_summarization = None

        if avg_growth > 0:
            predicted_exhaustion = max(0, (self.thresholds.hard_limit - current) // avg_growth)
            time_to_compaction = max(0, (self.thresholds.compaction_trigger - current) // avg_growth)
            time_to_summarization = max(0, (self.thresholds.summarization_trigger - current) // avg_growth)

        return ContextMetrics(
            tokens_used=current,
            percent=percent,
            trend=trend,
            predicted_exhaustion=predicted_exhaustion,
            time_to_compaction=time_to_compaction,
            time_to_summarization=time_to_summarization,
            history=self._history[-20:],  # last 20 readings
        )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Context Monitor CLI")
    parser.add_argument("--config", default=".agent_context_config.json", help="Config file path")
    parser.add_argument("--tokens", type=int, help="Current token count to check")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--metrics", action="store_true", help="Show detailed metrics")
    args = parser.parse_args()

    monitor = ContextMonitor.from_config(args.config)

    if args.tokens is not None:
        status = monitor.check_context(args.tokens)
        print(f"Action: {status.action.value}")
        print(f"Tokens: {status.tokens}")
        print(f"Percent: {status.percent:.1f}%")
        print(f"Message: {status.message}")

    if args.metrics:
        metrics = monitor.get_metrics()
        print(json.dumps(metrics.__dict__, indent=2, default=str))


if __name__ == "__main__":
    main()