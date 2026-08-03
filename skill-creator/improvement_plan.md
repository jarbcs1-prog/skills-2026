# Improvement Plan: skill-creator

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 483 | **Version:** 1.0 (implied)

### Strengths
- Complete TDD-based skill creation loop (capture intent → interview → write → test → evaluate → iterate)
- Detailed subagent orchestration for parallel test runs
- Comprehensive evaluation framework (qualitative + quantitative)
- Benchmark viewer with HTML output
- Description optimization with trigger eval queries
- Blind comparison system for rigorous A/B testing
- Packaging for distribution
- Platform-specific instructions (OpenCode Code, OpenCode.ai, Cowork)
- Reference to specialized subagents (grader, comparator, analyzer)
- 400+ lines of detailed procedural guidance

### Gaps Identified
1. **No automated skill scaffolding** - Manual directory creation
2. **No skill template library** - Start from scratch each time
3. **No CI/CD for skill testing** - Manual test execution
4. **No skill registry integration** - Manual packaging only
5. **No description optimization automation** - Semi-manual loop
6. **No skill dependency management** - Can't declare dependencies
7. **No versioning/migration** - Skills can't evolve safely
8. **No collaborative editing** - Single author workflow
9. **No skill analytics** - No usage/performance tracking post-deploy
10. **Reference files incomplete** - schemas.md referenced but not verified

---

## Improvement Roadmap

### Phase 1: Scaffolding & Templates (Week 1)
- [ ] Create `init_skill.py` for automated skill scaffolding
- [ ] Build template library (10+ skill types)
- [ ] Add skill manifest schema (dependencies, version, compatibility)
- [ ] Implement `validate_skill.py` for structure validation

### Phase 2: Automation (Week 2)
- [ ] Create GitHub Actions workflow for skill testing
- [ ] Automate description optimization (reduce manual steps)
- [ ] Add skill registry publish/install commands
- [ ] Implement skill dependency resolver

### Phase 3: Quality & Collaboration (Week 3)
- [ ] Integrate `skill-judge` for automated quality gates
- [ ] Add collaborative editing (multi-author with merge)
- [ ] Implement semantic versioning with migration guides
- [ ] Add skill health monitoring (usage, errors, performance)

### Phase 4: Ecosystem (Week 4)
- [ ] Build skill analytics dashboard
- [ ] Add skill marketplace metadata
- [ ] Create skill composition (combine skills into workflows)
- [ ] Implement skill inheritance (base skills + extensions)

---

## Specific Technical Tasks

### Skill Scaffolding
```python
# scripts/init_skill.py
class SkillScaffolder:
    TEMPLATES = {
        "tool": ToolSkillTemplate,               # File format operations (docx, pdf, xlsx)
        "analysis": AnalysisSkillTemplate,       # Data analysis, reporting
        "integration": IntegrationSkillTemplate, # API/client skills
        "workflow": WorkflowSkillTemplate,       # Multi-step processes
        "review": ReviewSkillTemplate,           # Code review, audit
        "generator": GeneratorSkillTemplate,     # Code/content generation
        "monitor": MonitorSkillTemplate,         # Observability, alerting
        "transform": TransformSkillTemplate,     # Data transformation
        "validator": ValidatorSkillTemplate,     # Validation, linting
        "router": RouterSkillTemplate            # Delegation, routing
    }
    
    def create(self, name: str, template: str, 
               target_dir: Path, metadata: SkillMetadata) -> SkillDir:
        # 1. Validate name (kebab-case, unique)
        # 2. Create directory structure
        # 3. Generate SKILL.md from template
        # 4. Create scripts/, references/, assets/, tests/
        # 5. Add evals/evals.json with template test cases
        # 6. Add GitHub Actions workflow
        # 7. Initialize git repo
        # 8. Create initial commit
        pass
```

### Skill Manifest
```yaml
# skill.yaml (new required file)
name: "my-skill"
version: "1.0.0"
description: "Comprehensive description with WHAT, WHEN, KEYWORDS"
author: "author-name"
license: "MIT"
compatibility:
  opencode: ">=0.1.0"
  platforms: ["opencode", "cowork"]
dependencies:
  - "code-quality>=1.0.0"
  - "verification-before-completion"
scripts:
  - "scripts/main.py"
references:
  - "references/guide.md"
assets:
  - "assets/template.docx"
tests:
  - "tests/test_skill.py"
evals:
  - "evals/evals.json"
```

### CI/CD Workflow
```yaml
# .github/workflows/skill-test.yml
name: Skill Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
      - name: Install skill-creator
        run: pip install -e .
      - name: Validate skill structure
        run: python scripts/validate_skill.py .
      - name: Run evals
        run: |
          python -m skill_creator.run_evals \
            --skill . \
            --evals evals/evals.json \
            --output test-results
      - name: Generate benchmark
        run: python -m scripts.aggregate_benchmark test-results
      - name: Upload benchmark
        uses: actions/upload-artifact@v4
        with:
          name: benchmark
          path: test-results/benchmark.json
```

### Description Optimization Automation
```python
# scripts/optimize_description.py
class DescriptionOptimizer:
    def optimize(self, skill_path: Path, eval_set: Path) -> OptimizationResult:
        # 1. Load current description
        # 2. Run trigger eval (current description vs eval queries)
        # 3. Generate improvement proposals (LLM-based)
        # 4. Evaluate each proposal on train/test split
        # 5. Select best by test score (avoid overfitting)
        # 6. Return optimized description with scores
        pass
```

### Skill Registry Integration
```python
# scripts/registry.py
class SkillRegistry:
    def publish(self, skill_path: Path, registry: str = "official") -> PublishResult:
        # 1. Validate skill (structure, tests, benchmark)
        # 2. Package as .skill file
        # 3. Upload to registry (GitHub Releases, npm, custom)
        # 4. Update registry index
        pass
    
    def install(self, skill_spec: str, target_dir: Path) -> InstallResult:
        # 1. Resolve skill_spec (name@version, github, local)
        # 2. Download .skill file
        # 3. Verify checksum
        # 4. Extract to target_dir
        # 5. Run post-install validation
        pass
```

---

## Acceptance Criteria
- [ ] `init_skill.py` creates valid skill in <30s
- [ ] 10 templates cover 80% of skill types
- [ ] CI/CD runs full test suite in <10 min
- [ ] Description optimization improves trigger accuracy >20%
- [ ] Registry publish/install works end-to-end
- [ ] Dependency resolution handles 10+ skill chains
- [ ] Skill-judge integration catches >90% of quality issues
- [ ] Versioning enables safe upgrades

---

## Dependencies
- `collaborative-skill-engineering` (workflow alignment)
- `skill-judge` (quality gates)
- `skill-reviewer` (peer review)
- `writing-skills` (documentation standards)
- `code-quality` (script validation)
- `test-driven-development` (TDD enforcement)
- `verification-before-completion` (quality claims)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Template bloat | Medium | Low | Max 10 core templates, community PRs |
| Registry centralization | Low | Medium | Federation support, local registries |
| Version conflicts | Medium | High | Semantic versioning, lock files |
| CI flakiness | Medium | High | Retry logic, test isolation |

---

## Success Metrics
- Skill creation time: <10 min from idea to valid structure
- Test pass rate: >95% for template-generated skills
- Description optimization: >20% trigger accuracy improvement
- Registry adoption: >100 skills published
- CI/CD reliability: >99% pass rate