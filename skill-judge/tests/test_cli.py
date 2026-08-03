"""Tests for the skill-judge CLI (python -m scripts.judge_skill ...)."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent

GOOD_SKILL_MD = """---
name: {name}
description: Use when writing robust production code, reviewing risky changes or explaining hard-won engineering decisions.
---

# My Craft
## When to use
Use when the stakes are high: writing critical code, reviewing a risky change or teaching a hard-won lesson.

## The mindset
Before you write code, ask yourself what the test must prove. Think about the trade-offs between speed and safety. The test: would this survive an adversarial review?

## Working
Step 1: reproduce the failure on a clean checkout.
Step 2: write the failing test first.
Step 3: implement the smallest change that passes.
Checkpoint each phase and record what you learned.

## Hard-won lessons
- Never ship a hotfix without a regression test, because the same bug will resurface.
- Do not trust a benchmark you did not run yourself; the hard way is the only way.
- Edge cases like empty input and boundary values decide production incidents.
- If a deploy fails at the verification step, roll back immediately rather than patching in place.
- When a test is flaky, treat it as a signal, not a nuisance.
- Only an expert knows when to break the checklist; learn the rules before bending them.
- Why is this trade-off acceptable? Because the alternative costs ten times more later.

## Decision tree
If the change touches a payment path, then run the full compliance suite.
If it touches only a utility, a focused unit test is enough.
Otherwise, run the middle tier.
When the reviewer disagrees, prefer the reviewer's position unless you can prove the edge case.

## Anti-patterns (NEVER list)
- NEVER pass silently on errors, because the failure cascades.
- NEVER overwrite a config file in place, because recovery becomes impossible.
- NEVER ignore a failing checkpoint.

## Error handling
If the build fails, capture the full log before retrying. On exception, preserve the original stack trace. Fallback to the previous release only when the new one cannot be repaired.

