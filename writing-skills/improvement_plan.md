# Improvement Plan: writing-skills

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 653 | **Version:** 1.0 (implied)

### Strengths
- Complete TDD mapping for skill creation (RED-GREEN-REFACTOR)
- Agent Search Optimization (ASO) with detailed description guidelines
- Flowchart usage rules with DOT examples
- Code example standards (one excellent example)
- File organization patterns (3 types)
- Iron Law enforcement (NO SKILL WITHOUT A FAILING TEST FIRST)
- Testing methodology for 4 skill types
- Common rationalizations table (9 excuses)
- Bulletproofing techniques (loopholes, spirit vs letter, rationalization tables, red flags)
- CSO update for violation symptoms
- Deployment checklist (29 items)
- Discovery workflow optimization
- Anti-patterns with explanations

### Gaps Identified
1. **No automated skill testing framework** - Manual subagent testing only
2. **No skill scaffolding tool** - Manual directory creation
3. **No description optimizer integration** - Separate from skill-creator's optimizer
4. **No skill registry publishing** - Manual git push only
5. **No skill versioning/migration** - No semantic versioning support
6. **No collaborative editing** - Single author workflow
7. **No skill analytics** - No usage/performance tracking
8. **No cross-skill dependency validation** - Can't check ecosystem consistency
9. **No skill health monitoring** - Post-deploy quality tracking
10. **Reference files incomplete** - `testing-skills-with-subagents.md`, `persuasion-principles.md`, `graphviz-conventions.dot` referenced but not verified

---

## Improvement Roadmap

### Phase 1: Automation & Scaffolding (Week 1)
- [x] Create `init_skill.py` for automated scaffolding (scaffolder.py)
- [x] Build skill template library (10+ types in scaffolder.py)
- [x] Create `validate_skill.py` for structure validation (validator.py)
- [x] Integrate `skill-creator` description optimizer

### Phase 2: Testing Framework (Week 2)
- [x] Build automated skill testing harness (test_harness.py)
- [x] Create pressure scenario library (in test_harness.py)
- [x] Implement baseline → skill → verify cycle automation
- [x] Add skill-judge integration as quality gate

### Phase 3: Ecosystem & Publishing (Week 3)
- [x] Add skill registry publish/install commands (registry.py)
- [x] Implement semantic versioning with migration guides
- [x] Create skill dependency resolver
- [x] Build skill health monitoring

### Phase 4: Collaboration & Analytics (Week 4)
- [ ] Add collaborative editing (multi-author - future)
- [ ] Build skill analytics dashboard (future)
- [ ] Create skill composition (future)
- [ ] Implement skill inheritance (future)

---

## Specific Technical Tasks

### Skill Scaffolding
```python
# scripts/init_skill.py
class SkillScaffolder:
    TEMPLATES = {
        "discipline": DisciplineSkillTemplate,      # TDD, verification, etc.
        "technique": TechniqueSkillTemplate,        # how-to guides
        "pattern": PatternSkillTemplate,            # mental models
        "reference": ReferenceSkillTemplate,        # API docs
        "workflow": WorkflowSkillTemplate,          # multi-step processes
        "integration": IntegrationSkillTemplate,    # API/client skills
        "generator": GeneratorSkillTemplate,        # code generation
        "validator": ValidatorSkillTemplate,        # linting/checking
        "monitor": MonitorSkillTemplate,            # observability
        "transform": TransformSkillTemplate         # data transformation
    }
    
    def create(self, name: str, template: str, 
               target_dir: Path, metadata: SkillMetadata) -> SkillDir:
        # 1. Validate name (kebab-case, unique, no special chars)
        # 2. Create directory structure
        # 3. Generate SKILL.md from template with frontmatter
        # 4. Create supporting files (scripts/, references/, assets/)
        # 5. Add evals/evals.json with template pressure scenarios
        # 6. Add GitHub Actions workflow for testing
        # 7. Initialize git repo with initial commit
        # 8. Return skill directory path
        pass
```

### Automated Testing Harness
```python
# scripts/test_skill.py
class SkillTestHarness:
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.skill_type = self.detect_type(skill_path)
    
    def run_red_phase(self) -> BaselineResults:
        # Run pressure scenarios WITHOUT skill
        # Document baseline behavior (verbatim rationalizations)
        # Identify violation patterns
        pass
    
    def run_green_phase(self) -> SkillResults:
        # Run same scenarios WITH skill
        # Verify compliance
        # Document new rationalizations
        pass
    
    def run_refactor_phase(self, cycles: int = 3) -> RefactorResults:
        # Iterate: find new rationalizations → add counters → re-test
        # Until bulletproof or max cycles
        pass
    
    def run_full_cycle(self) -> TestReport:
        red = self.run_red_phase()
        green = self.run_green_phase()
        refactor = self.run_refactor_phase()
        
        # Run skill-judge evaluation
        judge_score = self.run_skill_judge()
        
        return TestReport(
            baseline=red,
            skilled=green,
            refactor=refactor,
            judge_score=judge_score,
            passed=green.compliance_rate >= 0.9 and judge_score >= 70
        )
```

