"""Self-contained skill judge.

Scores a skill (SKILL.md package) across 8 dimensions and produces a grade.
Fully stdlib-only so it can be loaded by path from other tools
(e.g. writing-skills test harness) and run standalone.

Standalone usage:
    python scripts/judge_skill.py --skill .
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# Dimension definitions: (id, name, max_score)
DIMENSIONS: list[tuple[str, str, int]] = [
    ("D1", "KnowledgeDelta", 20),
    ("D2", "MindsetProcedure", 15),
    ("D3", "AntiPattern", 15),
    ("D4", "SpecCompliance", 15),
    ("D5", "ProgressiveDisclosure", 15),
    ("D6", "FreedomCalibration", 15),
    ("D7", "PatternRecognition", 10),
    ("D8", "PracticalUsability", 15),
]

TOTAL_MAX = sum(max_score for _, _, max_score in DIMENSIONS)  # 120

_GRADE_BANDS: list[tuple[int, str]] = [
    (100, "A+"),
    (90, "A"),
    (80, "B+"),
    (70, "B"),
    (60, "C"),
]

_KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# --- D1 knowledge-delta heuristics ---------------------------------------

_RED_FLAG_RE = [
    re.compile(r"(?i)\bwhat is (a |an )?(pdf|docx|xlsx|json|csv|api|database|git|markdown|sdk|cli|html|css|sql|http|rest)\b"),
    re.compile(r"(?i)\bhow to (write|read|open|save|create) (a )?(file|loop|function|class)\b"),
    re.compile(r"(?i)\bintroduction to\b"),
    re.compile(r"(?i)\b(write clean code|handle errors|avoid errors|code carefully)\b"),
    re.compile(r"(?i)\bfor (a )?beginner\b"),
]

_GREEN_FLAG_RE = [
    re.compile(r"(?i)\bnever\b[^\n]*\bbecause\b"),
    re.compile(r"(?i)\btrade[- ]?off\b"),
    re.compile(r"(?i)\bedge case(s)?\b"),
    re.compile(r"(?i)\b(if|when) .{0,40} fails\b"),
    re.compile(r"(?i)\bdecision tree\b"),
    re.compile(r"(?i)\blearned (this )?the hard way\b"),
    re.compile(r"(?i)\bonly (an )?expert\b"),
    re.compile(r"(?i)\bwhy\b[^\n]*\bbecause\b"),
]

# --- D2 heuristics --------------------------------------------------------

_MINDSET_RE = [
    re.compile(r"(?i)\bbefore (you )?(design|start|write|begin|choose|build|review)[^\n]*\bask\b"),
    re.compile(r"(?i)\bask (yourself|yourself:)\b"),
    re.compile(r"(?i)\bthink (about|in terms of)\b"),
    re.compile(r"(?i)\bmindset\b"),
    re.compile(r"(?i)\bmental model\b"),
    re.compile(r"(?i)\bwhat makes this (memorable|good|work)\b"),
    re.compile(r"(?i)\btrade[- ]?off(s)?\b"),
    re.compile(r"(?i)\bthe test:?\b"),
]

_DOMAIN_PROC_RE = [
    re.compile(r"(?i)\bstep \d\b"),
    re.compile(r"(?i)\bworkflow\b"),
    re.compile(r"(?i)\bprotocol\b"),
    re.compile(r"(?i)\bdomain\b"),
    re.compile(r"(?i)\bchecklist\b"),
    re.compile(r"(?i)\bcheckpoint(s)?\b"),
    re.compile(r"(?i)\bphase \d\b"),
    re.compile(r"(?i)\bplaybook\b"),
    re.compile(r"(?i)\bprocedure(s)?\b"),
]

_GENERIC_PROC_RE = [
    re.compile(r"(?i)\bopen the file\b"),
    re.compile(r"(?i)\bsave the file\b"),
    re.compile(r"(?i)\bclick (the )?(ok|save|submit|next) button\b"),
    re.compile(r"(?i)\bpress enter\b"),
]

# --- D3 heuristics --------------------------------------------------------

_GENERIC_WARNING_RE = re.compile(
    r"(?i)\b(avoid (making )?mistakes|be careful|don'?t make mistakes|avoid errors)\b"
)
_NEVER_RE = re.compile(r"(?i)\b(never|do not|don'?t|must not)\b")
_NEVER_WITH_REASON_RE = re.compile(r"(?i)\b(never|do not|don'?t|must not)\b[^\n]{0,200}\b(because|since|the hard way|—|-)\b")
_ANTIPATTERN_SECTION_RE = re.compile(r"(?i)\b(never do|anti[- ]?pattern|NEVER list)\b")

# --- D4 heuristics --------------------------------------------------------

_WHEN_TRIGGER_RE = re.compile(r"(?i)\b(use when|use for|when to use|when you|for tasks|triggers?)\b")
_NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")

# --- D5 heuristics --------------------------------------------------------

_MANDATORY_RE = re.compile(r"(?i)\bmandatory\b")
_DO_NOT_LOAD_RE = re.compile(r"(?i)\bdo not load\b")
_READ_ENTIRE_RE = re.compile(r"(?i)\bread entire file\b")

# --- D6 heuristics --------------------------------------------------------

_LOW_FREEDOM_RE = [
    re.compile(r"(?i)\b(docx|pdf|xlsx|convert|parse|byte|checksum|validation|schema|protocol|serialize)\b"),
]
_HIGH_FREEDOM_RE = [
    re.compile(r"(?i)\b(creative|design|aesthetic|taste|style|art|brand|copywriting)\b"),
]
_EXACT_STEP_RE = re.compile(r"(?i)\b(step 1|run this|exact|precisely|must match|bit[- ]for[- ]bit)\b")
_PRINCIPLE_RE = re.compile(r"(?i)\b(principle|guideline|not a template|judgment|freedom)\b")

# --- D7 pattern detection -------------------------------------------------

_CODE_FENCE_COUNT = "```"
_NAV_LINK_RE = re.compile(r"\[`?[\w./\-]+\.md`?\]\([\w./\-]+\.md\)")
_PHASE_RE = re.compile(r"(?i)\b(phase \d|checkpoint|stage \d)\b")
_STEP_HEADING_RE = re.compile(r"(?m)^#{1,4}\s*(step|phase|stage|checkpoint)\s*\d", re.IGNORECASE)
_STRONG_NEVER_RE = re.compile(r"(?i)\b(never|do not|don'?t|must not)\b")

_PATTERN_EXPECTED_LINES: dict[str, tuple[int, int]] = {
    "tool": (180, 500),
    "process": (120, 350),
    "philosophy": (100, 250),
    "mindset": (30, 120),
    "navigation": (15, 80),
}

# --- D8 heuristics --------------------------------------------------------

_DECISION_TREE_RE = re.compile(r"(?i)\b(if [^\n]{0,60} then|when [^\n]{0,60},?\s+(try|use|do)|otherwise|else)\b")
_ERROR_HANDLING_RE = re.compile(r"(?i)\b(if [^\n]{0,60} fails|error handling|fallback|on error|exception|recovery)\b")
_EDGE_CASE_RE = re.compile(r"(?i)\b(edge case|unusual|special case|boundary condition)\b")
_ACTIONABILITY_RE = re.compile(r"(?i)\b(you must|must |always |never |run:? )\b")


def _clamp(value: float, low: float, high: float) -> int:
    return max(low, min(high, value))


def _body_text(text: str) -> str:
    """SKILL.md body without frontmatter, fenced code and quoted examples."""
    body = re.sub(r"^---\n.*?\n---", "", text, count=1, flags=re.DOTALL)
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r'"[^"\n]{0,200}"', "", body)
    body = re.sub(r"'[^'\n]{0,200}'", "", body)
    body = re.sub(r"`[^`\n]+`", "", body)
    return body


@dataclass
class DimensionScore:
    id: str
    name: str
    score: float
    max_score: float
    findings: list[str] = field(default_factory=list)


@dataclass
class GradeResult:
    """Full evaluation result. `grade()` returns a dict built from this."""

    skill_name: str
    skill_path: str
    dimensions: list[DimensionScore]
    total: float
    issues: list[str]
    timestamp: str

    @property
    def percentage(self) -> float:
        return round(self.total / TOTAL_MAX * 100, 1)

    @property
    def grade(self) -> str:
        for threshold, letter in _GRADE_BANDS:
            if self.total >= threshold:
                return letter
        return "F"

    @property
    def passed(self) -> bool:
        d1 = next(d for d in self.dimensions if d.id == "D1").score
        return self.total >= 70 and d1 >= 11

    @classmethod
    def from_dict(cls, data: dict) -> "GradeResult":
        dims = [
            DimensionScore(
                id=d_id,
                name=d["name"],
                score=d["score"],
                max_score=d["max"],
                findings=d.get("findings", []),
            )
            for d_id, d in data["dimensions"].items()
        ]
        return cls(
            skill_name=data["skill_name"],
            skill_path=data["skill_path"],
            dimensions=dims,
            total=data["total"],
            issues=data.get("issues", []),
            timestamp=data.get("timestamp", ""),
        )

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "skill_path": self.skill_path,
            "dimensions": {
                d.id: {
                    "name": d.name,
                    "score": int(d.score),
                    "max": int(d.max_score),
                    "findings": d.findings,
                }
                for d in self.dimensions
            },
            "total": int(self.total),
            "percentage": self.percentage,
            "grade": self.grade,
            "passed": self.passed,
            "issues": self.issues,
            "timestamp": self.timestamp,
        }

    def render_markdown(self) -> str:
        lines = [
            f"# Skill Judge Report: {self.skill_name}",
            "",
            f"- **Path**: `{self.skill_path}`",
            f"- **Total**: {int(self.total)} / {TOTAL_MAX} ({self.percentage}%)",
            f"- **Grade**: {self.grade}",
            f"- **Quality gate**: {'PASS' if self.passed else 'FAIL'}",
            f"- **Timestamp**: {self.timestamp}",
            "",
            "## Dimension Scores",
            "",
            "| Dim | Name | Score | Max |",
            "|-----|------|-------|-----|",
        ]
        for d in self.dimensions:
            lines.append(f"| {d.id} | {d.name} | {int(d.score)} | {int(d.max_score)} |")
        lines += ["", "## Issues", ""]
        if self.issues:
            for issue in self.issues:
                lines.append(f"- {issue}")
        else:
            lines.append("- None")
        lines += ["", "## Dimension Findings", ""]
        for d in self.dimensions:
            if d.findings:
                lines.append(f"**{d.id} ({d.name})**:")
                for f_ in d.findings:
                    lines.append(f"- {f_}")
                lines.append("")
        return "\n".join(lines)

    def render_html(self) -> str:
        rows = "\n".join(
            f"<tr><td>{d.id}</td><td>{d.name}</td><td>{int(d.score)}</td>"
            f"<td>{int(d.max_score)}</td>"
            f"<td style='width:200px'><div class='bar'>"
            f"<div class='fill' style='width:{int(d.score/max(d.max_score,1)*100)}%'></div>"
            f"</div></td></tr>"
            for d in self.dimensions
        )
        issues = "".join(f"<li>{i}</li>" for i in self.issues) or "<li>None</li>"
        return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Skill Judge Report: {self.skill_name}</title>
<style>
body {{ font-family: 'Segoe UI', system-ui, sans-serif; max-width: 760px; margin: 40px auto; padding: 0 20px; color: #222; }}
h1 {{ border-bottom: 3px solid #4a6; padding-bottom: 8px; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; }}
th {{ background: #f2f2f2; }}
.bar {{ background: #eee; border-radius: 4px; height: 12px; }}
.fill {{ background: #4a6; height: 12px; border-radius: 4px; }}
.grade {{ font-size: 2em; font-weight: bold; color: #2a6; }}
.fail {{ color: #b00; }} .pass {{ color: #2a6; }}
</style></head><body>
<h1>Skill Judge Report: {self.skill_name}</h1>
<p><strong>Path</strong>: <code>{self.skill_path}</code></p>
<p><strong>Total</strong>: {int(self.total)} / {TOTAL_MAX} ({self.percentage}%) — <span class="grade">{self.grade}</span></p>
<p class="{'pass' if self.passed else 'fail'}">Quality gate: {'PASS' if self.passed else 'FAIL'}</p>
<table><tr><th>Dim</th><th>Name</th><th>Score</th><th>Max</th><th></th></tr>{rows}</table>
<h2>Issues</h2><ul>{issues}</ul>
</body></html>"""


