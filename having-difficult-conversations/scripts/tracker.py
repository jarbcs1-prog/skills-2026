"""Conversation outcome tracker and analytics."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from collections import defaultdict


@dataclass
class ConversationLog:
    id: str
    type: str
    person: str
    date: datetime
    framework: str
    outcome: str
    followup_date: Optional[str] = None
    notes: str = ""
    resolution_score: float = 0.0
    relationship_impact: float = 0.0
    clarity_score: float = 0.0


@dataclass
class ConversationAnalytics:
    total_conversations: int
    resolution_rate: float
    relationship_impact: float
    clarity_score: float
    recurring_patterns: List[str]
    framework_effectiveness: Dict[str, float]
    by_type: Dict[str, int]
    by_person: Dict[str, int]
    monthly_trend: Dict[str, int]


class ConversationTracker:
    def __init__(self, history_file: str = ".conversation_history.json"):
        self.history_file = history_file
        self.entries: List[ConversationLog] = []

    def log(self, conversation: ConversationLog) -> None:
        self.entries.append(conversation)

    def get_analytics(self, period_months: int = 3) -> ConversationAnalytics:
        if not self.entries:
            return ConversationAnalytics(
                total_conversations=0,
                resolution_rate=0.0,
                relationship_impact=0.0,
                clarity_score=0.0,
                recurring_patterns=[],
                framework_effectiveness={},
                by_type={},
                by_person={},
                monthly_trend={},
            )

        total = len(self.entries)
        resolved = sum(1 for e in self.entries if e.outcome == "resolved")
        resolution_rate = resolved / total if total > 0 else 0.0

        by_type = defaultdict(int)
        by_person = defaultdict(int)
        for entry in self.entries:
            by_type[entry.type] += 1
            by_person[entry.person] += 1

        framework_effectiveness = defaultdict(list)
        for entry in self.entries:
            framework_effectiveness[entry.framework].append(entry.resolution_score)

        avg_framework = {
            k: sum(v) / len(v) for k, v in framework_effectiveness.items() if v
        }

        return ConversationAnalytics(
            total_conversations=total,
            resolution_rate=resolution_rate,
            relationship_impact=sum(e.relationship_impact for e in self.entries) / total,
            clarity_score=sum(e.clarity_score for e in self.entries) / total,
            recurring_patterns=self._detect_patterns(),
            framework_effectiveness=avg_framework,
            by_type=dict(by_type),
            by_person=dict(by_person),
            monthly_trend=self._monthly_trend(),
        )

    def _detect_patterns(self) -> List[str]:
        patterns = []
        type_counts = defaultdict(int)
        for entry in self.entries:
            type_counts[entry.type] += 1
        for t, count in type_counts.items():
            if count > 2:
                patterns.append(f"Recurring {t} conversations ({count} occurrences)")
        return patterns

    def _monthly_trend(self) -> Dict[str, int]:
        trend = defaultdict(int)
        for entry in self.entries:
            month_key = entry.date.strftime("%Y-%m")
            trend[month_key] += 1
        return dict(trend)

    def get_history(self, person: Optional[str] = None,
                    last_n: int = 10) -> List[ConversationLog]:
        if person:
            filtered = [e for e in self.entries if e.person == person]
        else:
            filtered = self.entries
        return filtered[-last_n:]