## Verification
- [ ] Tests written before implementation
- [ ] Trade-offs documented
- [ ] Edge cases covered
"""


def make_skill(tmp_path: Path, name: str = "my-craft") -> Path:
    skill_dir = tmp_path / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        GOOD_SKILL_MD.format(name=name), encoding="utf-8"
    )
    return skill_dir


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.judge_skill", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_evaluate_text_output(tmp_path):
    skill = make_skill(tmp_path)
    proc = run_cli("evaluate", "--skill", str(skill))
    assert proc.returncode == 0
    assert "Total:" in proc.stdout
    assert "Grade:" in proc.stdout
    assert "Quality gate:" in proc.stdout
    assert "Dimensions:" in proc.stdout


def test_evaluate_json_output(tmp_path):
    skill = make_skill(tmp_path)
    proc = run_cli("evaluate", "--skill", str(skill), "--format", "json")
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert "total" in data
    assert data["skill_name"] == "my-craft"
    assert "D1" in data["dimensions"]


def test_evaluate_output_writes_file(tmp_path):
    skill = make_skill(tmp_path)
    out = tmp_path / "report.json"
    proc = run_cli("evaluate", "--skill", str(skill), "--format", "json", "--output", str(out))
    assert proc.returncode == 0
    assert out.exists()
    assert "Report written to" in proc.stdout
    assert json.loads(out.read_text(encoding="utf-8"))["total"] >= 0


def test_evaluate_html_output(tmp_path):
    skill = make_skill(tmp_path)
    proc = run_cli("evaluate", "--skill", str(skill), "--format", "html")
    assert proc.returncode == 0
    assert "<html" in proc.stdout


def test_evaluate_missing_skill_fails(tmp_path):
    proc = run_cli("evaluate", "--skill", str(tmp_path / "nope"))
    assert proc.returncode == 1
    assert "ERROR" in proc.stdout


def test_shorthand_skill_flag(tmp_path):
    skill = make_skill(tmp_path)
    proc = run_cli("--skill", str(skill))
    assert proc.returncode == 0
    assert "Total:" in proc.stdout


def test_batch(tmp_path):
    make_skill(tmp_path, name="alpha")
    make_skill(tmp_path, name="beta")
    proc = run_cli("batch", "--skills-dir", str(tmp_path))
    assert proc.returncode == 0
    assert "alpha" in proc.stdout
    assert "beta" in proc.stdout
    assert "skill(s) evaluated" in proc.stdout


def test_compare(tmp_path):
    a = make_skill(tmp_path, name="alpha")
    b = make_skill(tmp_path, name="beta")
    proc = run_cli("compare", "--skill-a", str(a), "--skill-b", str(b))
    assert proc.returncode == 0
    assert "Winner:" in proc.stdout
    assert "D1" in proc.stdout


def test_calibrate_passes(tmp_path):
    skill = make_skill(tmp_path)
    bench = tmp_path / "bench"
    bench.mkdir()
    (bench / "cfg.json").write_text(
        json.dumps(
            {
                "name": "t",
                "skills_dir": str(skill.parent),
                "expectations": [{"skill": "my-craft", "band": "expert"}],
            }
        ),
        encoding="utf-8",
    )
    proc = run_cli("calibrate", "--benchmarks-dir", str(bench))
    assert proc.returncode == 0
    assert "passed 1, failed 0" in proc.stdout


def test_calibrate_fails_on_band_mismatch(tmp_path):
    skill = make_skill(tmp_path)
    bench = tmp_path / "bench"
    bench.mkdir()
    (bench / "cfg.json").write_text(
        json.dumps(
            {
                "name": "t",
                "skills_dir": str(skill.parent),
                "expectations": [{"skill": "my-craft", "band": "insufficient"}],
            }
        ),
        encoding="utf-8",
    )
    proc = run_cli("calibrate", "--benchmarks-dir", str(bench))
    assert proc.returncode == 1
    assert "passed 0, failed 1" in proc.stdout


def test_certify_strong(tmp_path):
    skill = make_skill(tmp_path)
    proc = run_cli("certify", "--skill", str(skill), "--level", "strong")
    assert proc.returncode == 0
    assert "CERTIFIED" in proc.stdout


def test_history_and_trend(tmp_path):
    skill = make_skill(tmp_path)
    history = tmp_path / "history.jsonl"
    first = run_cli("evaluate", "--skill", str(skill), "--history", str(history))
    assert first.returncode == 0
    second = run_cli(
        "evaluate", "--skill", str(skill), "--history", str(history), "--format", "json"
    )
    assert second.returncode == 0
    proc = run_cli("history", "--skill", "my-craft", "--show-trend", "--history", str(history))
    assert proc.returncode == 0
    assert "my-craft" in proc.stdout
    assert "evaluation(s)" in proc.stdout
    assert "range" in proc.stdout


def test_history_empty(tmp_path):
    proc = run_cli("history", "--skill", "nope", "--history", str(tmp_path / "h.jsonl"))
    assert proc.returncode == 1
    assert "No history" in proc.stdout


def test_unknown_command_fails():
    proc = run_cli("frobnicate")
    assert proc.returncode == 1
    assert "ERROR" in proc.stdout


def test_no_args_prints_help():
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.judge_skill"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert proc.returncode == 1
    assert "Commands:" in proc.stdout


def test_unit_quality_gate_and_bands():
    from scripts.judge_skill import _band_for_total, quality_gate

    assert quality_gate({"total": 80, "dimensions": {"D1": {"score": 14}}}) == (True, [])
    gate, reasons = quality_gate({"total": 60, "dimensions": {"D1": {"score": 14}}})
    assert gate is False and len(reasons) > 0
    gate, reasons = quality_gate({"total": 80, "dimensions": {"D1": {"score": 8}}})
    assert gate is False and any("D1" in r for r in reasons)
    assert _band_for_total(95) == "expert"
    assert _band_for_total(85) == "strong"
    assert _band_for_total(75) == "adequate"
    assert _band_for_total(65) == "needs_work"
    assert _band_for_total(55) == "insufficient"


def test_unit_dimensions_total_120():
    from scripts.judge_skill import TOTAL_MAX

    assert TOTAL_MAX == 120
