"""Debugging analytics for systematic-debugging skill."""
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict


@dataclass
class DebugSession:
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    error_category: str = ""
    hypotheses_tested: int = 0
    fixes_attempted: int = 0
    first_fix_success: bool = False
    pattern_matched: Optional[str] = None
    new_bugs_introduced: int = 0
    time_to_root_cause_minutes: float = 0.0


@dataclass
class EffectivenessReport:
    avg_time_to_root_cause: float
    first_fix_success_rate: float
    rule_of_three_trigger_rate: float
    pattern_match_rate: float
    regression_rate: float
    total_sessions: int


@dataclass
class PatternStats:
    pattern_name: str
    occurrence_count: int
    avg_resolution_time: float
    success_rate: float


class DebuggingAnalytics:
    def __init__(self):
        self.sessions: List[DebugSession] = []

    def record_session(self, session: DebugSession) -> None:
        self.sessions.append(session)

    def get_effectiveness(self) -> EffectivenessReport:
        if not self.sessions:
            return EffectivenessReport(
                avg_time_to_root_cause=0.0,
                first_fix_success_rate=0.0,
                rule_of_three_trigger_rate=0.0,
                pattern_match_rate=0.0,
                regression_rate=0.0,
                total_sessions=0,
            )

        total = len(self.sessions)
        avg_time = sum(s.time_to_root_cause_minutes for s in self.sessions) / total
        first_fix = sum(1 for s in self.sessions if s.first_fix_success) / total
        rule_of_three = sum(1 for s in self.sessions if s.hypotheses_tested >= 3) / total
        pattern_matched = sum(1 for s in self.sessions if s.pattern_matched) / total
        regressions = sum(s.new_bugs_introduced for s in self.sessions) / total

        return EffectivenessReport(
            avg_time_to_root_cause=round(avg_time, 2),
            first_fix_success_rate=round(first_fix, 2),
            rule_of_three_trigger_rate=round(rule_of_three, 2),
            pattern_match_rate=round(pattern_matched, 2),
            regression_rate=round(regressions, 2),
            total_sessions=total,
        )

    def get_pattern_effectiveness(self) -> Dict[str, PatternStats]:
        pattern_sessions: Dict[str, List[DebugSession]] = defaultdict(list)
        for session in self.sessions:
            if session.pattern_matched:
                pattern_sessions[session.pattern_matched].append(session)

        result = {}
        for pattern_name, sessions in pattern_sessions.items():
            count = len(sessions)
            avg_time = sum(s.time_to_root_cause_minutes for s in sessions) / count
            success = sum(1 for s in sessions if s.first_fix_success) / count
            result[pattern_name] = PatternStats(
                pattern_name=pattern_name,
                occurrence_count=count,
                avg_resolution_time=round(avg_time, 2),
                success_rate=round(success, 2),
            )
        return result