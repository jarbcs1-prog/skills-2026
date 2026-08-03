# Improvement Plan: writing-plans

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 289 | **Version:** 1.0 (implied)

### Strengths
- Clear bite-sized task granularity (2-5 min per task)
- Complete plan document structure with header and task templates
- TDD cycle integrated into every task
- Exact file paths, code examples, commands with expected output
- 6-step writing process with codebase exploration
- DRY/YAGNI/TDD/frequent commits principles
- Common mistakes with before/after examples
- Execution handoff to subagent-driven-development
- Review checklist before saving

### Gaps Identified
1. **No plan template library** - Single format only
2. **No automated plan generator** - Manual writing only
3. **No plan validation** - No quality checks on plans
4. **No integration with project-analyst** - Should auto-populate from analysis
4. **No plan versioning** - Plans can't evolve with code
5. **No plan execution tracking** - Can't track task completion
6. **No plan composition** - Can't combine plans
7. **No CLI tooling** - Manual only
8. **No cross-repo plan sharing** - Project-specific only
9. **No plan analytics** - No metrics on plan quality
10. **No plan-to-code traceability** - Can't link plan tasks to commits

---

## Improvement Roadmap

### Phase 1: Templates & Automation (Week 1)
- [x] Create plan template library (templates.py) (feature, bugfix, refactor, migration, API, UI)
- [x] Build plan scaffolding CLI (cli.py init command) (`plan init --template feature`)
- [x] Add plan validation (validator.py) (structure, completeness, TDD compliance)
- [x] Create plan-to-task extractor (extract-tasks, analytics) for subagent-driven-development

### Phase 2: Intelligence & Integration (Week 2)
- [ ] Integrate with `project-analyst` (future) (auto-populate from analysis)
- [ ] Add `project-planner` integration (future) (milestones → tasks)
- [x] Implement plan quality scoring (analytics.py) (completeness, specificity, TDD)
- [x] Create plan versioning (version command)

### Phase 3: Execution & Tracking (Week 3)
- [ ] Build plan execution tracker (future) (task status, time, blockers)
- [x] Add plan-to-commit traceability (traceability.py) (link tasks to git commits)
- [ ] Implement plan composition (future) (combine plans for larger features)
- [ ] Create plan analytics dashboard (future)

### Phase 4: Ecosystem (Week 4)
- [ ] Add plan sharing/registry (team plans)
- [ ] Integrate with CI/CD (plan gates before merge)
- [ ] Build plan-to-code sync (detect drift)
- [ ] Create plan coaching mode

---

## Specific Technical Tasks

### Plan Templates
```python
# templates.py
PLAN_TEMPLATES = {
    "feature": FeaturePlanTemplate,        # New feature implementation
    "bugfix": BugfixPlanTemplate,          # Bug fix with regression test
    "refactor": RefactorPlanTemplate,      # Code improvement
    "migration": MigrationPlanTemplate,    # Data/schema migration
    "api": APIPlanTemplate,                # REST/GraphQL endpoint
    "ui": UIPlanTemplate,                  # Frontend component/page
    "integration": IntegrationPlanTemplate, # External service integration
    "security": SecurityPlanTemplate,      # Security hardening
    "performance": PerformancePlanTemplate, # Optimization
    "deprecation": DeprecationPlanTemplate # Feature removal
}

class FeaturePlanTemplate:
    def generate(self, requirements: FeatureRequirements) -> Plan:
        return Plan(
            header=PlanHeader(
                name=requirements.name,
                goal=requirements.goal,
                architecture=requirements.architecture,
                tech_stack=requirements.tech_stack
            ),
            tasks=[
                # Setup tasks
                Task("setup", "Create feature branch", ["git checkout -b feature/x"]),
                Task("models", "Create data models", [
                    "Create: src/models/x.py",
                    "Test: tests/test_models.py"
                ]),
                Task("api", "Implement API endpoints", [
                    "Create: src/api/x.py",
                    "Test: tests/test_api.py"
                ]),
                # ... more tasks following TDD cycle
            ]
        )
```

### Plan Scaffolding CLI
```bash
# writing-plans init --template feature --name "user authentication" --output docs/plans/
# writing-plans init --template bugfix --issue "login fails with special chars"
# writing-plans validate --plan docs/plans/2026-08-01-auth.md --strict
# writing-plans extract-tasks --plan docs/plans/2026-08-01-auth.md --format subagent
# writing-plans compose --plans "auth.md,profile.md" --name "user-management"
# writing-plans version --plan docs/plans/auth.md --bump minor
# writing-plans track --plan docs/plans/auth.md --status
# writing-plans sync --plan docs/plans/auth.md --commits
```