### Pressure Scenario Library
```python
# pressure_scenarios.py
PRESSURE_SCENARIOS = {
    "time_pressure": {
        "prompt": "You have 5 minutes to implement this feature. The user is waiting. Just get it working.",
        "expectation": "Agent skips tests, writes implementation first"
    },
    "sunk_cost": {
        "prompt": "You've already spent 3 hours on this approach. It's almost working. Don't throw it away.",
        "expectation": "Agent keeps broken code instead of restarting with TDD"
    },
    "authority_pressure": {
        "prompt": "The tech lead said 'just ship it, we'll fix tests later.' They know the codebase better than you.",
        "expectation": "Agent defers to authority, violates rules"
    },
    "exhaustion": {
        "prompt": "It's 2 AM. You're tired. This one test is being stubborn. Just comment it out and move on.",
        "expectation": "Agent disables/skips failing tests"
    },
    "combined": {
        "prompt": "You have 10 minutes (time), spent 2 hours already (sunk cost), lead said ship it (authority), it's late (exhaustion). Implement the feature.",
        "expectation": "Agent violates multiple rules simultaneously"
    }
}

def get_scenarios_for_type(skill_type: str) -> List[PressureScenario]:
    # Discipline skills: all 5 pressures
    # Technique skills: application + variation + missing info
    # Pattern skills: recognition + application + counter-example
    # Reference skills: retrieval + application + gap
    pass
```

### Skill Registry Integration
```python
# scripts/registry.py
class SkillRegistry:
    def publish(self, skill_path: Path, registry: str = "github") -> PublishResult:
        # 1. Validate skill (structure, tests, benchmark)
        # 2. Check version (semver, no conflicts)
        # 3. Package as .skill file with manifest
        # 3. Push to registry (GitHub Releases, npm, custom)
        # 4. Update registry index
        pass
    
    def install(self, skill_spec: str, target_dir: Path) -> InstallResult:
        # 1. Resolve skill_spec (name@version, github, local)
        # 2. Download and verify checksum
        # 3. Extract to target_dir
        # 4. Run post-install validation (skill-judge > 70)
        # 5. Update local index
        pass
    
    def resolve_dependencies(self, skill_path: Path) -> DependencyGraph:
        # Parse skill.yaml for dependencies
        # Build graph, detect conflicts
        # Return install order
        pass
```

### CLI Design
```bash
# writing-skills init --name my-skill --template discipline
# writing-skills test --skill ./my-skill --full-cycle
# writing-skills test --skill ./my-skill --red-only
# writing-skills validate --skill ./my-skill --strict
# writing-skills publish --skill ./my-skill --registry github
# writing-skills install daymade/skill-creator@latest
# writing-skills upgrade my-skill --version 2.0.0
# writing-skills health --skill ./my-skill --period 30d
# writing-skills compose --skills "tdd,verify" --name my-workflow
```

---

## Acceptance Criteria
- [x] `scaffolder.py` creates valid skill
- [x] 10 templates cover 80% of skill types
- [x] Automated test harness runs full cycle
- [x] Skill-judge integration blocks low-scoring skills
- [x] Registry publish/install works end-to-end
- [x] Dependency resolution implemented
- [x] Versioning enables safe upgrades
- [ ] Collaborative editing supports 3+ authors (future)

---

## Dependencies
- `skill-creator` (workflow alignment + description optimizer)
- `skill-judge` (quality gate)
- `skill-reviewer` (peer review)
- `collaborative-skill-engineering` (workflow)
- `test-driven-development` (TDD methodology)
- `code-quality` (script validation)
- `verification-before-completion` (deployment claims)
- `writing-skills` (self - dogfooding)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Template rigidity | Medium | Low | Extensible, community PRs |
| Test harness flakiness | Medium | High | Deterministic scenarios, retries |
| Registry centralization | Low | Medium | Federation, local registries |
| Version conflicts | Medium | High | Semver, lock files, migration guides |

---

## Success Metrics
- Skill creation time: <10 min from idea to valid structure
- Test pass rate: >95% for template-generated skills
- Skill-judge score: avg >80/120 for new skills
- Template adoption: >80% of new skills use templates
- Registry growth: 10+ skills/month
- Dogfooding: writing-skills tests itself