class SkillJudge:
    """Heuristic skill grader. Deterministic, stdlib only."""

    def grade(self, skill_path: str | os.PathLike[str]) -> dict:
        root = Path(skill_path)
        skill_md = root / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found under {root}")
        text = skill_md.read_text(encoding="utf-8")
        lower = text.lower()
        lines = text.splitlines()
        line_count = len(lines)
        issues: list[str] = []

        d1 = self._score_d1(lower, text, issues)
        d2 = self._score_d2(lower, lines, issues)
        d3 = self._score_d3(lower, lines, issues)
        d4 = self._score_d4(text, lines, root, issues)
        d5 = self._score_d5(text, lower, root, line_count, issues)
        d6 = self._score_d6(text, lower, lines, issues)
        d7 = self._score_d7(text, lower, root, line_count, issues)
        d8 = self._score_d8(lower, text, issues)

        dims = [
            DimensionScore("D1", "KnowledgeDelta", d1, 20),
            DimensionScore("D2", "MindsetProcedure", d2, 15),
            DimensionScore("D3", "AntiPattern", d3, 15),
            DimensionScore("D4", "SpecCompliance", d4, 15),
            DimensionScore("D5", "ProgressiveDisclosure", d5, 15),
            DimensionScore("D6", "FreedomCalibration", d6, 15),
            DimensionScore("D7", "PatternRecognition", d7, 10),
            DimensionScore("D8", "PracticalUsability", d8, 15),
        ]
        total = sum(d.score for d in dims)
        name = self._skill_name(text) or root.name
        result = GradeResult(
            skill_name=name,
            skill_path=str(root),
            dimensions=dims,
            total=total,
            issues=issues,
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        return result.to_dict()

    # -- helpers ------------------------------------------------------------

    def _skill_name(self, text: str) -> str | None:
        fm = self._frontmatter(text)
        if fm is None:
            return None
        m = re.search(r"(?m)^\s*name\s*:\s*(.+)$", fm)
        return m.group(1).strip() if m else None

    def _frontmatter(self, text: str) -> str | None:
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        return m.group(1) if m else None

    def _count(self, text: str, patterns: list[re.Pattern[str]]) -> int:
        return sum(len(p.findall(text)) for p in patterns)

    # -- dimensions ---------------------------------------------------------

    def _score_d1(self, lower: str, text: str, issues: list[str]) -> float:
        body = _body_text(text)
        red = self._count(body, _RED_FLAG_RE)
        green = self._count(body, _GREEN_FLAG_RE)
        score = _clamp(10 + 3 * min(green, 3) - 4 * min(red, 4), 0, 20)
        if red >= 3:
            score = min(score, 7)
        if green == 0:
            score = min(score, 12)
        if red >= 1:
            issues.append(f"D1: {red} redundant/tutorial section(s) dilute knowledge delta.")
        if green == 0:
            issues.append("D1: no expert-level signals found (decision trees, NEVER-with-reason, edge cases).")
        return score

    def _score_d2(self, lower: str, lines: list[str], issues: list[str]) -> float:
        mindset = self._count(lower, _MINDSET_RE)
        domain = self._count(lower, _DOMAIN_PROC_RE)
        generic = self._count(lower, _GENERIC_PROC_RE)
        score = _clamp(3 + 4 * min(mindset, 1) + 4 * min(domain, 1) + 3 * min(mindset * domain, 1), 0, 15)
        if generic >= 3 and mindset == 0:
            score = min(score, 6)
        if mindset == 0:
            issues.append("D2: no thinking-pattern guidance (e.g. 'Before X, ask...').")
        if domain == 0:
            issues.append("D2: no domain-specific procedures beyond generic steps.")
        return score

    def _score_d3(self, lower: str, lines: list[str], issues: list[str]) -> float:
        never_count = len(_NEVER_RE.findall(lower))
        reasoned = len(_NEVER_WITH_REASON_RE.findall(lower))
        has_section = bool(_ANTIPATTERN_SECTION_RE.search(lower))
        if never_count == 0:
            issues.append("D3: no anti-patterns (NEVER list) present.")
            return 2.0
        generic_only = bool(_GENERIC_WARNING_RE.search(lower)) and reasoned == 0
        if generic_only:
            issues.append("D3: only generic warnings, no reasoned NEVER list.")
            return 6.0
        score = _clamp(8 + 2 * min(reasoned, 3) + (3 if has_section else 0), 8, 15)
        if reasoned == 0:
            issues.append("D3: NEVER statements lack reasoning (WHY).")
        return score

    def _score_d4(self, text: str, lines: list[str], root: Path, issues: list[str]) -> float:
        fm = self._frontmatter(text)
        if fm is None:
            issues.append("D4: frontmatter missing or malformed.")
            return 3.0
        name_m = re.search(r"(?m)^\s*name\s*:\s*(.+)$", fm)
        desc_m = re.search(r"(?m)^\s*description\s*:\s*(.+)$", fm)
        name = name_m.group(1).strip() if name_m else ""
        desc = desc_m.group(1).strip() if desc_m else ""
        name_ok = bool(_NAME_RE.match(name))
        when_ok = bool(_WHEN_TRIGGER_RE.search(desc))
        length_ok = 50 <= len(desc) <= 400
        score = 6 + 3 * (1 if name_ok else 0) + 3 * (1 if when_ok else 0) + 3 * (1 if length_ok else 0)
        score = _clamp(score, 0, 15)
        if not name_ok:
            issues.append("D4: frontmatter name invalid (kebab-case required).")
        if not when_ok:
            issues.append("D4: description lacks WHEN/trigger context.")
        if not length_ok:
            issues.append(f"D4: description length {len(desc)} outside 50-400 ideal band.")
        return score

    def _score_d5(self, text: str, lower: str, root: Path, line_count: int, issues: list[str]) -> float:
        has_references = (root / "references").is_dir() or bool(_NAV_LINK_RE.findall(text))
        mandatory = bool(_MANDATORY_RE.search(lower) or _READ_ENTIRE_RE.search(lower))
        do_not_load = bool(_DO_NOT_LOAD_RE.search(lower))
        if line_count >= 500:
            base = 4.0
            issues.append("D5: SKILL.md exceeds 500 lines — content should move to references/.")
        elif line_count >= 300:
            base = 8.0
        else:
            base = 11.0
        score = _clamp(base + 2 * (1 if has_references else 0) + 2 * (1 if mandatory else 0) + (1 if do_not_load else 0), 0, 15)
        if not has_references:
            issues.append("D5: no on-demand reference files or links to sub-files.")
        return score

    def _score_d6(self, text: str, lower: str, lines: list[str], issues: list[str]) -> float:
        low = self._count(lower, _LOW_FREEDOM_RE) > 0
        high = self._count(lower, _HIGH_FREEDOM_RE) > 0
        exact = len(_EXACT_STEP_RE.findall(lower))
        principle = len(_PRINCIPLE_RE.findall(lower))
        if low:
            score = _clamp(10 + 4 * (1 if exact >= 2 else 0) + (1 if exact >= 4 else 0), 0, 15)
        elif high:
            if exact >= 3:
                score = 6.0
                issues.append("D6: creative task over-prescribed — freedom calibration off.")
            else:
                score = _clamp(10 + 4 * (1 if principle >= 1 else 0), 0, 15)
        else:
            score = _clamp(10 + 3 * (1 if principle >= 1 else 0), 0, 15)
        if not low and not high and exact == 0 and principle == 0:
            issues.append("D6: freedom calibration unclear — no explicit guidance on specificity level.")
        return score

    def _score_d7(self, text: str, lower: str, root: Path, line_count: int, issues: list[str]) -> float:
        fences = text.count(_CODE_FENCE_COUNT)
        nav_links = len(_NAV_LINK_RE.findall(text))
        phases = len(_PHASE_RE.findall(lower))
        step_headings = len(_STEP_HEADING_RE.findall(text))
        never_count = len(_STRONG_NEVER_RE.findall(lower))
        pattern: str | None = None
        if nav_links >= 3 and line_count < 120:
            pattern = "navigation"
        elif fences >= 2 and (bool(_MANDATORY_RE.search(lower)) or bool(_DECISION_TREE_RE.search(lower))):
            pattern = "tool"
        elif step_headings >= 2 or phases >= 2:
            pattern = "process"
        elif never_count >= 3 and line_count < 150:
            pattern = "mindset"
        elif "philosophy" in lower:
            pattern = "philosophy"
        if pattern is None:
            issues.append("D7: no recognizable official pattern (tool/process/mindset/philosophy/navigation).")
            return 4.0
        lo, hi = _PATTERN_EXPECTED_LINES.get(pattern, (0, 9999))
        lines_ok = lo <= line_count <= hi
        score = 8.0 + (2.0 if lines_ok else 0.0)
        if not lines_ok:
            issues.append(f"D7: identified {pattern} pattern but line count {line_count} outside {lo}-{hi} band.")
        return score

    def _score_d8(self, lower: str, text: str, issues: list[str]) -> float:
        decision = bool(_DECISION_TREE_RE.search(lower))
        fences = text.count(_CODE_FENCE_COUNT) >= 2
        errors = bool(_ERROR_HANDLING_RE.search(lower))
        edge = bool(_EDGE_CASE_RE.search(lower))
        action = bool(_ACTIONABILITY_RE.search(lower))
        present = sum([decision, fences, errors, edge])
        score = _clamp(5 + 2.5 * present + 2.5 * (1 if action else 0), 0, 15)
        missing = []
        if not decision:
            missing.append("decision trees")
        if not fences:
            missing.append("working code examples")
        if not errors:
            missing.append("error handling")
        if not edge:
            missing.append("edge cases")
        if missing:
            issues.append("D8: missing " + ", ".join(missing) + ".")
        return score


# --- quality gate ---------------------------------------------------------

def quality_gate(result: dict) -> tuple[bool, list[str]]:
    """Blocking gate: fail if total < 70 or D1 < 11."""
    total = result["total"]
    d1 = result["dimensions"]["D1"]["score"]
    reasons = []
    if total < 70:
        reasons.append(f"total {total} < 70")
    if d1 < 11:
        reasons.append(f"D1 {d1} < 11")
    return (not reasons, reasons)


# --- history --------------------------------------------------------------

def _default_history() -> Path:
    return Path.home() / ".skill-judge" / "history.jsonl"


def _append_history(result: dict, history_path: Path) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(result) + "\n")


