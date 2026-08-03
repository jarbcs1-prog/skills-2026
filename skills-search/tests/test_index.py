"""Unit tests for the skills-search indexing module using a temp fake registry."""
from __future__ import annotations

from pathlib import Path

from scripts.skill_index import (
    compose,
    index_local_skills,
    resolve_dependencies,
    search_skills,
    tokenize,
    trigram_jaccard,
    verify,
)


def write_skill(
    root: Path,
    name: str,
    description: str,
    version: str = "1.0.0",
    dependencies: str = "",
    has_tests: bool = True,
    workflow: bool = True,
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    lines = ["---", f"name: {name}", f"description: {description}", f"version: {version}"]
    if dependencies:
        lines.append(f"dependencies: {dependencies}")
    lines.extend(["---", "", f"# {name}"])
    if workflow:
        lines.extend(["", "## Workflow", "", "1. First step", "2. Second step"])
    if has_tests:
        (skill_dir / "tests").mkdir()
    (skill_dir / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return skill_dir


def test_index_local_skills_finds_fake_skills(tmp_path: Path) -> None:
    write_skill(tmp_path, "alpha-skill", "Alpha handles data")
    write_skill(tmp_path, "beta-skill", "Beta handles automation")
    skills = index_local_skills(tmp_path)
    assert len(skills) == 2
    assert [skill.name for skill in skills] == ["alpha-skill", "beta-skill"]


def test_frontmatter_parsing_extracts_fields(tmp_path: Path) -> None:
    write_skill(tmp_path, "meta-skill", "Extracts metadata", version="2.1.0")
    skill = index_local_skills(tmp_path)[0]
    assert skill.name == "meta-skill"
    assert skill.description == "Extracts metadata"
    assert skill.version == "2.1.0"
    assert skill.has_tests is True


def test_search_ranks_name_match_above_description_match(tmp_path: Path) -> None:
    write_skill(tmp_path, "database-tool", "handles queries")
    write_skill(tmp_path, "other-skill", "a database-tool for storage")
    results = search_skills("database-tool", index_local_skills(tmp_path))
    assert results[0]["name"] == "database-tool"
    assert results[0]["score"] >= results[1]["score"]


def test_verify_complete_skill_is_valid(tmp_path: Path) -> None:
    write_skill(tmp_path, "complete-skill", "Fully formed skill", has_tests=True)
    skill = index_local_skills(tmp_path)[0]
    report = verify(skill)
    assert report["valid"] is True
    assert all(report["checks"].values())
    assert report["errors"] == []


def test_verify_partial_skill_is_invalid(tmp_path: Path) -> None:
    write_skill(tmp_path, "partial-skill", "Missing tests", has_tests=False)
    skill = index_local_skills(tmp_path)[0]
    report = verify(skill)
    assert report["valid"] is False
    assert report["checks"]["tests"] is False


def test_resolve_dependencies_keeps_existing_only(tmp_path: Path) -> None:
    write_skill(tmp_path, "base-skill", "Base capability")
    write_skill(tmp_path, "child-skill", "Depends on base", dependencies="base-skill,ghost-skill")
    skills = index_local_skills(tmp_path)
    child = next(skill for skill in skills if skill.name == "child-skill")
    assert resolve_dependencies(child, skills) == ["base-skill"]


def test_compose_merges_workflow_steps(tmp_path: Path) -> None:
    write_skill(tmp_path, "first-skill", "First", workflow=True)
    write_skill(tmp_path, "second-skill", "Second", workflow=True)
    result = compose(["first-skill", "second-skill"], index_local_skills(tmp_path))
    assert result["skills"] == ["first-skill", "second-skill"]
    assert result["conflicts"] == []
    assert result["composed"]["workflow"] == ["First step", "Second step", "First step", "Second step"]


def test_tokenize_and_trigram_jaccard() -> None:
    assert tokenize("React Performance") == ["react", "performance"]
    assert trigram_jaccard("testing", "testing-tools") > 0
    assert trigram_jaccard("", "") == 0.0
