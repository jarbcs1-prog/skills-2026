# Improvement Plan: prompt-engineering

## Current State Assessment

**Tier:** 🔴 Duplicate / Merge Candidate
**Lines:** 340 | **Version:** 1.0 (implied)

### Strengths
- Comprehensive guide covering LLM, image, video prompting
- 50+ inference.sh CLI examples
- Covers basic structure, role prompting, CoT, few-shot, output formats, constraints
- Image prompting: subject, style, composition, quality, negative prompts
- Video prompting: shot types, camera movement, action, temporal keywords
- Advanced techniques: system prompts, structured output, iterative refinement, multi-turn
- Model-specific tips for AI Agent, GPT-4, FLUX, Veo
- Common mistakes table
- Prompt templates (code review, content writing, image generation)
- Related skills links

### Critical Issue: **Duplicate with prompt-engineer and prompt-optimizer**
- `prompt-engineer` (123 lines) - Workflow + references
- `prompt-optimizer` (195 lines) - EARS methodology + domain theories
- All three should be **merged into unified `prompt-engineering` skill**

---

## Merge Recommendation

**STRONGLY RECOMMEND MERGE** - See `prompt-engineer/improvement_plan.md` for full analysis.

### This Skill's Unique Contributions to Preserve
1. **inference.sh CLI examples** - 50+ runnable commands
2. **Image/video prompting guide** - Complete with examples
3. **Model-specific tips** - AI Agent, GPT-4, FLUX, Veo
4. **Iterative refinement examples** - Castle progression
5. **Multi-turn reasoning example** - Cart abandonment analysis
6. **Common mistakes table** - 6 mistakes with fixes
7. **Prompt templates** - Code review, content writing, image gen
8. **Related skills registry** - Links to inference.sh skills

### Migration Notes
- Move all examples to unified skill's template library
- Convert inference.sh examples to generic + provider-specific
- Preserve model-specific tips in model library
- Keep common mistakes as anti-pattern reference
- Templates become part of 20+ template library

---

## Deprecation Plan

1. **Enhance `prompt-engineer`** into unified `prompt-engineering` skill
2. **Add deprecation notice** to this skill's SKILL.md
3. **Update cross-references** in other skills
4. **Remove this skill** directory after migration

---

## Acceptance Criteria (for migration)
- [ ] Unified skill includes all 50+ inference.sh examples
- [ ] Image/video prompting guide preserved
- [ ] Model-specific tips in model library
- [ ] All templates in template library
- [ ] No broken references in other skills

---

## Dependencies
- `prompt-engineer` (primary merge target)
- `prompt-optimizer` (merge source)
- `unified prompt-engineering` (new skill)