def _load_history(history_path: Path) -> list[dict]:
    if not history_path.exists():
        return []
    records = []
    with history_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


# --- benchmark / calibration ---------------------------------------------

BAND_RULES: dict[str, tuple[float, float]] = {
    "expert": (90, 121),
    "strong": (80, 90),
    "adequate": (70, 80),
    "needs_work": (60, 70),
    "insufficient": (0, 60),
}


def _band_for_total(total: float) -> str:
    for name, (lo, hi) in BAND_RULES.items():
        if lo <= total < hi:
            return name
    return "expert" if total >= 121 else "insufficient"


def run_calibration(benchmarks_dir: Path) -> dict:
    """Run every *benchmark.json in benchmarks_dir against the judge."""
    results = []
    total = passed = 0
    for cfg_path in sorted(benchmarks_dir.glob("*.json")):
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        skills_dir = Path(cfg.get("skills_dir", "."))
        if not skills_dir.is_absolute():
            skills_dir = (cfg_path.parent / skills_dir).resolve()
        for expectation in cfg.get("expectations", []):
            skill = skills_dir / expectation["skill"]
            expected = expectation["band"]
            try:
                result = SkillJudge().grade(str(skill))
            except FileNotFoundError as exc:
                results.append(
                    {"skill": expectation["skill"], "expected_band": expected,
                     "actual_band": "missing", "total": 0, "grade": "F", "passed": False,
                     "reason": str(exc)}
                )
                total += 1
                continue
            actual = _band_for_total(result["total"])
            ok = actual == expected
            results.append(
                {"skill": expectation["skill"], "expected_band": expected,
                 "actual_band": actual, "total": result["total"],
                 "grade": result["grade"], "passed": ok}
            )
            total += 1
            passed += 1 if ok else 0
    return {
        "benchmarks_dir": str(benchmarks_dir),
        "checked": total,
        "passed": passed,
        "failed": total - passed,
        "results": results,
    }


