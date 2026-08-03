"""Plan template generators for the writing-plans skill.

Each template scaffolds a plan with the correct header and a task skeleton
appropriate for the change type. Generated plans are valid by construction:
every code-producing task follows the TDD cycle (write failing test, verify
failure, implement, verify pass) and commits after each task.
"""
from __future__ import annotations

import re
from datetime import date

from .plans import Plan, PlanHeader, PlanStep, Task

TEMPLATE_NAMES = (
    "feature",
    "bugfix",
    "refactor",
    "migration",
    "api",
    "ui",
    "integration",
    "security",
    "performance",
    "deprecation",
)

_TEMPLATE_DESCRIPTIONS = {
    "feature": "New feature implementation",
    "bugfix": "Bug fix with regression test",
    "refactor": "Code improvement without behavior change",
    "migration": "Data/schema migration",
    "api": "REST/GraphQL endpoint",
    "ui": "Frontend component/page",
    "integration": "External service integration",
    "security": "Security hardening",
    "performance": "Optimization",
    "deprecation": "Feature removal",
}


def describe_templates() -> dict[str, str]:
    return dict(_TEMPLATE_DESCRIPTIONS)


def generate_plan(template: str, name: str, goal: str = "", tech_stack: str = "") -> Plan:
    """Generate a Plan from the named template."""
    if template not in _TEMPLATE_DESCRIPTIONS:
        raise ValueError(f"unknown template: {template} (choose from {', '.join(TEMPLATE_NAMES)})")
    slug = _slugify(name)
    return _GENERATORS[template](name=name, slug=slug, goal=goal, tech_stack=tech_stack)


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "plan"


def _tdd_task(number: int, title: str, objective: str, create: str, test: str, test_case: str) -> Task:
    """Build a TDD-compliant code-producing task."""
    task = Task(
        number=number,
        title=title,
        objective=objective,
        files={"create": [create], "test": [test]},
    )
    task.steps = [
        PlanStep(
            "1: Write failing test",
            f"Add a test to `{test}`:\n\n```python\ndef {test_case}():\n    # arrange / act / assert\n    assert True\n```",
        ),
        PlanStep(
            "2: Run test to verify failure",
            f"Run: `pytest {test}::{test_case} -v`\nExpected: FAIL - target not implemented yet.",
        ),
        PlanStep(
            "3: Write minimal implementation",
            f"Create `{create}` with the minimal code that satisfies the test.",
        ),
        PlanStep(
            "4: Run test to verify pass",
            f"Run: `pytest {test}::{test_case} -v`\nExpected: PASS.",
        ),
        PlanStep("5: Commit", "```bash\ngit add " + create + " " + test + '\ngit commit -m "feat: ' + title.lower() + '"\n```'),
    ]
    return task


def _generic_skeleton(
    name: str, slug: str, goal: str, tech_stack: str, architecture: str, tasks: list[Task], version: str = "0.1.0"
) -> Plan:
    header = PlanHeader(
        name=name,
        goal=goal or f"Implement {name.lower()}.",
        architecture=architecture,
        tech_stack=tech_stack or "To be determined.",
        version=version,
    )
    return Plan(header=header, tasks=tasks)


