"""Verification templates per project type.

Each project type maps a phase (pre-commit, pre-push, pre-deploy) to an ordered
list of verification steps. Commands are templates that may reference
``{project_dir}``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .verifier import VerificationStep


@dataclass
class ProjectType:
    """Descriptor for a supported project type."""

    name: str
    manifest_files: tuple[str, ...]
    phases: dict[str, list[VerificationStep]] = field(default_factory=dict)


_VERIFICATION_TEMPLATES: dict[str, ProjectType] = {
    "python": ProjectType(
        name="python",
        manifest_files=("pyproject.toml", "requirements.txt", "setup.py", "Pipfile"),
        phases={
            "pre-commit": [
                VerificationStep("tests", "pytest tests/ -q", expected="pass", phase="pre-commit"),
                VerificationStep("lint", "ruff check .", expected="pass", phase="pre-commit"),
                VerificationStep("typecheck", "mypy .", expected="pass", phase="pre-commit"),
            ],
            "pre-push": [
                VerificationStep("tests", "pytest tests/ -q", expected="pass", phase="pre-push"),
                VerificationStep("lint", "ruff check .", expected="pass", phase="pre-push"),
                VerificationStep("typecheck", "mypy .", expected="pass", phase="pre-push"),
                VerificationStep("security", "bandit -r . -q", expected="pass", phase="pre-push"),
            ],
            "pre-deploy": [
                VerificationStep("tests", "pytest tests/ -q", expected="pass", phase="pre-deploy"),
                VerificationStep("build", "python -m compileall -q {project_dir}", expected="pass", phase="pre-deploy"),
            ],
        },
    ),
    "rust": ProjectType(
        name="rust",
        manifest_files=("Cargo.toml",),
        phases={
            "pre-commit": [
                VerificationStep("tests", "cargo test --all --quiet", expected="pass", phase="pre-commit"),
                VerificationStep("lint", "cargo clippy -- -D warnings", expected="pass", phase="pre-commit"),
                VerificationStep("fmt", "cargo fmt --check", expected="pass", phase="pre-commit"),
            ],
            "pre-push": [
                VerificationStep("tests", "cargo test --all --quiet", expected="pass", phase="pre-push"),
                VerificationStep("build", "cargo build --release", expected="pass", phase="pre-push"),
                VerificationStep("audit", "cargo audit", expected="pass", phase="pre-push"),
            ],
            "pre-deploy": [
                VerificationStep("build", "cargo build --release", expected="pass", phase="pre-deploy"),
                VerificationStep("tests", "cargo test --all --quiet", expected="pass", phase="pre-deploy"),
            ],
        },
    ),
    "javascript": ProjectType(
        name="javascript",
        manifest_files=("package.json",),
        phases={
            "pre-commit": [
                VerificationStep("tests", "npm test -- --ci", expected="pass", phase="pre-commit"),
                VerificationStep("lint", "npm run lint", expected="pass", phase="pre-commit"),
            ],
            "pre-push": [
                VerificationStep("tests", "npm test -- --ci", expected="pass", phase="pre-push"),
                VerificationStep("build", "npx tsc --noEmit", expected="pass", phase="pre-push"),
                VerificationStep("audit", "npm audit --audit-level=high", expected="pass", phase="pre-push"),
            ],
            "pre-deploy": [
                VerificationStep("build", "npm run build", expected="pass", phase="pre-deploy"),
            ],
        },
    ),
    "go": ProjectType(
        name="go",
        manifest_files=("go.mod",),
        phases={
            "pre-commit": [
                VerificationStep("tests", "go test ./...", expected="pass", phase="pre-commit"),
                VerificationStep("vet", "go vet ./...", expected="pass", phase="pre-commit"),
            ],
            "pre-push": [
                VerificationStep("tests", "go test ./...", expected="pass", phase="pre-push"),
                VerificationStep("build", "go build ./...", expected="pass", phase="pre-push"),
                VerificationStep("lint", "golangci-lint run", expected="pass", phase="pre-push"),
            ],
            "pre-deploy": [
                VerificationStep("build", "go build ./...", expected="pass", phase="pre-deploy"),
            ],
        },
    ),
    "generic": ProjectType(
        name="generic",
        manifest_files=(),
        phases={
            "pre-commit": [
                VerificationStep("tests", "test -x run-tests.sh && ./run-tests.sh", expected="pass", phase="pre-commit"),
            ],
            "pre-push": [
                VerificationStep("tests", "test -x run-tests.sh && ./run-tests.sh", expected="pass", phase="pre-push"),
                VerificationStep("build", "test -x build.sh && ./build.sh", expected="pass", phase="pre-push"),
            ],
            "pre-deploy": [
                VerificationStep("deploy", "test -x deploy.sh && ./deploy.sh --dry-run", expected="pass", phase="pre-deploy"),
            ],
        },
    ),
}


def get_verification_commands(project_type: str, phase: str) -> list[VerificationStep]:
    """Return ordered verification steps for a project type and phase."""
    project = _VERIFICATION_TEMPLATES.get(project_type)
    if project is None:
        project = _VERIFICATION_TEMPLATES["generic"]
    return project.phases.get(phase, [])


def get_project_types() -> list[str]:
    """Return names of all supported project types."""
    return list(_VERIFICATION_TEMPLATES)


def project_type_for_manifest(manifest_files: tuple[str, ...]) -> str:
    """Return the project type name whose manifest set matches the given files."""
    for project_type, project in _VERIFICATION_TEMPLATES.items():
        if set(project.manifest_files) == set(manifest_files):
            return project_type
    return "generic"


def render_step(step: VerificationStep, project_dir: str | Path = ".") -> VerificationStep:
    """Render a step template, substituting placeholders."""
    root = Path(project_dir).resolve()
    return VerificationStep(
        name=step.name,
        command=step.command.format(project_dir=str(root)),
        expected=step.expected,
        phase=step.phase,
    )