# --- CLI ------------------------------------------------------------------

def _p(name: str, **kwargs) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(prog=f"skill-judge {name}", **kwargs)


def _cmd_evaluate(args: list[str]) -> int:
    p = _p("evaluate")
    p.add_argument("--skill", required=True)
    p.add_argument("--format", choices=["text", "json", "html", "markdown"], default="text")
    p.add_argument("--output")
    p.add_argument("--history")
    p.add_argument("--mode", choices=["self-eval", "full"], default="full")
    ns = p.parse_args(args)
    try:
        result = SkillJudge().grade(ns.skill)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1
    _append_history(result, Path(ns.history) if ns.history else _default_history())
    fmt = ns.format
    if fmt == "json":
        out = json.dumps(result, indent=2)
    elif fmt == "html":
        out = GradeResult.from_dict(result).render_html()
    elif fmt == "markdown":
        out = GradeResult.from_dict(result).render_markdown()
    else:
        out = _render_text(result)
    if ns.output:
        Path(ns.output).write_text(out, encoding="utf-8")
        print(f"Report written to {ns.output}")
    else:
        print(out)
    return 0


def _cmd_batch(args: list[str]) -> int:
    p = _p("batch")
    p.add_argument("--skills-dir", required=True)
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--history")
    ns = p.parse_args(args)
    skills_dir = Path(ns.skills_dir)
    if not skills_dir.is_dir():
        print(f"ERROR: {skills_dir} is not a directory")
        return 1
    results = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        skill_dir = skill_md.parent
        try:
            result = SkillJudge().grade(str(skill_dir))
        except FileNotFoundError:
            continue
        results.append(result)
        _append_history(result, Path(ns.history) if ns.history else _default_history())
    if ns.format == "json":
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['skill_name']:<24} {int(r['total']):>3}/120  {r['grade']:<3} {'PASS' if r['passed'] else 'FAIL'}")
        print(f"\n{len(results)} skill(s) evaluated.")
    return 0


