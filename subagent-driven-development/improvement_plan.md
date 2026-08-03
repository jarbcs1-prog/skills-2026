# Improvement Plan: subagent-driven-development

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 316 | **Version:** 1.0 (implied)

### Strengths
- Complete subagent orchestration process (implementer → task reviewer → fix → final review)
- Clear decision graph for when to use
- Model selection guidance (cost/speed/quality tradeoffs)
- 4 implementer statuses with handling procedures
- Detailed reviewer prompt construction rules
- File handoff system (brief, report, reviewer inputs)
- Durable progress ledger (survives compaction)
- 3 prompt templates referenced
- Comprehensive example workflow
- Integration with required workflow skills
- Red flags section with 20+ specific prohibitions

### Gaps Identified
1. **Missing prompt templates** - implementer-prompt.md, task-reviewer-prompt.md referenced but not present
2. **Missing scripts** - task-brief, review-package scripts referenced but not present
3. **No automated orchestration** - Manual dispatch only
4. **No parallel task support** - Sequential only (by design but could be optional)
5. **No cost tracking** - No token/cost budget per task
6. **No quality metrics** - No measurement of review effectiveness
7. **No integration with CI/CD** - Session-only, no pipeline
8. **No task estimation** - No effort tracking vs actual
8. **No conflict detection** - Pre-flight only scans plan, not runtime
9. **No skill marketplace** - Tied to specific superpowers skills

---

## Improvement Roadmap

### Phase 1: Core Assets (Week 1)
- [ ] Create `implementer-prompt.md` template
- [ ] Create `task-reviewer-prompt.md` template
- [ ] Build `scripts/task-brief.py` and `scripts/review-package.py`
- [ ] Add `scripts/review-package` for final whole-branch review

### Phase 2: Automation (Week 2)
- [ ] Create orchestrator CLI (`sdd` command)
- [ ] Add parallel task support (independent tasks)
- [ ] Implement cost tracking per task/model
- [ ] Add task estimation vs actual tracking

### Phase 3: Quality & Integration (Week 3)
- [ ] Integrate `code-reviewer` for task reviews
- [ ] Add `test-driven-development` enforcement
- [ ] Create CI/CD pipeline integration
- [ ] Add conflict detection at runtime

### Phase 4: Ecosystem (Week 4)
- [ ] Build progress dashboard
- [ ] Add skill marketplace for prompt templates
- [ ] Implement task reuse (common patterns)
- [ ] Create onboarding tutorial

---

## Specific Technical Tasks

### Implementer Prompt Template
```markdown
# scripts/implementer-prompt.md
# Implementer Subagent Prompt

## Role
You are an implementer subagent. Your job is to implement ONE task from a plan, following TDD.

## Inputs
- Read the task brief: `{brief_path}` — this is your complete requirements
- Global constraints: `{constraints_path}` — binding requirements from the plan
- Interfaces from prior tasks: `{interfaces_path}` — exact signatures to match

## Process
1. **Read brief completely** — understand exact values, magic strings, test cases
2. **Ask questions** — if ANY ambiguity, ask before implementing
3. **Write failing test first** (RED) — use `test-driven-development` skill
4. **Implement minimal fix** (GREEN) — address root cause only
5. **Run tests** — ensure all pass
6. **Self-review** — check spec compliance, code quality, YAGNI
7. **Commit** — atomic commit with descriptive message
8. **Write report** to `{report_path}` with:
   - Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
   - Commits: `<base>..<head>`
   - Test summary: `X/Y passing`
   - Concerns: [if any]

## Constraints
- NEVER read the full plan — only your task brief
- NEVER make assumptions — ask questions
- NEVER skip tests — TDD is mandatory
- NEVER bundle refactoring with fixes
- ALWAYS use exact values from brief
- ALWAYS write report to specified path
```

### Task Reviewer Prompt Template
```markdown
# scripts/task-reviewer-prompt.md
# Task Reviewer Subagent Prompt

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
```

### Task Brief Script
```python
# scripts/task-brief.py
#!/usr/bin/env python3
"""
Extract task N from plan file to a brief file.
Usage: task-brief PLAN_FILE N
"""

import sys
import re
from pathlib import Path

def extract_task(plan_file: Path, task_num: int) -> str:
    content = plan_file.read_text()
    # Find "## Task N:" or "## Phase N:" section
    # Extract until next "## Task" or "## Phase" or EOF
    pattern = rf"(## (?:Task|Phase) {task_num}:.*?)(?=## (?:Task|Phase) \d+|$)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        raise ValueError(f"Task {task_num} not found in {plan_file}")
    return match.group(1).strip()

if __name__ == "__main__":
    plan_file = Path(sys.argv[1])
    task_num = int(sys.argv[2])
    brief = extract_task(plan_file, task_num)
    
    output = Path(f"sdd/task-{task_num}-brief.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(brief)
    print(output)
```

### Review Package Script
```python
# scripts/review-package.py
#!/usr/bin/env python3
"""
Generate review package for task or final review.
Usage: review-package BASE HEAD
"""

import subprocess
import sys
from pathlib import Path

def generate_package(base: str, head: str) -> Path:
    # Git log (oneline)
    log = subprocess.run(["git", "log", "--oneline", f"{base}..{head}"],
                        capture_output=True, text=True).stdout
    
    # Git diff stat
    stat = subprocess.run(["git", "diff", "--stat", f"{base}..{head}"],
                         capture_output=True, text=True).stdout
    
    # Git diff with context (U10)
    diff = subprocess.run(["git", "diff", "-U10", f"{base}..{head}"],
                         capture_output=True, text=True).stdout
    
    package = f"""# Review Package: {base}..{head}

## Commits
{log}

## Stat Summary
{stat}

## Full Diff
```diff
{diff}
```
"""
    output = Path(f"sdd/review-{base[:7]}-{head[:7]}.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(package)
    print(output)
    return output

if __name__ == "__main__":
    base = sys.argv[1]
    head = sys.argv[2]
    generate_package(base, head)
```

### Orchestrator CLI
```bash
# sdd execute --plan plan.md --parallel 2
# sdd execute --plan plan.md --cost-budget 100000
# sdd status --ledger sdd/progress.md
# sdd resume --plan plan.md --ledger sdd/progress.md
# sdd review --final --merge-base main
```

---

## Acceptance Criteria
- [ ] All 4 prompt templates/scripts created and tested
- [ ] Orchestrator executes full plan with <5% manual intervention
- [ ] Parallel execution works for independent tasks
- [ ] Cost tracking accurate within 10%
- [ ] Ledger survives compaction/resume
- [ ] Review package includes all required context
- [ ] Integration with code-reviewer works

---

## Dependencies
- `writing-plans` (plan creation)
- `requesting-code-review` (final review template)
- `test-driven-development` (TDD enforcement)
- `code-quality` (script validation)
- `verification-before-completion` (quality claims)
- `systematic-debugging` (when blockers occur)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Subagent context loss | Medium | High | File handoffs, ledger persistence |
| Review loop infinite | Low | High | Max 3 review cycles, then escalate |
| Cost overrun | Medium | High | Budget enforcement, model selection |
| Plan drift | Medium | High | Pre-flight scan, runtime conflict detection |

---

## Success Metrics
- Task completion rate: >95% first-pass spec compliance
- Review cycles per task: <1.5 average
- Cost per task: within 20% of estimate
- Ledger recovery: 100% after compaction
- Time to execute 10-task plan: <2 hours