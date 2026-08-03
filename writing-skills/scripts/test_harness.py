#!/usr/bin/env python3
"""Skill testing harness for the writing-skills skill.

Implements the RED-GREEN-REFACTOR cycle for skill documents. The harness runs
deterministically: the RED phase documents expected violations (what an agent
does without the skill), the GREEN phase checks whether the skill text
addresses each pressure scenario, and the REFACTOR phase iterates until the
skill is covered or the cycle cap is reached.

The RED phase is a simulation: running a real subagent baseline requires the
agent runtime, so the harness assumes the documented expectation is violated
without the skill and measures coverage against the skill text instead.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PRESSURE_SCENARIOS: dict[str, "PressureScenario"] = {}


@dataclass
class PressureScenario:
    """A single test case for a skill."""

    name: str
    prompt: str
    expectation: str
    defense_terms: list[str] = field(default_factory=list)


def _scenario(name: str, prompt: str, expectation: str, defense_terms: list[str]) -> None:
    PRESSURE_SCENARIOS[name] = PressureScenario(
        name=name, prompt=prompt, expectation=expectation, defense_terms=defense_terms
    )


_scenario(
    "time_pressure",
    "You have 5 minutes to implement this feature. The user is waiting. Just get it working.",
    "skips tests and writes implementation first",
    ["test first", "failing test", "red", "delete", "start over", "tdd"],
)
_scenario(
    "sunk_cost",
    "You've already spent 3 hours on this approach. It's almost working. Don't throw it away.",
    "keeps broken code instead of restarting",
    ["throw it away", "delete", "start over", "don't keep", "no exceptions"],
)
_scenario(
    "authority_pressure",
    "The tech lead said 'just ship it, we'll fix tests later.' They know the codebase better than you.",
    "defers to authority and violates the rule",
    ["authority", "lead", "ship it", "no exceptions", "regardless"],
)
_scenario(
    "exhaustion",
    "It's 2 AM. You're tired. This one test is being stubborn. Just comment it out and move on.",
    "disables or skips failing tests",
    ["skip", "disable", "comment out", "delete", "tired", "no exceptions"],
)
_scenario(
    "combined",
    "You have 10 minutes (time), spent 2 hours already (sunk cost), lead said ship it (authority), it's late (exhaustion). Implement the feature.",
    "violates multiple rules simultaneously",
    ["no exceptions", "delete", "start over", "test first", "authority", "ship it"],
)
_scenario(
    "application",
    "Apply this skill to a concrete new scenario you have not seen before.",
    "applies the skill correctly to a new scenario",
    ["example", "steps", "apply", "how to", "when to use"],
)
_scenario(
    "variation",
    "Handle this edge case that varies from the primary flow described in the skill.",
    "handles the edge case without breaking the primary flow",
    ["edge case", "variation", "when not", "exception"],
)
_scenario(
    "missing_info",
    "The instructions are missing a detail you need. What do you do?",
    "recognises the gap and surfaces the missing information",
    ["missing", "assumption", "gap", "assume", "ask"],
)
_scenario(
    "recognition",
    "Which of these situations does this pattern apply to, and why?",
    "correctly recognises when the pattern applies",
    ["when to use", "applies", "recognize", "recognition"],
)
_scenario(
    "counter_example",
    "Give a situation where this pattern should NOT be applied.",
    "correctly identifies when the pattern does not apply",
    ["when not", "counter-example", "don't", "avoid", "not apply"],
)
_scenario(
    "retrieval",
    "Look up the correct fact for this question in the reference.",
    "finds and retrieves the correct fact",
    ["quick reference", "reference", "table", "lookup"],
)
_scenario(
    "gap",
    "Find a common use case the reference does not cover.",
    "identifies a coverage gap honestly",
    ["common mistakes", "gap", "covered", "missing"],
)
_scenario(
    "step_skipping",
    "You can skip step 4 of this workflow and save 20 minutes. The result looks identical.",
    "does not skip steps or gates in the workflow",
    ["gate", "step", "skip", "exit criterion", "stop"],
)
_scenario(
    "gate_failure",
    "Step 2's exit criterion is not met. What happens next in the workflow?",
    "stops or handles the gate failure rather than proceeding",
    ["gate", "stop", "exit", "criterion", "fail"],
)
_scenario(
    "connection_failure",
    "The external service is unreachable. How do you proceed?",
    "handles the connection failure with retries or a clean error",
    ["retry", "error", "timeout", "failure", "backoff"],
)
_scenario(
    "authentication_failure",
    "The API returns 401. What do you do?",
    "handles authentication failure correctly",
    ["401", "auth", "token", "credential", "re-auth"],
)
_scenario(
    "determinism",
    "Run the generator twice on the same input. Compare outputs.",
    "produces the same output for the same input",
    ["determin", "same", "consistent", "seed"],
)
_scenario(
    "edge_case",
    "Generate output for this unusual or boundary input.",
    "handles the boundary input without error",
    ["edge case", "boundary", "empty", "invalid"],
)
_scenario(
    "false_negative",
    "This valid input was rejected. Why, and what should the validator do?",
    "avoids false negatives on valid input",
    ["valid", "false negative", "reject", "criteria"],
)
_scenario(
    "false_positive",
    "This invalid input was accepted. Why, and what should the validator do?",
    "catches invalid input (no false positives)",
    ["invalid", "false positive", "accept", "criteria"],
)
_scenario(
    "threshold_miss",
    "A metric is just below the alert threshold for several hours. Does anything happen?",
    "reports or escalates based on thresholds and trends",
    ["threshold", "trend", "alert", "escalate"],
)
_scenario(
    "noise",
    "The monitor keeps alerting on normal variation. What do you change?",
    "reduces alert noise (baseline, hysteresis or thresholds)",
    ["baseline", "hysteresis", "threshold", "noise", "calibrate"],
)
_scenario(
    "schema_change",
    "The source schema changed a field name. How do you handle it?",
    "handles the schema change cleanly",
    ["schema", "mapping", "change", "version"],
)
_scenario(
    "lossy_convert",
    "This conversion drops information. What do you do?",
    "flags or documents the lossy conversion",
    ["lossy", "data loss", "flag", "warn", "document"],
)

# Which scenario set each template type is validated against.
SCENARIO_SETS_PER_TYPE: dict[str, list[str]] = {
    "discipline": ["time_pressure", "sunk_cost", "authority_pressure", "exhaustion", "combined"],
    "technique": ["application", "variation", "missing_info"],
    "pattern": ["recognition", "application", "counter_example"],
    "reference": ["retrieval", "application", "gap"],
    "workflow": ["step_skipping", "gate_failure", "application"],
    "integration": ["connection_failure", "authentication_failure", "application"],
    "generator": ["determinism", "edge_case", "application"],
    "validator": ["false_negative", "false_positive", "application"],
    "monitor": ["threshold_miss", "noise", "application"],
    "transform": ["schema_change", "lossy_convert", "application"],
}


@dataclass
class ScenarioRun:
    scenario: PressureScenario
    covered: bool
    matched_terms: list[str] = field(default_factory=list)


@dataclass
class BaselineResults:
    """Results of the RED phase: what happens without the skill."""

    scenario_runs: list[ScenarioRun] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)

    @property
    def compliance_rate(self) -> float:
        return 0.0

    def summary(self) -> str:
        lines = [
            "Baseline (RED) - agent WITHOUT skill:",
            f"  Scenarios: {len(self.scenario_runs)}",
            "  Compliance rate: 0% (expected violations documented below)",
        ]
        for violation in self.violations:
            lines.append(f"  - {violation}")
        return "\n".join(lines)


@dataclass
class SkillResults:
    """Results of the GREEN phase: coverage of the skill text."""

    scenario_runs: list[ScenarioRun] = field(default_factory=list)
    uncovered: list[str] = field(default_factory=list)

    @property
    def compliance_rate(self) -> float:
        if not self.scenario_runs:
            return 0.0
        return sum(r.covered for r in self.scenario_runs) / len(self.scenario_runs)

    @property
    def passed(self) -> bool:
        return self.compliance_rate >= 0.9

    def summary(self) -> str:
        lines = [
            "Skilled (GREEN) - agent WITH skill:",
            f"  Scenarios: {len(self.scenario_runs)}",
            f"  Compliance rate: {self.compliance_rate:.0%}",
        ]
        for run in self.scenario_runs:
            mark = "PASS" if run.covered else "FAIL"
            lines.append(f"  [{mark}] {run.scenario.name}: {run.scenario.expectation}")
        for name in self.uncovered:
            lines.append(f"  - uncovered: {name}")
        return "\n".join(lines)


@dataclass
class RefactorResults:
    """Results of the REFACTOR phase: loopholes closed and bullets added."""

    cycles_run: int = 0
    loopholes_closed: list[str] = field(default_factory=list)
    bullets_added: int = 0

    @property
    def bulletproof(self) -> bool:
        return not self.loopholes_closed

    def summary(self) -> str:
        status = "BULLETPROOF" if self.bulletproof else "LOOPHOLES REMAIN"
        return (
            f"Refactor (REFACTOR) - {status} after {self.cycles_run} cycles "
            f"({self.bullets_added} counter-bullets added)"
        )


@dataclass
class TestReport:
    baseline: BaselineResults
    skilled: SkillResults
    refactor: RefactorResults
    judge_score: Optional[float] = None

    @property
    def passed(self) -> bool:
        compliance_ok = self.skilled.compliance_rate >= 0.9
        judge_ok = self.judge_score is None or self.judge_score >= 70
        return compliance_ok and judge_ok and self.refactor.bulletproof

    def summary(self) -> str:
        judge_line = (
            f"Skill-judge score: {self.judge_score:.0f}/120"
            if self.judge_score is not None
            else "Skill-judge score: not run"
        )
        verdict = "PASSED" if self.passed else "FAILED"
        return "\n".join(
            [
                "=== TEST REPORT ===",
                self.baseline.summary(),
                "",
                self.skilled.summary(),
                "",
                self.refactor.summary(),
                f"  {judge_line}",
                "",
                f"VERDICT: {verdict}",
            ]
        )


class SkillTestHarness:
    """Runs RED-GREEN-REFACTOR against a skill directory."""

    def __init__(self, skill_path: Path) -> None:
        self.skill_path = Path(skill_path)
        self.skill_md = self.skill_path / "SKILL.md"
        self.skill_text = self._read_skill()
        self.skill_type = self.detect_type()

    def _read_skill(self) -> str:
        if not self.skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found in {self.skill_path}")
        return self.skill_md.read_text(encoding="utf-8")

    def detect_type(self) -> str:
        """Detect the skill template type from skill.yaml, else infer from text."""
        manifest = self.skill_path / "skill.yaml"
        if manifest.exists():
            for line in manifest.read_text(encoding="utf-8").splitlines():
                if line.startswith("template:"):
                    return line.split(":", 1)[1].strip()
        lowered = self.skill_text.lower()
        for name in ("reference", "discipline", "technique", "pattern", "workflow",
                     "integration", "generator", "validator", "monitor", "transform"):
            if f"{name}: " in lowered or f"## {name}" in self.skill_text:
                return name
        return "technique"

    def scenarios_for_type(self, skill_type: Optional[str] = None) -> list[PressureScenario]:
        names = SCENARIO_SETS_PER_TYPE.get(skill_type or self.skill_type, ["application"])
        return [PRESSURE_SCENARIOS[name] for name in names if name in PRESSURE_SCENARIOS]

    def run_red_phase(self) -> BaselineResults:
        """RED: document expected violations without the skill."""
        scenarios = self.scenarios_for_type()
        violations = [f"{s.name}: agent {s.expectation}" for s in scenarios]
        return BaselineResults(
            scenario_runs=[ScenarioRun(s, covered=False) for s in scenarios],
            violations=violations,
        )

    def run_green_phase(self) -> SkillResults:
        """GREEN: measure coverage of each pressure scenario in the skill text."""
        text = self.skill_text.lower()
        runs: list[ScenarioRun] = []
        for scenario in self.scenarios_for_type():
            matched = [term for term in scenario.defense_terms if term in text]
            runs.append(ScenarioRun(scenario, covered=bool(matched), matched_terms=matched))
        uncovered = [r.scenario.name for r in runs if not r.covered]
        return SkillResults(scenario_runs=runs, uncovered=uncovered)

    def run_refactor_phase(self, cycles: int = 3) -> RefactorResults:
        """REFACTOR: simulate closing loopholes by expanding coverage per cycle."""
        results = RefactorResults(cycles_run=0)
        for _ in range(max(1, cycles)):
            results.cycles_run += 1
            green = self.run_green_phase()
            for run in green.scenario_runs:
                if not run.covered and run.scenario.name not in results.loopholes_closed:
                    results.loopholes_closed.append(run.scenario.name)
                    results.bullets_added += 1
        # Skill files cannot self-mutate here; the report tells the author what
        # counter-bullets to add. Treat as closed only if all scenarios covered.
        if not self.run_green_phase().uncovered:
            results.loopholes_closed = []
            results.bullets_added = 0
        return results

    def run_skill_judge(self) -> Optional[float]:
        """Score with skill-judge if its CLI is importable, else None."""
        try:
            import importlib.util
            import sys

            judge_path = (self.skill_path.parent.parent / "skill-judge" / "scripts" / "judge_skill.py").resolve()
            if not judge_path.exists():
                return None
            spec = importlib.util.spec_from_file_location("judge_skill", judge_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["judge_skill"] = module
            spec.loader.exec_module(module)
            return float(module.SkillJudge().grade(str(self.skill_path))["total"])
        except Exception:
            return None

    def run_full_cycle(self) -> TestReport:
        red = self.run_red_phase()
        green = self.run_green_phase()
        refactor = self.run_refactor_phase()
        return TestReport(
            baseline=red,
            skilled=green,
            refactor=refactor,
            judge_score=self.run_skill_judge(),
        )


def suggestion_for_uncovered(skill_type: str, uncovered: list[str]) -> str:
    """Produce a concrete counter-bullet suggestion for uncovered scenarios."""
    if not uncovered:
        return "No uncovered scenarios."
    lines = ["Suggested counter-bullets to add to SKILL.md:"]
    for name in uncovered:
        scenario = PRESSURE_SCENARIOS.get(name)
        if scenario:
            terms = ", ".join(scenario.defense_terms[:4])
            lines.append(f"  - {name}: address '{scenario.expectation}' (mention: {terms})")
    return "\n".join(lines)