def _cmd_compare(args: list[str]) -> int:
    p = _p("compare")
    p.add_argument("--skill-a", required=True)
    p.add_argument("--skill-b", required=True)
    ns = p.parse_args(args)
    try:
        a = SkillJudge().grade(ns.skill_a)
        b = SkillJudge().grade(ns.skill_b)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1
    a_g = GradeResult.from_dict(a)
    b_g = GradeResult.from_dict(b)
    winner = a_g.skill_name if a_g.total >= b_g.total else b_g.skill_name
    print(f"{a_g.skill_name}: {int(a_g.total)} ({a_g.grade})")
    print(f"{b_g.skill_name}: {int(b_g.total)} ({b_g.grade})")
    print(f"Winner: {winner}")
    for da, db in zip(a_g.dimensions, b_g.dimensions):
        marker = ">" if da.score > db.score else ("<" if da.score < db.score else "=")
        print(f"  {da.id} {int(da.score):>3} {marker} {int(db.score):>3}")
    return 0


def _cmd_calibrate(args: list[str]) -> int:
    p = _p("calibrate")
    p.add_argument("--benchmarks-dir", required=True)
    p.add_argument("--format", choices=["text", "json"], default="text")
    ns = p.parse_args(args)
    benchmarks_dir = Path(ns.benchmarks_dir)
    if not benchmarks_dir.is_dir():
        print(f"ERROR: {benchmarks_dir} is not a directory")
        return 1
    report = run_calibration(benchmarks_dir)
    if ns.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"Checked {report['checked']} benchmark entries, passed {report['passed']}, failed {report['failed']}")
        for r in report["results"]:
            status = "PASS" if r["passed"] else "FAIL"
            detail = f"{r['actual_band']} ({int(r['total'])}/{TOTAL_MAX})" if r["actual_band"] != "missing" else r.get("reason", "missing")
            print(f"  [{status}] {r['skill']:<28} expected={r['expected_band']:<12} actual={detail}")
    return 0 if report["failed"] == 0 else 1


