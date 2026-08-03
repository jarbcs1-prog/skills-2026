# PR Template for Skill Contributions

Use this template when creating PRs for agent skills repositories.

## PR Title Format

```
refactor: Align skill with agents best practices
```

Or for specific improvements:
```
feat: Add marketplace support for plugin installation
docs: Add detailed documentation in English
fix: Improve error handling in scripts
```

## PR Body Template

```markdown
## Summary

### What This PR Does

- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

### What This PR Does NOT Change

- [Preserved item 1]
- [Preserved item 2]

## Detailed Changes

### 1. [Change Category]

**Before:**
[Description of current state]

**After:**
[Description of improvement]

**Rationale:**
[Why this change helps users]

### 2. [Change Category]

...

## Why These Changes?

This PR addresses:
- [Issue 1 and how it's fixed]
- [Issue 2 and how it's fixed]

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| SKILL.md | Modified | Improved description and workflow |
| README.md | Modified | Added installation instructions |
| README.en.md | Added | English documentation |
| marketplace.json | Added | Plugin marketplace support |

## Test Plan

- [ ] Test 1
- [ ] Test 2
- [ ] Test 3

---

```

## Key Sections Explained

### Summary
- Brief overview (2-3 sentences)
- Link to best practices

### What This PR Does NOT Change
**CRITICAL** - Always include this section to show respect for original work.

### Rationale
- Explain WHY each change helps
- Quote official documentation
- Don't be judgmental

### Test Plan
- Provide actionable verification steps
- Help maintainers review quickly

## Tone Guidelines

### Do
- Be helpful and constructive
- Explain benefits to users
- Acknowledge good aspects of original

### Don't
- Be critical or judgmental
- Imply the original is "wrong"
- Use words like "fix", "correct", "proper" negatively

### Examples

```
❌ "Fixed the incorrect description format"
✅ "Improved description for better skill discovery"

❌ "The skill had several issues..."
✅ "This PR adds improvements for..."

❌ "Corrected the non-standard structure"
✅ "Added marketplace support for easier installation"
```
