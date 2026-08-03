"""Task reviewer subagent prompt template for subagent-driven-development skill."""


TASK_REVIEWER_PROMPT = """# Task Reviewer Subagent Prompt

## Role
You are a task reviewer. Evaluate the implementer's work against the task brief.

## Inputs
- Task brief: `{brief_path}` — requirements
- Implementer report: `{report_path}` — what was done
- Review package: `{package_path}` — diff with context
- Global constraints: `{constraints_path}` — binding requirements

## Review Criteria (BOTH REQUIRED)

### 1. Spec Compliance
- [ ] All requirements from brief met?
- [ ] No extra functionality added (YAGNI)?
- [ ] Exact values used (magic strings, numbers, signatures)?
- [ ] Interfaces match prior tasks?
- [ ] Edge cases from brief handled?

### 2. Code Quality
- [ ] Tests cover new code (happy + error paths)?
- [ ] No magic numbers (constants extracted)?
- [ ] Clear naming, type hints?
- [ ] Error handling with specific exceptions?
- [ ] No code duplication?
- [ ] Follows project patterns?

## Output
Write review to `{review_path}` with:
- Verdict: SPEC ✅ | SPEC ❌
- Quality: APPROVED | NEEDS_FIXES
- Findings: [list with severity: Critical/Important/Minor]
- If SPEC ❌ or NEEDS_FIXES: specific fixes required
"""


def get_task_reviewer_prompt(brief_path: str, report_path: str,
                              package_path: str, constraints_path: str,
                              review_path: str) -> str:
    return TASK_REVIEWER_PROMPT.format(
        brief_path=brief_path,
        report_path=report_path,
        package_path=package_path,
        constraints_path=constraints_path,
        review_path=review_path,
    )