def _cmd_certify(args: list[str]) -> int:
    p = _p("certify")
    p.add_argument("--skill", required=True)
    p.add_argument("--level", choices=["blocked", "adequate", "strong", "expert"], default=None)
    ns = p.parse_args(args)
    try:
        result = SkillJudge().grade(ns.skill)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1
    total = result["total"]
    if ns.level == "expert":
        ok = total >= 90 and result["passed"]
    elif ns.level == "strong":
        ok = total >= 80 and result["passed"]
    elif ns.level == "adequate":
        ok = total >= 70
    elif ns.level == "blocked":
        ok = not result["passed"]
    else:
        ok = result["passed"]
    print(f"{result['skill_name']}: {int(total)} ({result['grade']}) -> {'CERTIFIED' if ok else 'NOT CERTIFIED'}")
    return 0 if ok else 1


def _cmd_history(args: list[str]) -> int:
    p = _p("history")
    p.add_argument("--skill", required=True)
    p.add_argument("--show-trend", action="store_true")
    p.add_argument("--history")
    ns = p.parse_args(args)
    records = _load_history(Path(ns.history) if ns.history else _default_history())
    matches = [r for r in records if r.get("skill_name") == ns.skill]
    if not matches:
        print(f"No history for {ns.skill}")
        return 1
    latest = matches[-1]
    print(f"{latest['skill_name']}: last {int(latest['total'])} ({latest['grade']}) at {latest['timestamp']}")
    if ns.show_trend:
        totals = [int(r["total"]) for r in matches]
        print(f"  {len(totals)} evaluation(s), range {min(totals)}-{max(totals)}, "
              f"latest {totals[-1]} vs first {totals[0]}")
    return 0


