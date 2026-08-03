# Improvement Plan: project-planner

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 297 | **Version:** 1.0 (implied)

### Strengths
- Comprehensive 6-step planning process
- Detailed task sizing guidelines (XS to XL)
- Multiple estimation techniques (three-point, t-shirt, planning poker)
- Complete output format with milestones, phases, dependencies, risks, resources
- Full worked example (website redesign)
- Visual dependency mapping
- Risk mitigation table
- Resource allocation with weekly hours
- Success metrics defined

### Gaps Identified
1. **No automation** - Manual planning only
2. **No template library** - Only one example
3. **No integration with project-analyst** - Should auto-detect from analysis
4. **No CLI tooling** - No project-planner CLI
5. **No project tracking** - Plan creation only, no execution monitoring
6. **No dependency visualization tool** - ASCII only
7. **No resource leveling** - Overallocation detection
8. **No critical path calculation** - Manual only
9. **No Monte Carlo simulation** - For probabilistic estimates
10. **No export formats** - Markdown only

---

## Improvement Roadmap

### Phase 1: Automation & Templates (Week 1)
- [ ] Create project template library (10+ project types)
- [ ] Build CLI for plan generation
- [ ] Add `project-analyst` integration (auto-populate from analysis)
- [ ] Implement critical path calculation

### Phase 2: Advanced Planning (Week 2)
- [ ] Add resource leveling (overallocation detection)
- [ ] Implement Monte Carlo simulation for estimates
- [ ] Add dependency graph visualization (Mermaid, GraphViz)
- [ ] Create milestone tracking with progress

### Phase 3: Execution Tracking (Week 3)
- [ ] Add plan execution mode (mark tasks complete, track progress)
- [ ] Implement burndown/burnup charts
- [ ] Add variance analysis (planned vs actual)
- [ ] Create replanning workflow (when things change)

### Phase 4: Integration & Export (Week 4)
- [ ] Export to project management tools (GitHub Projects, Jira, Linear, Notion)
- [ ] Add CI/CD integration (milestone gates)
- [ ] Create plan health dashboard
- [ ] Add team collaboration features

---

## Specific Technical Tasks

### Template Library
```python
# templates.py
TEMPLATES = {
    "web_app": "Web Application",
    "mobile_app": "Mobile App (React Native/Flutter)",
    "api_service": "REST/GraphQL API Service",
    "cli_tool": "CLI Tool",
    "library": "Library/Package",
    "data_pipeline": "Data Pipeline/ETL",
    "ml_project": "Machine Learning Project",
    "migration": "System Migration",
    "refactor": "Large Refactoring",
    "security_audit": "Security Audit & Hardening"
}

def get_template(name: str) -> ProjectTemplate:
    # Returns pre-populated plan with phases, tasks, estimates
    # Based on industry best practices for each type
    pass
```

### Critical Path Calculation
```python
# scheduling.py
class CriticalPathCalculator:
    def calculate(self, tasks: List[Task], dependencies: List[Dependency]) -> ScheduleResult:
        # 1. Build dependency graph
        # 2. Forward pass (earliest start/finish)
        # 3. Backward pass (latest start/finish)
        # 4. Calculate float/slack
        # 5. Identify critical path (zero float)
        # 6. Return schedule with critical path highlighted
        pass

class ResourceLeveler:
    def level(self, schedule: ScheduleResult, resources: List[Resource]) -> LeveledSchedule:
        # Detect overallocation
        # Apply leveling heuristics (delay non-critical, split tasks)
        # Return adjusted schedule
        pass
```

### Monte Carlo Simulation
```python
# estimation.py
class MonteCarloEstimator:
    def simulate(self, tasks: List[Task], iterations: int = 10000) -> EstimateDistribution:
        # For each task, sample from distribution (triangular: optimistic, likely, pessimistic)
        # Run simulation
        # Return: P50, P80, P90, P95 completion dates
        # Identify tasks with highest variance contribution
        pass
```

### CLI Design
```bash
# project-planner init --template web_app --name "My Project"
# project-planner generate --analysis analysis.json --output plan.md
# project-planner schedule --plan plan.md --calculate-critical-path
# project-planner track --plan plan.md --update "task-id:done"
# project-planner report --plan plan.md --format burndown --output chart.png
# project-planner export --plan plan.md --format github-projects
# project-planner replan --plan plan.md --changes changes.json
```

### Progress Tracking
```python
# tracker.py
class PlanTracker:
    def update_progress(self, plan: ProjectPlan, updates: List[TaskUpdate]) -> ProjectPlan:
        # Mark tasks complete/in-progress
        # Recalculate schedule
        # Identify new critical path
        # Detect delays
        pass
    
    def generate_burndown(self, plan: ProjectPlan) -> BurndownData:
        # Daily remaining effort
        # Ideal vs actual
        # Projected completion
        pass
    
    def variance_analysis(self, plan: ProjectPlan) -> VarianceReport:
        # Planned vs actual per task
        # Cumulative variance
        # Root cause categories
        pass
```

---

## Acceptance Criteria
- [ ] 10+ templates covering common project types
- [ ] Critical path calculated in <100ms for 100 tasks
- [ ] Resource leveling resolves >80% of overallocations
- [ ] Monte Carlo P80 estimate within 15% of actual
- [ ] CLI generates plan in <30s
- [ ] Export works for 4+ PM tools
- [ ] Burndown chart updates in real-time
- [ ] Replanning preserves completed work

---

## Dependencies
- `project-analyst` (auto-population from analysis)
- `writing-plans` (implementation plan generation - next step)
- `code-quality` (CLI code)
- `verification-before-completion` (estimate claims)
- `docs-write` (plan documentation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Template rigidity | Medium | Low | Customizable, extensible templates |
| Estimation accuracy | High | High | Monte Carlo, historical calibration |
| Tool lock-in | Low | Medium | Multiple export formats |
| Plan drift | High | High | Regular replanning, variance alerts |

---

## Success Metrics
- Plan creation time: <10 min for standard projects
- Estimate accuracy (P80): within 20%
- Critical path accuracy: >90% matches reality
- Template adoption: >80% of plans use templates
- Export success: 100% for supported tools