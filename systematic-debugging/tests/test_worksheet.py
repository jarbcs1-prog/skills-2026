"""Tests for systematic-debugging worksheet generator."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.worksheet import (
    DebugSession, ErrorAnalysis, Reproduction, EvidenceRow, Hypothesis,
    WorksheetGenerator,
)


def test_worksheet_generator_creates_output():
    session = DebugSession()
    session.error_analysis = ErrorAnalysis(
        error_message="TypeError: NoneType",
        stack_trace="Traceback...",
        error_code="E100",
        file_line="main.py:10",
    )
    session.reproduction = Reproduction(
        steps=["Run pytest", "See error"],
        consistency="Always",
        environment="Python 3.12",
        test_command="pytest test_x.py",
    )
    session.evidence = [
        EvidenceRow(component="api", input_val="req", output_val="resp",
                     expected="200", actual="500", status="Failed"),
    ]
    session.hypotheses = [
        Hypothesis(number=1, description="Null return from API",
                    test="Mock API response", result="Confirmed", next_step="Fix"),
    ]

    gen = WorksheetGenerator(session)
    output = gen.generate()
    assert "TypeError" in output
    assert "Phase 1" in output
    assert "Rule of Three" in output


def test_worksheet_generator_saves_to_file(tmp_path):
    session = DebugSession()
    session.error_analysis = ErrorAnalysis(error_message="test error")
    session.reproduction = Reproduction(steps=["step 1"])

    gen = WorksheetGenerator(session)
    out_file = tmp_path / "worksheet.md"
    gen.save(str(out_file))
    assert out_file.exists()
    content = out_file.read_text()
    assert "test error" in content