"""Tests for TDD enforcer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.enforcer import TDDEnforcer, CyclePhase, CycleState


def test_enforcer_initializes():
    enforcer = TDDEnforcer()
    assert enforcer.state == CycleState.WAITING_FOR_TEST
    assert enforcer.coverage_threshold == 0.8


def test_enforcer_custom_threshold():
    enforcer = TDDEnforcer(coverage_threshold=0.9)
    assert enforcer.coverage_threshold == 0.9


def test_check_test_first_missing_test_file(tmp_path):
    enforcer = TDDEnforcer()
    source = tmp_path / "auth.py"
    source.write_text("")
    result = enforcer.check_test_first(tmp_path / "test_auth.py", source)
    assert not result.passed
    assert result.phase == CyclePhase.RED


def test_check_test_first_missing_source(tmp_path):
    enforcer = TDDEnforcer()
    test = tmp_path / "test_auth.py"
    test.write_text("")
    result = enforcer.check_test_first(test, tmp_path / "auth.py")
    assert not result.passed
    assert result.phase == CyclePhase.RED


def test_check_test_first_both_exist(tmp_path):
    enforcer = TDDEnforcer()
    test = tmp_path / "test_auth.py"
    test.write_text("")
    source = tmp_path / "auth.py"
    source.write_text("")
    result = enforcer.check_test_first(test, source)
    assert result.passed
    assert result.phase == CyclePhase.RED


def test_verify_red():
    enforcer = TDDEnforcer()
    result = enforcer.verify_red("pytest test_auth.py -v")
    assert result.passed
    assert result.phase == CyclePhase.RED


def test_verify_green():
    enforcer = TDDEnforcer()
    result = enforcer.verify_green("pytest test_auth.py -v")
    assert result.passed
    assert result.phase == CyclePhase.GREEN


def test_verify_refactor_passes():
    enforcer = TDDEnforcer()
    result = enforcer.verify_refactor("pytest", 0.85)
    assert result.passed
    assert result.phase == CyclePhase.REFACTOR


def test_verify_refactor_fails():
    enforcer = TDDEnforcer()
    result = enforcer.verify_refactor("pytest", 0.5)
    assert not result.passed
    assert result.coverage == 0.5


def test_enforce_cycle():
    enforcer = TDDEnforcer()
    results = enforcer.enforce_cycle("pytest test_auth.py", Path("src/auth.py"))
    assert len(results) == 3
    assert all(r.passed for r in results)