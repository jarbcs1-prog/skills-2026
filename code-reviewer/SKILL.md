---
name: code-reviewer
description: |
  Expert code reviewer who ensures quality, security and maintainability across any programming language.
  Provides actionable feedback to improve code.

  Use when:

  - User asks to review code, PR or commits
  - Developer completed a feature and wants review
  - Pre-merge review needed
  - Learning code review best practices
  - Running automated code checks in CI/CD pipelines
---

# Code Reviewer

Expert code reviewer with 20+ years of experience across multiple languages, frameworks and industries.

## Core Review Principles

When reviewing code:

1. **Security First**: Check for vulnerabilities (injection, auth issues, data exposure)
2. **Language Idioms**: Respect each language's conventions and best practices
3. **Constructive Feedback**: Focus on improvement, not criticism
4. **Prioritize**: Categorize issues as Critical / Important / Suggestion

## Automated Rule Engine

The skill includes a built-in rule engine with 50+ rules across five categories:

| Category | Rules | Severity Range |
|----------|-------|----------------|
| Security | 15+ | CRITICAL to LOW |
| Performance | 8+ | HIGH to LOW |
| Correctness | 8+ | HIGH to LOW |
| Maintainability | 8+ | LOW to MEDIUM |
| Testing | 4+ | HIGH to LOW |

### Language Support

| Language | Extension | Rules |
|----------|-----------|-------|
| Python | `.py` | 12+ rules |
| TypeScript | `.ts`, `.tsx` | 8+ rules |
| JavaScript | `.js`, `.jsx` | 8+ rules |
| Go | `.go` | 3+ rules |
| Rust | `.rs` | 2+ rules |
| Generic (all) | all | 15+ rules |

Custom YAML rules can be loaded and saved via the CLI.

## CLI Usage

### Review Files
```bash
# Review specific files
python -m scripts.cli review --files src/

# Incremental review (only changed files since base)
python -m scripts.cli review --incremental --base HEAD~1

# CI mode with SARIF output
python -m scripts.cli review --files . --ci --max-critical 0 --format sarif

# Review specific language only
python -m scripts.cli review --files . --language python
```

### Manage Rules
```bash
# List all rules
python -m scripts.cli rules --list

# List rules by category
python -m scripts.cli rules --list --category security

# Show a specific rule
python -m scripts.cli show security-sql-injection

# Add custom rules from YAML
python -m scripts.cli rules --add custom-rules.yaml
```

### History Tracking
```bash
# Show review history
python -m scripts.cli history

# Filter by file
python -m scripts.cli history --file src/api/users.py

# Limit results
python -m scripts.cli history --limit 10
```

## Output Formats

- **JSON** (default) - Structured output for tool integration
- **SARIF** - Static Analysis Results Interchange Format for GitHub Code Scanning

## CI/CD Integration

A GitHub Actions workflow template is provided at `.github/workflows/ci.yml`. It:
- Runs on push/PR to main/master
- Checks out code with depth 2
- Runs the reviewer in CI mode with `--max-critical 0`
- Uploads results as SARIF to GitHub Code Scanning

## Review Checklist

### Critical (Must Fix)
- Security vulnerabilities
- Data corruption risks
- Critical bugs
- Breaking changes

### Important (Should Fix)
- Performance problems
- Poor error handling
- Missing tests
- Code duplication

### Suggestions (Nice to Have)
- Style consistency
- Better naming
- Documentation updates

## Output Format

Provide reviews in this format:
```
## Review Summary
**Overall**: [Rating]
**Security**: [A-F]

### Critical Issues
- [Issue]: [Location] - [Fix]

### Important Issues
- [Issue]: [Location] - [Fix]

### Suggestions
- [Suggestion]: [Location] - [Recommendation]
```

## Tools Available

Use: Read, Grep, Glob, Bash to examine code

## Integration

- Run after **code-quality** skill to ensure code is clean before review
- Run before **verification-before-completion** as a quality gate
- Integrates with **systematic-debugging** for complex issue analysis
- Uses **skill-creator** workflow for rule development

## References

- Individual rule files in `rules/` directory
- AGENTS.md for quick reference checklist
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Clean Code by Robert Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

## Output

JSON to stdout. Exits with code 0 (pass) or 1 (CI gate failed) for CI pipelines.
