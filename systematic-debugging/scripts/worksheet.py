"""Debugging worksheet generator for systematic-debugging skill."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ErrorAnalysis:
    error_message: str = ""
    stack_trace: str = ""
    error_code: str = ""
    file_line: str = ""


@dataclass
class Reproduction:
    steps: List[str] = field(default_factory=list)
    consistency: str = "Always"
    environment: str = ""
    test_command: str = ""


@dataclass
class EvidenceRow:
    component: str
    input_val: str
    output_val: str
    expected: str
    actual: str
    status: str = "Pending"


@dataclass
class Hypothesis:
    number: int
    description: str
    test: str
    result: str = ""
    next_step: str = ""


@dataclass
class DebugSession:
    error_analysis: ErrorAnalysis = field(default_factory=ErrorAnalysis)
    reproduction: Reproduction = field(default_factory=Reproduction)
    evidence: List[EvidenceRow] = field(default_factory=list)
    hypotheses: List[Hypothesis] = field(default_factory=list)
    phase: int = 1


class WorksheetGenerator:
    def __init__(self, session: DebugSession):
        self.session = session

    def generate(self) -> str:
        lines = []
        lines.append("# Debugging Worksheet")
        lines.append("")
        lines.append("## Phase 1: Root Cause Investigation")
        lines.append("")
        lines.append("### Error Analysis")
        lines.append(f"- **Error message**: {self.session.error_analysis.error_message}")
        lines.append(f"- **Stack trace**: {self.session.error_analysis.stack_trace}")
        lines.append(f"- **Error code**: {self.session.error_analysis.error_code}")
        lines.append(f"- **File:line**: {self.session.error_analysis.file_line}")
        lines.append("")
        lines.append("### Reproduction")
        lines.append("- **Steps to reproduce**:")
        for i, step in enumerate(self.session.reproduction.steps, 1):
            lines.append(f"  {i}. {step}")
        lines.append(f"- **Consistency**: {self.session.reproduction.consistency}")
        lines.append(f"- **Environment**: {self.session.reproduction.environment}")
        lines.append(f"- **Test command**: {self.session.reproduction.test_command}")
        lines.append("")
        lines.append("### Evidence Gathering")
        lines.append("| Component | Input | Output | Expected | Actual | Status |")
        lines.append("|-----------|-------|--------|----------|--------|--------|")
        for ev in self.session.evidence:
            lines.append(f"| {ev.component} | {ev.input_val} | {ev.output_val} | {ev.expected} | {ev.actual} | {ev.status} |")
        lines.append("")
        lines.append("### Root Cause Hypothesis")
        for hyp in self.session.hypotheses:
            lines.append(f"- **Hypothesis {hyp.number}**: {hyp.description}")
            lines.append(f"  - **Test**: {hyp.test}")
            lines.append(f"  - **Result**: {hyp.result or 'Not yet tested'}")
            lines.append(f"  - **Next**: {hyp.next_step or 'N/A'}")
        lines.append("")
        lines.append("**Rule of Three Check**: [ ] < 3 attempts -> continue | [ ] >= 3 -> Question architecture")
        lines.append("")
        return "\n".join(lines)

    def save(self, output_path: str) -> str:
        content = self.generate()
        Path(output_path).write_text(content)
        return content