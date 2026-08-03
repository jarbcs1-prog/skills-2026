"""Template registry for the skill-creator scaffolder.

Defines the ten scaffold templates (tool/analysis/integration/workflow/review/
generator/monitor/transform/validator/router), where their files live under
``templates/``, and shared placeholder substitution helpers.

Placeholders use the ``{{name}}`` form and are substituted by
:func:`placeholders_substitute`.
"""

from __future__ import annotations

import re
from pathlib import Path

TEMPLATES: dict[str, str] = {
    "tool": "A focused tool for one practical task (e.g. file-format operations).",
    "analysis": "Data analysis and reporting over structured input.",
    "integration": "Connects to external services and APIs.",
    "workflow": "A multi-step process executed in a fixed order.",
    "review": "Audits code, docs or configuration against standards.",
    "generator": "Produces code or content from a specification.",
    "monitor": "Observes a system and raises alerts on deviation.",
    "transform": "Converts data between formats or schemas.",
    "validator": "Checks input and reports violations with locations.",
    "router": "Delegates work to the right downstream handler.",
}

TEMPLATE_NAMES: tuple[str, ...] = tuple(TEMPLATES.keys())

_SHARED_DIR_NAME = "_shared"
_PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def describe_templates() -> str:
    """Return human-readable lines describing every template."""
    lines = []
    for name in TEMPLATE_NAMES:
        lines.append(f"{name}: {TEMPLATES[name]}")
    return "\n".join(lines)


def templates_root() -> Path:
    """Absolute path to the ``templates/`` directory."""
    return Path(__file__).resolve().parent.parent / "templates"


def shared_file(name: str) -> Path:
    """Path to a shared template file inside ``templates/_shared``."""
    return templates_root() / _SHARED_DIR_NAME / name


def template_file(template: str, filename: str) -> Path:
    """Path to ``filename`` inside a specific template directory."""
    return templates_root() / template / filename


def is_known_template(template: str) -> bool:
    """Return True when ``template`` is one of the ten scaffold types."""
    return template in TEMPLATES


def read_shared(name: str) -> str:
    """Read and return the text of a shared template file."""
    return shared_file(name).read_text(encoding="utf-8")


def placeholders_substitute(text: str, mapping: dict[str, object]) -> str:
    """Replace ``{{key}}`` placeholders in ``text`` using ``mapping``.

    Unknown placeholders are left untouched so the caller can detect them.
    """
    def _replace(match: "re.Match[str]") -> str:
        key = match.group(1)
        if key in mapping:
            value = mapping[key]
            if isinstance(value, (list, tuple)):
                return str(list(value))
            return str(value)
        return match.group(0)

    return _PLACEHOLDER_RE.sub(_replace, text)


def missing_placeholders(text: str) -> list[str]:
    """Return the names of every placeholder referenced in ``text``."""
    return list(dict.fromkeys(_PLACEHOLDER_RE.findall(text)))