def _render_text(result: dict) -> str:
    lines = [
        f"Skill: {result['skill_name']}",
        f"Path: {result['skill_path']}",
        f"Total: {result['total']}/{TOTAL_MAX} ({result['percentage']}%)  Grade: {result['grade']}",
        f"Quality gate: {'PASS' if result['passed'] else 'FAIL'}",
        "",
        "Dimensions:",
    ]
    for d_id, d in result["dimensions"].items():
        lines.append(f"  {d_id} {d['name']:<22} {d['score']:>3}/{d['max']}")
    if result["issues"]:
        lines += ["", "Issues:"]
        lines += [f"  - {i}" for i in result["issues"]]
    return "\n".join(lines)


SUBCOMMANDS = {
    "evaluate": _cmd_evaluate,
    "batch": _cmd_batch,
    "compare": _cmd_compare,
    "calibrate": _cmd_calibrate,
    "certify": _cmd_certify,
    "history": _cmd_history,
}


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__.strip())
        print("\nCommands: " + ", ".join(sorted(SUBCOMMANDS)))
        print("  python scripts/judge_skill.py --skill .   (shorthand for evaluate)")
        return 1
    # Shorthand: no subcommand but global --skill flag -> evaluate.
    if args[0] not in SUBCOMMANDS and "--skill" in args:
        args = ["evaluate"] + args
    cmd = args[0]
    if cmd not in SUBCOMMANDS:
        print(f"ERROR: unknown command '{cmd}'")
        print("Commands: " + ", ".join(sorted(SUBCOMMANDS)))
        return 1
    return SUBCOMMANDS[cmd](args[1:])


if __name__ == "__main__":
    sys.exit(main())
