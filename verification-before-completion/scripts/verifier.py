"""Verification engine for the verification-before-completion skill.

Provides evidence-gathering primitives: run a command, capture output and
exit code, match expected results, and record the outcome so completion
claims are always backed by fresh verification evidence.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import os


def _is_windows() -> bool:
    return os.name == "nt"


@dataclass
class VerificationStep:
    """A single verification command plus what counts as passing."""

    name: str
    command: str
    expected: str = "pass"
    phase: str = "pre-commit"


@dataclass
class VerificationResult:
    """Outcome of running one verification step."""

    passed: bool
    name: str
    command: str
    output: str = ""
    exit_code: int | None = None
    duration: float = 0.0
    timestamp: str = ""
    reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ComplianceReport:
    """Aggregate verification compliance metrics over a period."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    passed_rate: float = 0.0
    false_completion_rate: float = 0.0
    avg_verification_time: float = 0.0
    most_common_failures: list[str] = field(default_factory=list)
    emergency_overrides: int = 0


class VerificationEngine:
    """Runs verification steps and records evidence."""

    EXPECTED_MODES = ("pass", "fail")

    def __init__(self, history_path: str | Path | None = None):
        self.history_path = Path(history_path) if history_path else None

    def run_step(self, step: VerificationStep) -> VerificationResult:
        """Execute a single verification step and evaluate the result.

        ``expected`` semantics:
          - ``"pass"``: command must exit 0
          - ``"fail"``: command must exit non-zero
          - anything else: a regex, the command must exit 0 and output must match
        """
        start = time.monotonic()
        timestamp = datetime.now().isoformat(timespec="seconds")
        try:
            command = self._prepare_command(step.command)
            proc = subprocess.run(
                command,
                shell=isinstance(command, str),
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            duration = time.monotonic() - start
            return VerificationResult(
                passed=False,
                name=step.name,
                command=step.command,
                output="(timed out after 120s)",
                exit_code=None,
                duration=round(duration, 3),
                timestamp=timestamp,
                reason="verification timed out",
            )
        except OSError as exc:
            duration = time.monotonic() - start
            return VerificationResult(
                passed=False,
                name=step.name,
                command=step.command,
                output=str(exc),
                exit_code=None,
                duration=round(duration, 3),
                timestamp=timestamp,
                reason="could not run command",
            )

        duration = time.monotonic() - start
        output = f"{proc.stdout}\n{proc.stderr}".strip()
        passed = self._evaluate(step.expected, proc.returncode, output)
        reason = self._reason(step.expected, proc.returncode, output)
        result = VerificationResult(
            passed=passed,
            name=step.name,
            command=step.command,
            output=output,
            exit_code=proc.returncode,
            duration=round(duration, 3),
            timestamp=timestamp,
            reason=reason,
        )
        if self.history_path:
            self._record(result)
        return result

    @staticmethod
    def _prepare_command(command: str) -> str | list[str]:
        """Build a runnable command from a shell string.

        On Windows the string is passed to ``cmd.exe`` which splits on spaces,
        breaking executables whose path contains spaces. Detect the longest
        leading token run that resolves to a real executable and quote it.
        """
        if not _is_windows():
            return command
        head = command.lstrip()
        if head.startswith('"'):
            return command
        parts = head.split(" ")
        for i in range(len(parts), 0, -1):
            candidate = " ".join(parts[:i])
            if shutil.which(candidate) is not None or Path(candidate).exists():
                if i > 1:
                    return f'"{candidate}"' + (" " + " ".join(parts[i:]) if len(parts) > i else "")
                return command
        return command

    def run_all(self, steps: list[VerificationStep]) -> list[VerificationResult]:
        """Run steps in order and return results for each."""
        results = []
        for step in steps:
            results.append(self.run_step(step))
        return results

    def run_with_override(
        self, steps: list[VerificationStep], reason: str, approver: str = ""
    ) -> list[VerificationResult]:
        """Run steps but treat failures as warnings with an emergency audit trail.

        Records an `emergency override` entry in the history so compliance
        reports can surface how often overrides are used.
        """
        import os

        results = self.run_all(steps)
        now = datetime.now().isoformat(timespec="seconds")
        for result in results:
            if not result.passed:
                result.reason = f"EMERGENCY OVERRIDE: {reason}"
        if self.history_path:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            audit = {
                "timestamp": now,
                "name": "emergency override",
                "passed": True,  # override means we proceed despite failures
                "command": "",
                "reason": "emergency override",
                "duration": 0.0,
                "exit_code": 0,
                "output": "",
                "override_reason": reason,
                "approver": approver,
                "triggered_by": os.environ.get("GITHUB_ACTOR", os.environ.get("USER", "")),
            }
            with self.history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(audit) + "\n")
        return results

    @staticmethod
    def _evaluate(expected: str, exit_code: int, output: str) -> bool:
        if expected == "pass":
            return exit_code == 0
        if expected == "fail":
            return exit_code != 0
        return exit_code == 0 and re.search(expected, output, re.IGNORECASE) is not None

    @staticmethod
    def _reason(expected: str, exit_code: int, output: str) -> str:
        if expected == "pass":
            return "command exited 0" if exit_code == 0 else f"command exited {exit_code}"
        if expected == "fail":
            return "command failed as expected" if exit_code != 0 else f"command exited {exit_code} but failure expected"
        if exit_code != 0:
            return f"command exited {exit_code}"
        if re.search(expected, output, re.IGNORECASE):
            return f"output matched /{expected}/"
        return f"output did not match /{expected}/"

    @staticmethod
    def detect_project_type(project_dir: str | Path = ".") -> str:
        """Detect project type from manifest files present in the directory."""
        root = Path(project_dir)
        markers = {
            "python": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
            "rust": ["Cargo.toml"],
            "javascript": ["package.json"],
            "go": ["go.mod"],
        }
        for project_type, files in markers.items():
            if any((root / marker).exists() for marker in files):
                return project_type
        return "generic"

    def _record(self, result: VerificationResult) -> None:
        if self.history_path is None:
            return
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result.to_dict()) + "\n")

    def get_history(self, period_days: int = 30) -> list[dict]:
        """Load verification history within the given period (or all if 0)."""
        if self.history_path is None or not self.history_path.exists():
            return []
        cutoff = datetime.now() - timedelta(days=period_days)
        entries = []
        for line in self.history_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            try:
                ts = datetime.fromisoformat(entry.get("timestamp", ""))
            except ValueError:
                continue
            if period_days and ts < cutoff:
                continue
            entries.append(entry)
        return entries

    def compliance_report(self, period_days: int = 30) -> ComplianceReport:
        """Compute compliance metrics from recorded history."""
        entries = self.get_history(period_days)
        report = ComplianceReport(total=len(entries))
        if not entries:
            return report
        report.passed = sum(1 for e in entries if e.get("passed"))
        report.failed = report.total - report.passed
        report.passed_rate = round(report.passed / report.total, 3)
        report.false_completion_rate = round(report.failed / report.total, 3)
        durations = [e.get("duration", 0.0) for e in entries]
        report.avg_verification_time = round(sum(durations) / len(durations), 3)
        failure_names: dict[str, int] = {}
        for e in entries:
            if not e.get("passed"):
                failure_names[e.get("name", "unknown")] = failure_names.get(e.get("name", "unknown"), 0) + 1
        report.most_common_failures = sorted(failure_names, key=failure_names.get, reverse=True)[:5]
        report.emergency_overrides = sum(1 for e in entries if e.get("reason") == "emergency override")
        return report