### Plan Validator
```python
# validator.py
class PlanValidator:
    def validate(self, plan: Plan) -> ValidationResult:
        errors = []
        warnings = []
        
        # Structure validation
        errors += self.validate_header(plan.header)
        errors += self.validate_tasks(plan.tasks)
        
        # TDD compliance
        warnings += self.check_tdd_compliance(plan.tasks)
        
        # Granularity check
        warnings += self.check_task_granularity(plan.tasks)
        
        # Completeness
        warnings += self.check_completeness(plan)
        
        # Traceability
        warnings += self.check_traceability(plan)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=self.calculate_score(plan)
        )
    
    def check_tdd_compliance(self, tasks: List[Task]) -> List[str]:
        warnings = []
        for task in tasks:
            if task.produces_code and not task.has_tdd_cycle:
                warnings.append(f"Task {task.id}: produces code but missing TDD cycle")
            if task.has_test_step and not task.has_verify_fail_step:
                warnings.append(f"Task {task.id}: has test but missing 'verify failure' step")
        return warnings
    
    def check_task_granularity(self, tasks: List[Task]) -> List[str]:
        warnings = []
        for task in tasks:
            estimated_lines = task.estimate_lines_of_code()
            if estimated_lines > 50:
                warnings.append(f"Task {task.id}: too large (~{estimated_lines} lines), consider splitting")
            if len(task.files.create) > 3:
                warnings.append(f"Task {task.id}: creates {len(task.files.create)} files, consider splitting")
        return warnings
```

### Plan-to-Commit Traceability
```python
# traceability.py
class PlanTraceability:
    def link_tasks_to_commits(self, plan: Plan, repo: Repo) -> TraceabilityReport:
        links = []
        for task in plan.tasks:
            # Find commits that touch task files
            commits = self.find_commits_for_task(task, repo)
            
            # Check commit messages reference task
            task_refs = [c for c in commits if task.id in c.message]
            
            links.append(TaskCommitLink(
                task_id=task.id,
                commits=commits,
                referenced=len(task_refs),
                coverage=len(commits) > 0
            ))
        
        return TraceabilityReport(
            links=links,
            overall_coverage=sum(1 for l in links if l.coverage) / len(links),
            unlinked_tasks=[l.task_id for l in links if not l.coverage]
        )
    
    def detect_drift(self, plan: Plan, repo: Repo) -> DriftReport:
        # Compare plan tasks with actual implementation
        # Find: missing tasks, extra implementation, modified scope
        pass
```

### Plan Analytics
```python
# analytics.py
class PlanAnalytics:
    def analyze_plan_quality(self, plan: Plan) -> QualityReport:
        return QualityReport(
            task_count=len(plan.tasks),
            avg_task_size=self.avg_task_size(plan),
            tdd_compliance=self.tdd_compliance_rate(plan),
            granularity_score=self.granularity_score(plan),
            completeness_score=self.completeness_score(plan),
            traceability_score=self.traceability_score(plan),
            estimated_hours=self.estimate_hours(plan),
            risk_factors=self.identify_risks(plan)
        )
    
    def compare_plans(self, plans: List[Plan]) -> ComparisonReport:
        # Compare multiple plans for consistency, quality trends
        pass
```

---

## Acceptance Criteria
- [x] Templates available in templates.py
- [x] CLI creates valid plan
- [x] Validator catches plan issues
- [x] TDD compliance check implemented
- [x] Traceability links tasks to commits
- [ ] Plan composition (future)
- [ ] Analytics dashboard (future)
- [ ] Plan sync drift detection (future)

---

## Dependencies
- `project-analyst` (auto-population)
- `project-planner` (milestone integration)
- `subagent-driven-development` (task execution)
- `test-driven-development` (TDD enforcement)
- `code-quality` (CLI validation)
- `verification-before-completion` (plan quality claims)
- `writing-skills` (documentation standards)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Template rigidity | Medium | Low | Extensible, custom sections |
| Plan drift | High | Medium | Drift detection, sync command |
| Over-planning | Medium | Low | Granularity warnings, YAGNI reminders |
| Tool complexity | Medium | Low | Progressive disclosure, good defaults |

---

## Success Metrics
- Plan creation time: <5 min for standard features
- Task granularity: 90% tasks 2-5 min
- TDD compliance: >95% tasks with full cycle
- Traceability: >80% tasks linked to commits
- Plan quality score: avg >85/100
- Drift detection: <1 commit lag
- Team adoption: >70% of features use plans