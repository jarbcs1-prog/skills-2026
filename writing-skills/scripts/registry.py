#!/usr/bin/env python3
"""Skill registry and versioning for the writing-skills skill.

A registry is a local directory layout:

    <registry>/
      index.json                      # {name: {version: path}}
      <name>/
        <version>/
          SKILL.md, skill.yaml, ...   # packaged copy of the skill

Publishing validates a skill, copies it under the registry and updates the
index. Installing resolves a `name@version` spec (or a bare name for the
latest version), copies it out and runs post-install validation.
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .scaffolder import SkillMetadata, validate_name

_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)([-+].*)?$")


def parse_version(version: str) -> tuple[int, int, int]:
    match = _SEMVER_RE.match(version.strip())
    if not match:
        raise ValueError(f"Invalid semantic version: {version!r} (expected MAJOR.MINOR.PATCH)")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(version: str, kind: str) -> str:
    major, minor, patch = parse_version(version)
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def compare_versions(a: str, b: str) -> int:
    """Return -1, 0 or 1 comparing two semver strings."""
    va, vb = parse_version(a), parse_version(b)
    return (va > vb) - (va < vb)


@dataclass
class PublishResult:
    name: str
    version: str
    path: Path
    published: bool
    message: str

    def summary(self) -> str:
        status = "published" if self.published else "NOT published"
        return f"{self.name}@{self.version} {status}: {self.message}"


@dataclass
class InstallResult:
    name: str
    version: str
    target: Path
    installed: bool
    message: str

    def summary(self) -> str:
        status = "installed" if self.installed else "NOT installed"
        return f"{self.name}@{self.version} {status}: {self.message}"


class SkillRegistry:
    """Local registry with publish/install/upgrade and dependency resolution."""

    def __init__(self, registry_dir: Path) -> None:
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.registry_dir / "index.json"
        self._index: dict[str, dict[str, str]] = self._load_index()

    def _load_index(self) -> dict[str, dict[str, str]]:
        if not self.index_path.exists():
            return {}
        try:
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_index(self) -> None:
        self.index_path.write_text(
            json.dumps(self._index, indent=2, sort_keys=True), encoding="utf-8"
        )

    # -- publishing ---------------------------------------------------------

    def publish(self, skill_path: Path, version: Optional[str] = None) -> PublishResult:
        skill_path = Path(skill_path).resolve()
        if not (skill_path / "SKILL.md").exists():
            return PublishResult(
                skill_path.name, version or "", skill_path, False,
                "SKILL.md not found - nothing to publish",
            )
        metadata = self._read_manifest(skill_path)
        version = version or metadata.version or "1.0.0"
        try:
            parse_version(version)
        except ValueError as exc:
            return PublishResult(metadata.name, version, skill_path, False, str(exc))

        existing = self._index.get(metadata.name, {})
        if version in existing:
            return PublishResult(
                metadata.name, version, skill_path, False,
                f"version {version} already published for {metadata.name}",
            )

        dest = self.registry_dir / metadata.name / version
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(skill_path, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self._stamp_version(dest, version)
        self._index.setdefault(metadata.name, {})[version] = str(skill_path)
        self._save_index()
        return PublishResult(metadata.name, version, dest, True, f"copied to {dest}")

    # -- installation -------------------------------------------------------

    def resolve(self, spec: str) -> tuple[str, str]:
        """Resolve 'name@version' or 'name' to (name, version)."""
        spec = spec.strip()
        if "@" in spec:
            name, version = spec.rsplit("@", 1)
        else:
            name, version = spec, "latest"
        validate_name(name)
        return name, version

    def available_versions(self, name: str) -> list[str]:
        versions = list(self._index.get(name, {}).keys())
        versions.sort(key=parse_version)
        return versions

    def install(self, spec: str, target_dir: Path) -> InstallResult:
        name, version = self.resolve(spec)
        versions = self.available_versions(name)
        if not versions:
            return InstallResult(name, version, target_dir, False,
                                 f"{name} not found in registry {self.registry_dir}")
        if version == "latest":
            version = versions[-1]
        elif version not in versions:
            return InstallResult(name, version, target_dir, False,
                                 f"{name}@{version} not found (available: {', '.join(versions)})")
        source = self.registry_dir / name / version
        if not source.exists():
            return InstallResult(name, version, target_dir, False, f"registry entry missing at {source}")

        dest = Path(target_dir) / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

        if not (dest / "SKILL.md").exists():
            return InstallResult(name, version, dest, False, "installed skill missing SKILL.md")
        return InstallResult(name, version, dest, True, f"installed to {dest}")

    def upgrade(self, name: str, version: str, target_dir: Path) -> InstallResult:
        versions = self.available_versions(name)
        if not versions:
            return InstallResult(name, version, target_dir, False,
                                 f"{name} not found in registry {self.registry_dir}")
        try:
            parse_version(version)
        except ValueError as exc:
            return InstallResult(name, version, target_dir, False, str(exc))
        current = self._current_version(Path(target_dir) / name)
        if current is not None and compare_versions(version, current) < 0:
            return InstallResult(name, version, Path(target_dir) / name, False,
                                 f"downgrade {current} -> {version} refused")
        return self.install(f"{name}@{version}", target_dir)

    @staticmethod
    def _stamp_version(dest: Path, version: str) -> None:
        """Rewrite the published manifest's version so the registry copy is self-consistent."""
        manifest = dest / "skill.yaml"
        if manifest.exists():
            lines = []
            stamped = False
            for line in manifest.read_text(encoding="utf-8").splitlines():
                if line.startswith("version:"):
                    lines.append(f"version: {version}")
                    stamped = True
                else:
                    lines.append(line)
            if not stamped:
                lines.append(f"version: {version}")
            manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            manifest.write_text(f"name: {dest.parent.name}\nversion: {version}\n", encoding="utf-8")

    @staticmethod
    def _current_version(skill_dir: Path) -> Optional[str]:
        manifest = skill_dir / "skill.yaml"
        if not manifest.exists():
            return None
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line.startswith("version:"):
                return line.split(":", 1)[1].strip()
        return None

    # -- dependency resolution ----------------------------------------------

    def resolve_dependencies(self, skill_path: Path) -> list[str]:
        """Return dependencies in install order (leaf-first). Detects cycles."""
        visited: set[str] = set()
        visiting: set[str] = set()
        order: list[str] = []
        cycle: list[str] = []

        def visit(name: str, from_dir: Path) -> None:
            if name in visiting:
                cycle.append(name)
                return
            if name in visited:
                return
            visiting.add(name)
            meta = self._read_manifest(from_dir)
            for dep in meta.dependencies:
                dep_dir = self._locate_dependency(dep)
                if dep_dir is not None:
                    visit(dep, dep_dir)
                else:
                    # Unresolvable dependency still needs to be reported; treat
                    # it as an external install-required item.
                    order.append(dep)
            visiting.discard(name)
            if name not in order:
                order.append(name)
            visited.add(name)

        meta = self._read_manifest(Path(skill_path))
        for dep in meta.dependencies:
            dep_dir = self._locate_dependency(dep)
            if dep_dir is not None:
                visit(dep, dep_dir)
        for name in meta.dependencies:
            if name not in order:
                order.append(name)
        if cycle:
            raise ValueError(f"Dependency cycle detected involving: {cycle}")
        return order

    def _locate_dependency(self, name: str) -> Optional[Path]:
        versions = self.available_versions(name)
        if not versions:
            return None
        return self.registry_dir / name / versions[-1]

    def _read_manifest(self, skill_path: Path) -> SkillMetadata:
        manifest = Path(skill_path) / "skill.yaml"
        if not manifest.exists():
            return SkillMetadata(name=Path(skill_path).name, template="")
        return SkillMetadata.from_dict(self._parse_manifest(manifest))

    @staticmethod
    def _parse_manifest(manifest: Path) -> dict:
        data: dict = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if ":" not in line or line.lstrip().startswith("#"):
                continue
            key, _, value = line.partition(":")
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                value = json.loads(value) if value.strip() != "[]" else []
            data[key.strip()] = value
        return data
