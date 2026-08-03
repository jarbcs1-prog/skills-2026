# Improvement Plan: collaborative-skill-engineering

## Current State Assessment

**Tier:** 🟡 Strong Core (Needs Structure/Polish)
**Lines:** 83 | **Version:** 1.0 (implied)

### Strengths
- Clear 6-step workflow with agent actions defined
- References `init_skill.py` and `validate_skill.py` scripts
- Emphasizes iterative feedback with user
- Structured resource planning (scripts, references, templates)
- References skill-creator guidelines

### Gaps Identified
1. **Scripts not included** - References `scripts/init_skill.py` and `scripts/validate_skill.py` but skill dir has no scripts/
2. **No skill structure guide** - References `references/skill_structure_guide.md` but not present
3. **No quality gates** - Validation only checks structure, not content quality
4. **No skill-judge integration** - Missing evaluation against rubric
5. **No template library** - No starter templates for common skill types
6. **No versioning/migration** - Skills can't evolve safely
7. **No dependency management** - Skills can't declare dependencies
8. **No testing framework** - No way to test skill behavior
9. **No publishing workflow** - Manual delivery only

---

## Improvement Roadmap

### Phase 1: Core Scripts & Structure (Week 1)
- [x] Create `scripts/init_skill.py` with interactive setup
- [x] Create `scripts/validate_skill.py` with comprehensive checks
- [x] Write `references/skill_structure_guide.md` with full anatomy
- [ ] Add skill manifest schema (name, version, dependencies, triggers)

### Phase 2: Quality Gates (Week 2)
- [ ] Integrate `skill-judge` evaluation in validation
- [x] Add content quality checks (frontmatter validation, section checks) (trigger precision, workflow completeness)
- [ ] Implement skill testing framework (input/output validation)
- [ ] Add backwards compatibility checks

### Phase 3: Templates & Patterns (Week 3)
- [ ] Create skill templates: CLI tool, Analysis skill, Integration skill, Workflow skill (minimal template exists)
- [ ] Add pattern library: common triggers, common workflows, common outputs
- [ ] Implement skill dependency resolution
- [ ] Add skill versioning with migration guides

### Phase 4: Publishing & Ecosystem (Week 4)
- [ ] Create skill packaging (zip with manifest)
- [ ] Add skill registry integration (publish, install, update)
- [ ] Implement skill marketplace metadata
- [ ] Create skill analytics (usage, quality scores)

---

## Specific Technical Tasks

### init_skill.py
```python
# scripts/init_skill.py
#!/usr/bin/env python3
"""
Interactive skill initializer.
Creates skill directory with proper structure and templates.
"""

import argparse
import os
import shutil
from pathlib import Path
from string import Template

SKILL_TEMPLATES = {
    "cli": "cli_skill_template",
    "analysis": "analysis_skill_template", 
    "integration": "integration_skill_template",
    "workflow": "workflow_skill_template",
    "minimal": "minimal_template"
}

def init_skill(name: str, template: str = "minimal", target_dir: Path = None):
    # 1. Validate name (kebab-case, unique)
    # 2. Create directory structure
    # 3. Copy template files
    # 4. Generate SKILL.md with frontmatter
    # 5. Create scripts/, references/, templates/ dirs
    # 6. Add example test file
    # 7. Initialize git repo
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--template", choices=list(SKILL_TEMPLATES.keys()), default="minimal")
    parser.add_argument("--dir", type=Path, default=Path.cwd())
    args = parser.parse_args()
    init_skill(args.name, args.template, args.dir)
```

### validate_skill.py
```python
# scripts/validate_skill.py
#!/usr/bin/env python3
"""
Comprehensive skill validator.
Checks structure, content quality, and best practices.
"""

import yaml
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]
    score: float  # 0-100 skill-judge score

def validate_skill(skill_dir: Path) -> ValidationResult:
    errors = []
    warnings = []
    
    # 1. Structure validation
    errors += check_structure(skill_dir)
    
    # 2. SKILL.md frontmatter validation
    errors += check_frontmatter(skill_dir / "SKILL.md")
    
    # 3. Content quality (skill-judge rubric)
    score, quality_issues = evaluate_quality(skill_dir)
    warnings += quality_issues
    
    # 4. Script validation (syntax, shebang, permissions)
    errors += check_scripts(skill_dir / "scripts")
    
    # 5. Reference validation (exists, readable, not empty)
    warnings += check_references(skill_dir / "references")
    
    # 6. Trigger precision check
    warnings += check_triggers(skill_dir / "SKILL.md")
    
    # 7. Dependency validation
    errors += check_dependencies(skill_dir)
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        score=score
    )
```

### Skill Manifest Schema
```yaml
# skill.yaml (new file in skill root)
name: "my-skill"
version: "1.0.0"
description: "Brief description for registry"
author: "author-name"
license: "MIT"
dependencies:
  - "code-quality>=1.0.0"
  - "verification-before-completion"
triggers:
  - "code review"
  - "quality check"
categories:
  - "development"
  - "quality"
scripts:
  - "scripts/main.py"
references:
  - "references/guide.md"
templates:
  - "templates/output.md"
tests:
  - "tests/test_skill.py"
```

### Skill Templates
```
templates/
  cli_skill/
    SKILL.md.template
    scripts/main.py.template
    references/usage.md.template
    tests/test_cli.py.template
  analysis_skill/
    SKILL.md.template
    scripts/analyze.py.template
    scripts/visualize.py.template
    references/methodology.md.template
  integration_skill/
    SKILL.md.template
    scripts/client.py.template
    scripts/auth.py.template
    references/api.md.template
  workflow_skill/
    SKILL.md.template
    scripts/orchestrate.py.template
    scripts/steps/*.py.template
    references/process.md.template
```

---

## Acceptance Criteria
- [x] `init_skill.py` creates valid skill
- [x] `validate_skill.py` catches 100% of structural errors
- [ ] Skill-judge integration (future)
- [ ] 4 templates (minimal template exists, others future)
- [ ] Dependency resolution (future)
- [ ] Packaging (future)
- [ ] Migration guide (future)

---

## Dependencies
- `skill-creator` (TDD methodology for skill development)
- `skill-judge` (quality evaluation)
- `skill-reviewer` (peer review process)
- `writing-skills` (documentation standards)
- `code-quality` (script validation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Template bloat | Medium | Low | Max 5 templates, community contributions |
| Validation false positives | Low | High | Extensive test suite, escape hatches |
| Dependency conflicts | Medium | Medium | Semantic versioning, lock files |
| Script portability | Low | High | Pure Python, no external deps |

---

## Success Metrics
- Skill creation time: <5 min from idea to valid structure
- Validation pass rate: >95% for template-generated skills
- Skill-judge score: avg >80/120 for new skills
- Template adoption: >80% of new skills use templates
- Ecosystem growth: 10+ community skills/month