class AgentVerifier:
    """Verifies that an agent's completion claim matches VCS reality."""

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir = Path(project_dir)

    def get_vcs_diff(self) -> list[str]:
        """Return changed/untracked file paths under the project dir (via git).

        ``git status --porcelain`` reports paths relative to the repo root, so
        they are relativized against ``self.project_dir``; paths outside the
        project directory are excluded.
        """
        git = shutil.which("git")
        if git is None:
            return []
        try:
            proc = subprocess.run(
                [git, "status", "--porcelain", "--untracked-files=all"],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=30,
            )
            root_proc = subprocess.run(
                [git, "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            return []
        if proc.returncode != 0:
            return []
        repo_root = Path(root_proc.stdout.strip()) if root_proc.returncode == 0 else self.project_dir.resolve()
        project_root = self.project_dir.resolve()
        changed = []
        for line in proc.stdout.splitlines():
            tokens = line.split()
            path = tokens[1] if len(tokens) > 1 else line
            candidate = Path(path) if Path(path).is_absolute() else repo_root / path
            try:
                rel = candidate.resolve().relative_to(project_root)
            except ValueError:
                continue
            if rel.as_posix() in (".", ""):
                continue
            changed.append(rel.as_posix())
        return changed

    @staticmethod
    def files_match(claimed_files: list[str], actual_diff: list[str]) -> bool:
        """Every claimed file must appear in the actual VCS diff."""
        claimed = {Path(f).as_posix() for f in claimed_files}
        actual = {Path(f).as_posix() for f in actual_diff}
        return claimed.issubset(actual)

    def verify_agent_task(self, task: str, claimed_files: list[str]) -> VerificationResult:
        """Check that claimed changes exist in the VCS diff for the given task."""
        timestamp = datetime.now().isoformat(timespec="seconds")
        actual_diff = self.get_vcs_diff()
        if not actual_diff:
            return VerificationResult(
                passed=False,
                name=f"agent:{task}",
                command="git status --porcelain",
                output="no VCS diff available; cannot confirm changes",
                exit_code=None,
                duration=0.0,
                timestamp=timestamp,
                reason="VCS diff doesn't match claimed changes",
            )
        if not self.files_match(claimed_files, actual_diff):
            missing = [f for f in claimed_files if Path(f).as_posix() not in {Path(a).as_posix() for a in actual_diff}]
            return VerificationResult(
                passed=False,
                name=f"agent:{task}",
                command="git status --porcelain",
                output=json.dumps({"claimed": claimed_files, "actual": actual_diff, "missing": missing}),
                exit_code=None,
                duration=0.0,
                timestamp=timestamp,
                reason="VCS diff doesn't match claimed changes",
            )
        return VerificationResult(
            passed=True,
            name=f"agent:{task}",
            command="git status --porcelain",
            output=json.dumps({"claimed": claimed_files, "actual": actual_diff}),
            exit_code=0,
            duration=0.0,
            timestamp=timestamp,
            reason="all claimed files present in VCS diff",
        )