def _gen_feature(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        Task(
            number=1,
            title="Create the data model",
            objective=f"Define the core data structures backing {name.lower()}.",
            files={"create": [f"src/{slug}/models.py"], "test": [f"tests/test_{slug}_models.py"]},
            steps=[
                PlanStep("1: Write failing test", f"Add `tests/test_{slug}_models.py` asserting the model exists and has the expected fields."),
                PlanStep("2: Run test to verify failure", f"Run: `pytest tests/test_{slug}_models.py -v`\nExpected: FAIL - module not found."),
                PlanStep("3: Write minimal implementation", f"Create `src/{slug}/models.py` with the minimal model definitions."),
                PlanStep("4: Run test to verify pass", f"Run: `pytest tests/test_{slug}_models.py -v`\nExpected: PASS."),
                PlanStep("5: Commit", f"```bash\ngit add src/{slug}/models.py tests/test_{slug}_models.py\ngit commit -m \"feat: add {slug} models\"\n```"),
            ],
        ),
        _tdd_task(
            2,
            "Implement core logic",
            f"Implement the core behavior for {name.lower()}.",
            f"src/{slug}/core.py",
            f"tests/test_{slug}_core.py",
            f"test_{slug}_core_behavior",
        ),
        _tdd_task(
            3,
            "Wire up integration",
            "Connect the core logic to the rest of the application.",
            f"src/{slug}/integration.py",
            f"tests/test_{slug}_integration.py",
            f"test_{slug}_integration",
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal,
        tech_stack,
        f"Layered approach: {slug} models -> core -> integration, each layer TDD-driven.",
        tasks,
    )


def _gen_bugfix(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        Task(
            number=1,
            title="Reproduce the bug with a regression test",
            objective=f"Write a failing test that reproduces {name.lower()}.",
            files={"test": [f"tests/test_{slug}_regression.py"]},
            steps=[
                PlanStep("1: Write the regression test", f"Add `tests/test_{slug}_regression.py` that reproduces the reported symptom."),
                PlanStep("2: Run test to verify failure", f"Run: `pytest tests/test_{slug}_regression.py -v`\nExpected: FAIL - the bug reproduces."),
                PlanStep("3: Commit the failing test", f"```bash\ngit add tests/test_{slug}_regression.py\ngit commit -m \"test: reproduce {slug} bug\"\n```"),
            ],
        ),
        _tdd_task(
            2,
            "Fix the bug",
            "Implement the minimal fix so the regression test passes.",
            "src/fix_target.py",
            f"tests/test_{slug}_regression.py",
            f"test_{slug}_regression",
        ),
        Task(
            number=3,
            title="Run the full suite",
            objective="Confirm the fix does not break existing behavior.",
            steps=[
                PlanStep("1: Run the full test suite", "Run: `pytest tests/ -q`\nExpected: all pass, including the new regression test."),
                PlanStep("2: Commit the fix", f"```bash\ngit add src/ tests/\ngit commit -m \"fix: {slug}\"\n```"),
            ],
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Fix {name.lower()}.",
        tech_stack,
        "Regression-test first, then minimal fix, then full-suite confirmation.",
        tasks,
    )


def _gen_refactor(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        Task(
            number=1,
            title="Establish a safety net",
            objective="Ensure existing behavior is covered before refactoring.",
            files={"test": ["tests/test_coverage.py"]},
            steps=[
                PlanStep("1: Check existing coverage", "Run: `pytest tests/ -q`\nExpected: current suite green."),
                PlanStep("2: Add missing coverage", f"Add tests in `tests/test_coverage.py` for the code paths touched by {name.lower()}."),
                PlanStep("3: Commit the safety net", f"```bash\ngit add tests/\ngit commit -m \"test: safety net for {slug}\"\n```"),
            ],
        ),
        _tdd_task(
            2,
            "Refactor incrementally",
            f"Apply the refactor described by {name.lower()} without changing behavior.",
            "src/refactor_target.py",
            "tests/test_coverage.py",
            "test_refactor_target_unchanged",
        ),
        Task(
            number=3,
            title="Confirm behavior is unchanged",
            objective="Run the full suite after refactoring.",
            steps=[
                PlanStep("1: Run the full suite", "Run: `pytest tests/ -q`\nExpected: all green (no behavior change)."),
                PlanStep("2: Commit the refactor", f"```bash\ngit add src/\ngit commit -m \"refactor: {slug}\"\n```"),
            ],
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Refactor {name.lower()} while preserving behavior.",
        tech_stack,
        "Behavior-preserving refactor guarded by a test safety net.",
        tasks,
    )


def _gen_migration(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        Task(
            number=1,
            title="Write the schema migration",
            objective=f"Create the migration script for {name.lower()}.",
            files={"create": [f"migrations/{date.today().isoformat()}_{slug}.py"], "test": [f"tests/test_{slug}_migration.py"]},
            steps=[
                PlanStep("1: Write failing test", f"Add `tests/test_{slug}_migration.py` asserting the migration applies cleanly."),
                PlanStep("2: Run test to verify failure", f"Run: `pytest tests/test_{slug}_migration.py -v`\nExpected: FAIL - migration missing."),
                PlanStep("3: Write the migration", f"Create `migrations/{date.today().isoformat()}_{slug}.py` with up/down scripts."),
                PlanStep("4: Run test to verify pass", f"Run: `pytest tests/test_{slug}_migration.py -v`\nExpected: PASS."),
                PlanStep("5: Commit", f"```bash\ngit add migrations/ tests/\ngit commit -m \"migrate: {slug}\"\n```"),
            ],
        ),
        Task(
            number=2,
            title="Apply and verify on a staging copy",
            objective="Run the migration against a copy of production data.",
            steps=[
                PlanStep("1: Apply migration", "Run the migration against the staging database."),
                PlanStep("2: Verify data integrity", "Run integrity queries; expected: no data loss or orphaned rows."),
                PlanStep("3: Commit the verification notes", f"```bash\ngit add docs/\ngit commit -m \"docs: migration {slug} verified\"\n```"),
            ],
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Migrate {name.lower()}.",
        tech_stack,
        "Reversible migration with a verification step on a staging copy.",
        tasks,
    )


def _gen_api(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        _tdd_task(
            1,
            "Define the API contract",
            f"Create the endpoint stub and contract test for {name.lower()}.",
            f"src/api/{slug}.py",
            f"tests/test_api_{slug}.py",
            f"test_{slug}_endpoint",
        ),
        Task(
            number=2,
            title="Validate input and error cases",
            objective="Add validation and error handling for the endpoint.",
            files={"modify": [f"src/api/{slug}.py"], "test": [f"tests/test_api_{slug}.py"]},
            steps=[
                PlanStep("1: Write failing tests", f"Add tests to `tests/test_api_{slug}.py` for invalid input and 4xx responses."),
                PlanStep("2: Run test to verify failure", f"Run: `pytest tests/test_api_{slug}.py -v`\nExpected: FAIL - validation missing."),
                PlanStep("3: Implement validation", f"Add input validation and error responses to `src/api/{slug}.py`."),
                PlanStep("4: Run test to verify pass", f"Run: `pytest tests/test_api_{slug}.py -v`\nExpected: PASS."),
                PlanStep("5: Commit", f"```bash\ngit add src/api/{slug}.py tests/test_api_{slug}.py\ngit commit -m \"feat(api): {slug} validation\"\n```"),
            ],
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Add the {name.lower()} API endpoint.",
        tech_stack,
        "Contract-first endpoint with validation and explicit error responses.",
        tasks,
    )


def _gen_ui(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        _tdd_task(
            1,
            "Create the component shell",
            f"Build the initial {name.lower()} component with a render test.",
            f"src/components/{slug}.jsx",
            f"tests/test_{slug}.test.jsx",
            f"test_{slug}_renders",
        ),
        Task(
            number=2,
            title="Style and wire interactions",
            objective="Add styling and interactive behavior to the component.",
            files={"modify": [f"src/components/{slug}.jsx"], "test": [f"tests/test_{slug}.test.jsx"]},
            steps=[
                PlanStep("1: Write interaction tests", f"Extend `tests/test_{slug}.test.jsx` with click/input interaction assertions."),
                PlanStep("2: Run test to verify failure", f"Run: `npm test -- tests/test_{slug}.test.jsx`\nExpected: FAIL - interactions missing."),
                PlanStep("3: Implement interactions", f"Wire state and event handlers into `src/components/{slug}.jsx`."),
                PlanStep("4: Run test to verify pass", f"Run: `npm test -- tests/test_{slug}.test.jsx`\nExpected: PASS."),
                PlanStep("5: Commit", f"```bash\ngit add src/components/{slug}.jsx tests/\ngit commit -m \"feat(ui): {slug} interactions\"\n```"),
            ],
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Build the {name.lower()} UI component.",
        tech_stack,
        "Component shell first, then interactions, each verified by component tests.",
        tasks,
    )


def _gen_integration(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        Task(
            number=1,
            title="Stub the external service",
            objective=f"Create a contract-faithful stub for {name.lower()}.",
            files={"create": [f"src/integrations/{slug}_stub.py"], "test": [f"tests/test_{slug}_stub.py"]},
            steps=[
                PlanStep("1: Write failing test", f"Add `tests/test_{slug}_stub.py` asserting the stub matches the documented contract."),
                PlanStep("2: Run test to verify failure", f"Run: `pytest tests/test_{slug}_stub.py -v`\nExpected: FAIL - stub missing."),
                PlanStep("3: Implement the stub", f"Create `src/integrations/{slug}_stub.py` implementing the documented interface."),
                PlanStep("4: Run test to verify pass", f"Run: `pytest tests/test_{slug}_stub.py -v`\nExpected: PASS."),
                PlanStep("5: Commit", f"```bash\ngit add src/integrations/ tests/\ngit commit -m \"feat(integration): {slug} stub\"\n```"),
            ],
        ),
        _tdd_task(
            2,
            "Implement the real client",
            f"Replace the stub with the real {name.lower()} client.",
            f"src/integrations/{slug}_client.py",
            f"tests/test_{slug}_client.py",
            f"test_{slug}_client",
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Integrate with {name.lower()}.",
        tech_stack,
        "Contract-stub first, real client second, keeping tests independent of the network.",
        tasks,
    )


def _gen_security(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        _tdd_task(
            1,
            "Harden the attack surface",
            f"Apply the {name.lower()} hardening change.",
            "src/security_target.py",
            "tests/test_security.py",
            "test_security_hardening",
        ),
        Task(
            number=2,
            title="Run the security scanner",
            objective="Confirm no new vulnerabilities were introduced.",
            steps=[
                PlanStep("1: Run scanner", "Run: `ruff check . && bandit -r . -q`\nExpected: 0 errors."),
                PlanStep("2: Review the diff", "Confirm only intended files changed."),
                PlanStep("3: Commit", f"```bash\ngit add src/ tests/\ngit commit -m \"security: {slug}\"\n```"),
            ],
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Harden {name.lower()}.",
        tech_stack,
        "Targeted hardening with a regression test plus a scanner pass.",
        tasks,
    )


def _gen_performance(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        Task(
            number=1,
            title="Benchmark the baseline",
            objective=f"Capture the current performance of {name.lower()}.",
            files={"create": [f"bench/{slug}_bench.py"], "test": [f"tests/test_{slug}_perf.py"]},
            steps=[
                PlanStep("1: Write the benchmark", f"Create `bench/{slug}_bench.py` measuring the hot path."),
                PlanStep("2: Run and record baseline", "Run the benchmark and record the baseline numbers in the task."),
                PlanStep("3: Commit the baseline", f"```bash\ngit add bench/ tests/\ngit commit -m \"perf: {slug} baseline\"\n```"),
            ],
        ),
        _tdd_task(
            2,
            "Optimize the hot path",
            f"Implement the {name.lower()} optimization.",
            "src/perf_target.py",
            "tests/test_perf_target.py",
            "test_perf_target",
        ),
        Task(
            number=3,
            title="Confirm the improvement",
            objective="Re-run the benchmark and compare against baseline.",
            steps=[
                PlanStep("1: Re-run benchmark", "Run: `python bench/" + slug + "_bench.py`\nExpected: improvement over baseline."),
                PlanStep("2: Commit", f"```bash\ngit add src/ bench/\ngit commit -m \"perf: {slug}\"\n```"),
            ],
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Improve the performance of {name.lower()}.",
        tech_stack,
        "Measure first, optimize second, re-measure to confirm.",
        tasks,
    )


def _gen_deprecation(name: str, slug: str, goal: str, tech_stack: str) -> Plan:
    tasks = [
        Task(
            number=1,
            title="Mark as deprecated",
            objective=f"Deprecate {name.lower()} without removing it.",
            files={"modify": [f"src/{slug}.py"], "test": [f"tests/test_{slug}_deprecation.py"]},
            steps=[
                PlanStep("1: Write failing test", f"Add `tests/test_{slug}_deprecation.py` asserting a deprecation warning is emitted."),
                PlanStep("2: Run test to verify failure", f"Run: `pytest tests/test_{slug}_deprecation.py -v`\nExpected: FAIL - no warning."),
                PlanStep("3: Add the deprecation marker", f"Add a deprecation warning to `src/{slug}.py`."),
                PlanStep("4: Run test to verify pass", f"Run: `pytest tests/test_{slug}_deprecation.py -v`\nExpected: PASS."),
                PlanStep("5: Commit", f"```bash\ngit add src/ tests/\ngit commit -m \"deprecate: {slug}\"\n```"),
            ],
        ),
        Task(
            number=2,
            title="Update internal callers",
            objective="Point internal callers at the replacement.",
            steps=[
                PlanStep("1: Find callers", "Search the codebase for usages of the deprecated API."),
                PlanStep("2: Migrate callers", "Update each caller to the replacement API."),
                PlanStep("3: Run the suite", "Run: `pytest tests/ -q`\nExpected: all pass with no new deprecation warnings."),
                PlanStep("4: Commit", f"```bash\ngit add src/ tests/\ngit commit -m \"refactor: migrate off {slug}\"\n```"),
            ],
        ),
    ]
    return _generic_skeleton(
        name,
        slug,
        goal or f"Deprecate {name.lower()}.",
        tech_stack,
        "Deprecate with a warning first, then migrate callers, then (separately) remove.",
        tasks,
    )


_GENERATORS = {
    "feature": _gen_feature,
    "bugfix": _gen_bugfix,
    "refactor": _gen_refactor,
    "migration": _gen_migration,
    "api": _gen_api,
    "ui": _gen_ui,
    "integration": _gen_integration,
    "security": _gen_security,
    "performance": _gen_performance,
    "deprecation": _gen_deprecation,
}
