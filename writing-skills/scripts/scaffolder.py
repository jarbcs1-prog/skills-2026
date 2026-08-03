#!/usr/bin/env python3
"""Skill scaffolder for the writing-skills skill.

Generates a valid skill directory (SKILL.md + supporting structure) from one
of ten template types. Every template produces a TDD-compatible structure:
pressure scenarios are emitted into evals/evals.json so the skill can be
tested with the SkillTestHarness immediately after creation.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# Template identifiers, in the order shown by `writing-skills init --help`.
TEMPLATES: dict[str, str] = {
    "discipline": "Enforces a rule/requirement (TDD, verification-before-completion)",
    "technique": "Concrete method with steps to follow (how-to guide)",
    "pattern": "Way of thinking about problems (mental model)",
    "reference": "API docs, syntax guides, tool documentation",
    "workflow": "Multi-step process with explicit order and gates",
    "integration": "API/client integration with connection details",
    "generator": "Produces code or artifacts from inputs",
    "validator": "Lints, checks or validates inputs/outputs",
    "monitor": "Observability: watch a system and report state",
    "transform": "Converts data from one form to another",
}

# Intro sentence and section plan per template.
_TEMPLATE_SECTIONS: dict[str, tuple[str, list[str]]] = {
    "discipline": (
        "**Writing this skill IS Test-Driven Development applied to a rule.** "
        "Run a failing baseline, write the rule to stop the failure, then refactor "
        "until the rule is bulletproof against rationalization.",
        ["Core Rule", "Rationalization Table", "Red Flags - STOP and Start Over", "No Exceptions"],
    ),
    "technique": (
        "**This is a concrete method with steps to follow.** "
        "The value is in the ordering: apply the steps in sequence and the outcome "
        "is reproducible.",
        ["Steps", "Edge Cases", "Missing Information", "Common Mistakes"],
    ),
    "pattern": (
        "**This is a way of thinking about problems.** "
        "Learn to recognise when the pattern applies and, just as importantly, when it does not.",
        ["When It Applies", "When NOT to Apply", "Recognition Signals", "Counter-Examples"],
    ),
    "reference": (
        "**This is a retrieval-oriented reference.** "
        "Structure it so an agent can find the right fact fast: quick-reference table first, "
        "deep detail in supporting files.",
        ["Quick Reference", "Detailed Reference", "Gap Coverage", "Common Lookups"],
    ),
    "workflow": (
        "**This is a multi-step process with explicit gates.** "
        "Each step has an entry condition and an exit criterion; the workflow stops if a gate fails.",
        ["Step Gates", "Workflow Diagram", "Early-Stop Conditions", "Common Mistakes"],
    ),
    "integration": (
        "**This connects to an external service or API.** "
        "Document authentication, request/response shapes and failure modes explicitly.",
        ["Authentication", "Endpoints", "Error Handling", "Rate Limits"],
    ),
    "generator": (
        "**This produces code or artifacts from inputs.** "
        "Make inputs, outputs and generation rules explicit so output is deterministic.",
        ["Inputs", "Output Format", "Generation Rules", "Validation"],
    ),
    "validator": (
        "**This checks whether inputs or outputs are valid.** "
        "Define what 'valid' means precisely: pass criteria, fail criteria and report format.",
        ["Pass Criteria", "Fail Criteria", "Report Format", "Common Mistakes"],
    ),
    "monitor": (
        "**This watches a system and reports its state.** "
        "Define what to watch, how often, what thresholds matter and what the alert response is.",
        ["Metrics Watched", "Thresholds", "Alert Response", "Common Mistakes"],
    ),
    "transform": (
        "**This converts data from one form to another.** "
        "Make the source schema, target schema and mapping rules explicit.",
        ["Source Schema", "Target Schema", "Mapping Rules", "Lossy Conversions"],
    ),
}

_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass
class SkillMetadata:
    """Metadata persisted to skill.yaml for registry/versioning purposes."""

    name: str
    template: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    license: str = "MIT"
    compatibility: str = ""
    dependencies: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    evals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "license": self.license,
            "compatibility": self.compatibility,
            "dependencies": self.dependencies,
            "scripts": self.scripts,
            "references": self.references,
            "assets": self.assets,
            "tests": self.tests,
            "evals": self.evals,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SkillMetadata":
        return cls(
            name=data.get("name", ""),
            template=data.get("template", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
            license=data.get("license", "MIT"),
            compatibility=data.get("compatibility", ""),
            dependencies=list(data.get("dependencies", [])),
            scripts=list(data.get("scripts", [])),
            references=list(data.get("references", [])),
            assets=list(data.get("assets", [])),
            tests=list(data.get("tests", [])),
            evals=list(data.get("evals", [])),
        )


class SkillNameError(ValueError):
    """Raised when a skill name violates the kebab-case naming rules."""


def validate_name(name: str) -> None:
    """Validate a skill name: letters, numbers and hyphens only, kebab-case."""
    if not name or not _NAME_RE.match(name):
        raise SkillNameError(
            "Skill name must be kebab-case: lowercase letters, numbers and "
            "hyphens only (e.g. 'condition-based-waiting')."
        )


def _build_skill_md(name: str, template: str, description: str) -> str:
    intro, sections = _TEMPLATE_SECTIONS[template]
    title = name.replace("-", " ").title()
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
        "---",
        "",
        f"# {title}",
        "",
        "## Overview",
        intro,
        "",
        "## When to Use",
        "",
        "- [Triggering conditions go here]",
        "",
        "## Core Content",
        "",
        *[f"### {s}\n\n- " for s in sections],
        "",
        "## Verification",
        "",
        "Run the pressure scenarios in `evals/evals.json` with a subagent before "
        "and after loading this skill. A skill without a failing baseline test is "
        "an unverified skill.",
        "",
    ]
    return "\n".join(lines)


def generate_evals(name: str, scenarios: list[str]) -> str:
    """Generate evals/evals.json content for the given scenario names."""
    from .test_harness import PRESSURE_SCENARIOS

    evals = []
    for index, scenario_name in enumerate(scenarios, start=1):
        scenario = PRESSURE_SCENARIOS.get(scenario_name)
        if scenario is None:
            continue
        evals.append(
            {
                "id": index,
                "name": scenario_name,
                "prompt": scenario.prompt,
                "expected_output": scenario.expectation,
                "expectations": [f"The agent {scenario.expectation}"],
            }
        )
    return json.dumps({"skill_name": name, "evals": evals}, indent=2)


class SkillScaffolder:
    """Creates valid skill directory structures from templates."""

    def __init__(self, scenario_sets: Optional[dict[str, list[str]]] = None) -> None:
        # Maps template -> scenario names to embed in evals/evals.json.
        self.scenario_sets = scenario_sets or {
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

    def create(
        self,
        name: str,
        template: str,
        target_dir: Path,
        description: str = "",
        author: str = "",
        version: str = "1.0.0",
        dependencies: Optional[list[str]] = None,
    ) -> Path:
        """Create a skill directory and return its path.

        Raises:
            SkillNameError: for invalid names.
            ValueError: for unknown templates or duplicate skill directories.
        """
        validate_name(name)
        if template not in TEMPLATES:
            raise ValueError(f"Unknown template '{template}'. Choose from: {', '.join(TEMPLATES)}")

        description = description.strip() or (
            f"Use when {name.replace('-', ' ')} is relevant and {template} guidance is needed"
        )
        root = Path(target_dir) / name
        if root.exists():
            raise ValueError(f"Skill directory already exists: {root}")

        root.mkdir(parents=True, exist_ok=True)
        for sub in ("scripts", "references", "assets", "evals"):
            (root / sub).mkdir(exist_ok=True)

        (root / "SKILL.md").write_text(
            _build_skill_md(name, template, description), encoding="utf-8"
        )
        (root / "evals" / "evals.json").write_text(
            generate_evals(name, self.scenario_sets.get(template, ["application"])),
            encoding="utf-8",
        )

        metadata = SkillMetadata(
            name=name,
            template=template,
            description=description,
            author=author,
            version=version,
            dependencies=list(dependencies or []),
            scripts=[],
            tests=[],
            evals=["evals/evals.json"],
        )
        (root / "skill.yaml").write_text(self._render_manifest(metadata), encoding="utf-8")
        return root

    @staticmethod
    def _render_manifest(metadata: SkillMetadata) -> str:
        now = datetime.now().strftime("%Y-%m-%d")
        lines = [
            f"name: {metadata.name}",
            f"version: {metadata.version}",
            f"template: {metadata.template}",
            f"created: {now}",
            f"description: '{metadata.description}'",
            f"author: {metadata.author or 'anonymous'}",
            f"license: {metadata.license}",
        ]
        for key in ("compatibility", "dependencies", "scripts", "references", "assets", "tests", "evals"):
            value = getattr(metadata, key)
            if isinstance(value, list):
                lines.append(f"{key}: {json.dumps(value)}")
            else:
                lines.append(f"{key}: {value or ''}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def describe_templates() -> str:
        lines = []
        for name, desc in TEMPLATES.items():
            lines.append(f"  {name:12s} {desc}")
        return "\n".join(lines)


def list_scaffolded_files(skill_dir: Path) -> list[Path]:
    """Return the relative paths of all files in a skill directory."""
    return sorted(p.relative_to(skill_dir) for p in skill_dir.rglob("*") if p.is_file())
