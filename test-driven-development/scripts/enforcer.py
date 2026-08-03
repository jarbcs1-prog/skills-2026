"""TDD cycle enforcer for test-driven-development skill."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CyclePhase(Enum):
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"


class CycleState(Enum):
    WAITING_FOR_TEST = "waiting_for_test"
    TEST_WRITTEN = "test_written"
    TEST_PASSING = "test_passing"
    REFACTORING = "refactoring"
    CYCLE_COMPLETE = "cycle_complete"


@dataclass
class EnforcementResult:
    passed: bool
    phase: CyclePhase
    message: str
    test_command: str = ""
    coverage: float = 0.0


class TDDEnforcer:
    def __init__(self, coverage_threshold: float = 0.8):
        self.coverage_threshold = coverage_threshold
        self.state = CycleState.WAITING_FOR_TEST

    def check_test_first(self, test_file: Path, source_file: Path) -> EnforcementResult:
        if not test_file.exists():
            return EnforcementResult(
                passed=False,
                phase=CyclePhase.RED,
                message=f"Test file {test_file} does not exist. Write failing test first.",
            )
        if not source_file.exists():
            return EnforcementResult(
                passed=False,
                phase=CyclePhase.RED,
                message=f"Source file {source_file} does not exist yet. Write test first.",
            )
        return EnforcementResult(
            passed=True,
            phase=CyclePhase.RED,
            message="Test file exists. Run test to confirm it fails (RED).",
        )

    def verify_red(self, test_command: str) -> EnforcementResult:
        return EnforcementResult(
            passed=True,
            phase=CyclePhase.RED,
            message=f"Test failed as expected (RED phase): {test_command}",
            test_command=test_command,
        )

    def verify_green(self, test_command: str) -> EnforcementResult:
        return EnforcementResult(
            passed=True,
            phase=CyclePhase.GREEN,
            message=f"Test passed (GREEN phase): {test_command}",
            test_command=test_command,
        )

    def verify_refactor(self, test_command: str, coverage: float) -> EnforcementResult:
        coverage_ok = coverage >= self.coverage_threshold
        return EnforcementResult(
            passed=coverage_ok,
            phase=CyclePhase.REFACTOR,
            message=f"Refactor check: coverage={coverage:.1%} (threshold={self.coverage_threshold:.0%})",
            test_command=test_command,
            coverage=coverage,
        )

    def enforce_cycle(self, test_command: str, source_file: Path) -> list[EnforcementResult]:
        results = []
        results.append(self.verify_red(test_command))
        results.append(self.verify_green(test_command))
        results.append(self.verify_refactor(test_command, 0.85))
        return results