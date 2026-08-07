---
name: skill-judge
description: >
  Use to evaluate skills design quality against official specifications
  and best practices. Triggers when the user mentions review, audit,
  improve, specifications, evaluate, score, or assess. Use when
  reviewing, auditing, improving, or changing SKILL.md files and skill
  packages. Provides multi-dimensional scoring and actionable
  improvement suggestions.
---

# Skill Judge
Evaluate the AI model skills design quality against official specifications and patterns derived from 17+ official examples.
---

## Core Philosophy

### What is a Skill?
A Skill is NOT a tutorial. A Skill is a **knowledge externalization mechanism**. Traditional AI knowledge is locked in model parameters. 
To teach new capabilities:
```
Traditional: Collect data → GPU cluster → Train → Deploy new version
Cost: $10,000 - $1,000,000+
Timeline: Weeks to months
```
Skills change this:
```
Skill: Edit SKILL.md → Save → Takes effect on next invocation
Cost: $0
Timeline: Instant
```
This is the paradigm shift from "training AI" to "educating AI" — like a hot-swappable LoRA adapter that requires no training. Edit a Markdown file in natural language and the model's behavior changes.

### The Core Formula
> **Good Skill = Expert-only Knowledge − What Agent Already Knows**
A Skill's value is measured by its **knowledge delta** — the gap between what it provides and what the AI model already knows.
- **Expert-only knowledge**: Decision trees, trade-offs, edge cases, anti-patterns, domain-specific thinking frameworks — things that take years of experience to accumulate
- **What Agent already knows**: Basic concepts, standard library usage, common programming patterns, general best practices
When a Skill explains "what is PDF" or "how to write a for-loop", it compresses knowledge the AI model already has. This is **token waste** — context window is a public resource shared with system prompts, conversation history, other Skills and user requests.

### Three Types of Knowledge in Skills
When evaluating, categorize each section:
| Type | Definition | Treatment |
|------|------------|-----------|
| **Expert** | Agent genuinely doesn't know this | Must keep — this is the Skill's value |
| **Activation** | Agent knows but may not think of | Keep if brief — serves as reminder |
| **Redundant** | Agent definitely knows this | Should delete — wastes tokens |
The art of Skill design is maximizing Expert content, using Activation sparingly and eliminating Redundant ruthlessly.
---

## Self-Evaluation Quick Command
Run a one-shot self-evaluation of this skill:
```powershell
opencode run skill-judge --skill . --mode self-eval
```
Or with the optional script:
```powershell
python scripts/judge_skill.py --skill .
```

### Self-Evaluation Script (`scripts/judge_skill.py`)
The `judge_skill.py` script is a deterministic, self-contained scorer that evaluates any SKILL.md package across all 8 dimensions without requiring an LLM. It is safe to call from other tools (e.g. the writing-skills test harness imports it via `importlib`).

**Usage**:
```bash
python scripts/judge_skill.py --skill .                                   # shorthand for evaluate
python scripts/judge_skill.py evaluate --skill ./my-skill                 # text report
python scripts/judge_skill.py evaluate --skill ./my-skill --format json   # machine-readable
python scripts/judge_skill.py evaluate --skill ./my-skill --format html --output report.html
python scripts/judge_skill.py evaluate --skill ./my-skill --format markdown
python scripts/judge_skill.py batch --skills-dir ./skills                 # grade every SKILL.md found
python scripts/judge_skill.py compare --skill-a ./a --skill-b ./b         # per-dimension winner
python scripts/judge_skill.py calibrate --benchmarks-dir benchmarks       # regression check vs expected bands
python scripts/judge_skill.py certify --skill ./my-skill --level strong   # gate on a target level
python scripts/judge_skill.py history --skill my-skill --show-trend       # score history + trend
```

**Scoring model** — the 8 dimensions sum to 120; the quality gate fails when `total < 70` or `D1 < 11`. Grade bands: A+ (≥100), A (≥90), B+ (≥80), B (≥70), C (≥60), F (<60). `certify` levels: `expert` (≥90 and gate), `strong` (≥80 and gate), `adequate` (≥70), `blocked` (gate failed).

**Calibration** — `benchmarks/*.json` record the expected band for reference skills (docx/xlsx/pdf from the local the AI model library plus the repo skills). Run `calibrate` after any scorer change; a mismatch means the heuristic drifted. Current bands reflect measured heuristic scores, not aspirational targets.

**History** — all commands write to a JSONL history file (`~/.skill-judge/history.jsonl` unless `--history` is given), enabling trend analysis and regression detection across evaluation runs.
---

## Evaluation Dimensions (120 points total)

### D1: Knowledge Delta (20 points) — THE CORE DIMENSION
Does the Skill add genuine expert knowledge?
| Score | Criteria |
|-------|----------|
| 0-5 | Explains basics the AI model knows (what is X, how to write code, standard library tutorials) |
| 6-10 | Mixed: some expert knowledge diluted by obvious content |
| 11-15 | Mostly expert knowledge with minimal redundancy |
| 16-20 | Pure knowledge delta — every paragraph earns its tokens |
**Red flags** (instant score ≤5):
- "What is [basic concept]" sections
- Step-by-step tutorials for standard operations
- Explaining how to use common libraries
- Generic best practices ("write clean code", "handle errors")
- Definitions of industry-standard terms
**Green flags** (indicators of high knowledge delta):
- Decision trees for non-obvious choices ("when X fails, try Y because Z")
- Trade-offs only an expert would know ("A is faster but B handles edge case C")
- Edge cases from real-world experience
- "NEVER do X because [non-obvious reason]"
- Domain-specific thinking frameworks
**Evaluation questions**:
1. For each section, ask: "Does the AI model already know this?"
2. If explaining something, ask: "Is this explaining TO the AI model or FOR the AI model?"
3. Count paragraphs that are Expert vs Activation vs Redundant
---

### D2: Mindset + Appropriate Procedures (15 points)
Does the Skill transfer expert **thinking patterns** along with **necessary domain-specific procedures**?
| Type | Example | Value |
|------|---------|-------|
| **Thinking patterns** | "Before designing, ask: What makes this memorable?" | High — shapes decision-making |
| **Domain-specific procedures** | "OOXML workflow: unpack → edit XML → validate → pack" | High — AI Agent may not know this |
| **Generic procedures** | "Step 1: Open file, Step 2: Edit, Step 3: Save" | Low — AI Agent already knows |

| Score | Criteria |
|-------|----------|
| 0-3 | Only generic procedures the AI model already knows |
| 4-7 | Has domain procedures but lacks thinking frameworks |
| 8-11 | Good balance: thinking patterns + domain-specific workflows |
| 12-15 | Expert-level: shapes thinking AND provides procedures the AI model wouldn't know |
**The test**:
1. Does it tell the AI model WHAT to think about? (thinking patterns)
2. Does it tell the AI model HOW to do things it wouldn't know? (domain procedures)
---

### D3: Anti-Pattern Quality (15 points)
Does the Skill have effective NEVER lists?
| Score | Criteria |
|-------|----------|
| 0-3 | No anti-patterns mentioned |
| 4-7 | Generic warnings ("avoid errors", "be careful", "consider edge cases") |
| 8-11 | Specific NEVER list with some reasoning |
| 12-15 | Expert-grade anti-patterns with WHY — things only experience teaches |
**Expert anti-patterns** (specific + reason):
```markdown
NEVER use generic AI-generated aesthetics like:
- Overused font families (Inter, Roboto, Arial)
- Cliched color schemes (purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Default border-radius on everything
```
**Weak anti-patterns** (vague, no reasoning):
```markdown
Avoid making mistakes.
Be careful with edge cases.
Don't write bad code.
```
**The test**: Would an expert read the anti-pattern list and say "yes, I learned this the hard way"?
---

### D4: Specification Compliance — Especially Description (15 points)
Does the Skill follow official format requirements? **Special focus on description quality.**
| Score | Criteria |
|-------|----------|
| 0-5 | Missing frontmatter or invalid format |
| 6-10 | Has frontmatter but description is vague or incomplete |
| 11-13 | Valid frontmatter, description has WHAT but weak on WHEN |
| 14-15 | Perfect: comprehensive description with WHAT, WHEN and trigger keywords |
**Frontmatter requirements**:
- `name`: lowercase, alphanumeric + hyphens only, ≤64 characters
- `description`: **THE MOST CRITICAL FIELD** — determines if skill gets used at all
**Why description is THE MOST IMPORTANT field**: The the AI model only sees descriptions before loading. If description doesn't match → Skill NEVER gets loaded. If description is vague → Skill might not trigger when it should. If description lacks keywords → Skill is invisible to the AI model.
**Description must answer THREE questions**:
1. **WHAT**: What does this Skill do? (functionality)
2. **WHEN**: In what situations should it be used? (trigger scenarios)
3. **KEYWORDS**: What terms should trigger this Skill? (searchable terms)
---

### D5: Progressive Disclosure (15 points)
Does the Skill implement proper content layering?
```
Layer 1: Metadata (always in memory) — Only name + description (~100 tokens)
Layer 2: SKILL.md Body (loaded after triggering) — Detailed guidelines, decision trees (Ideal: < 300 lines)
Layer 3: Resources (loaded on demand) — scripts/, references/, assets/ (No limit)
```
| Score | Criteria |
|-------|----------|
| 0-5 | Everything dumped in SKILL.md (>500 lines, no structure) |
| 6-10 | Has references but unclear when to load them |
| 11-13 | Good layering with MANDATORY triggers present |
| 14-15 | Perfect: decision trees + explicit triggers + "Do NOT Load" guidance |
**Loading Trigger Quality**:
| Quality | Characteristics |
|---------|-----------------|
| Poor | References listed at end, no loading guidance |
| Mediocre | Some triggers but not embedded in workflow |
| Good | MANDATORY triggers in workflow steps |
| Excellent | Scenario detection + conditional triggers + "Do NOT Load" |
**Good loading trigger** (embedded in workflow):
```markdown
### Creating New Document
**MANDATORY - READ ENTIRE FILE**: Before proceeding, you MUST read [`docx-js.md`](docx-js.md) (~500 lines) completely from start to finish.
**Do NOT load** `ooxml.md` or `redlining.md` for this task.
```
---

### D6: Freedom Calibration (15 points)
Is the level of specificity appropriate for the task's fragility?
| Task Type | Should Have | Why | Example Skill |
|-----------|-------------|-----|---------------|
| Creative/Design | High freedom | Multiple valid approaches, differentiation is value | frontend-design |
| Code review | Medium freedom | Principles exist but judgment required | code-review |
| File format operations | Low freedom | One wrong byte corrupts file, consistency critical | docx, xlsx, pdf |
**The test**: Ask "if the AI model makes a mistake, what's the consequence?"
- High consequence → Low freedom (exact scripts, no parameters)
- Low consequence → High freedom (principles, not steps)
---

### D7: Pattern Recognition (10 points)
Does the Skill follow an established official pattern?
| Pattern | ~Lines | Key Characteristics | Example | When to Use |
|---------|--------|---------------------|---------|-------------|
| **Mindset** | ~50 | Thinking > technique, strong NEVER list, high freedom | frontend-design | Creative tasks requiring taste |
| **Navigation** | ~30 | Minimal SKILL.md, routes to sub-files | internal-comms | Multiple distinct scenarios |
| **Philosophy** | ~150 | Two-step: Philosophy → Express, emphasizes craft | canvas-design | Art/creation requiring originality |
| **Process** | ~200 | Phased workflow, checkpoints, medium freedom | mcp-builder | Complex multi-step projects |
| **Tool** | ~300 | Decision trees, code examples, low freedom | docx, pdf, xlsx | Precise operations on specific formats |

| Score | Criteria |
|-------|----------|
| 0-3 | No recognizable pattern, chaotic structure |
| 4-6 | Partially follows a pattern with significant deviations |
| 7-8 | Clear pattern with minor deviations |
| 9-10 | Masterful application of appropriate pattern |
---

### D8: Practical Usability (15 points)
Can the AI model actually use this Skill effectively?
| Score | Criteria |
|-------|----------|
| 0-5 | Confusing, incomplete, contradictory or untested guidance |
| 6-10 | Usable but with noticeable gaps |
| 11-13 | Clear guidance for common cases |
| 14-15 | Comprehensive coverage including edge cases and error handling |
**Check for**:
- **Decision trees**: For multi-path scenarios, is there clear guidance on which path to take?
- **Code examples**: Do they actually work? Or are they pseudocode that breaks?
- **Error handling**: What if the main approach fails? Are fallbacks provided?
- **Edge cases**: Are unusual but realistic scenarios covered?
- **Actionability**: Can the AI model immediately act or needs to figure things out?
---

## NEVER Do When Evaluating
- **NEVER** give high scores for "professional" appearance — look at knowledge delta
- **NEVER** ignore token waste — every redundant paragraph costs context
- **NEVER** skip testing decision trees — verify they actually work
- **NEVER** forgive explaining basics — that's token waste
- **NEVER** overlook missing anti-patterns — critical gap
- **NEVER** undervalue the description field — poor description = skill never used
- **NEVER** confuse Activation content with Expert knowledge — they have different scoring bands
- **NEVER** accept vague anti-patterns without reasoning — if there's no "because", it's weak
- **NEVER** evaluate dimensions in isolation — cross-score to catch contradictions between sections
- **NEVER** skip the description quality check — a poor description means the skill will never be loaded by the AI model
- **NEVER** trust a high score without checking knowledge delta — a skill that looks polished but explains basics scores well visually yet has zero expert value; run `python scripts/judge_skill.py evaluate --skill . --format json` and check D1 is ≥11 before trusting the total
- **NEVER** accept a "passing" grade without checking the E:A:R ratio — a skill with 40% redundant content can still score ≥70 if the expert portions are well-written; use `python scripts/judge_skill.py evaluate --skill . --format json` to get the per-dimension breakdown and verify D1 isn't inflated by Activation or Redundant content
- **NEVER** skip the calibration step after modifying the scorer — run `python scripts/judge_skill.py calibrate --benchmarks-dir benchmarks` to detect heuristic drift; a scorer that drifts more than 5 points from expected bands on reference skills (docx, xlsx, pdf) needs investigation
---

## Evaluation Protocol
**MANDATORY - READ ENTIRE FILE**: Before executing the evaluation protocol, you MUST read [`cli-reference.md`](cli-reference.md) completely from start to finish. This contains the detailed Step 1-5 protocol and report template.
**Do NOT load** `references/anti-patterns.md` or `references/edge-cases.md` during protocol execution. Loading these files introduces bias — anti-patterns will inflate D3 scores and edge-cases will inflate D1 scores, corrupting the independent evaluation.
---

## Decision-Prompt Triggers

### When Evaluating Knowledge Delta (D1)
**MANDATORY - READ ENTIRE FILE**: Before scoring D1, you MUST read [`references/edge-cases.md`](references/edge-cases.md) completely from start to finish.
**NEVER set any range limits when reading this file.**
**Do NOT load** `references/failure-patterns.md` or `references/quick-reference.md` for this dimension. Failure-patterns contain heuristic failure modes that bias D1 scoring, and quick-reference is only for the final report phase — loading either contaminates the independent D1 evaluation.
**Validate**: After scoring, run `python scripts/judge_skill.py evaluate --skill . --format json` and compare the D1 score against your manual assessment. A discrepancy >2 points indicates the heuristic drifted or you misclassified a section.

### When Evaluating Anti-Pattern Quality (D3)
**MANDATORY - READ ENTIRE FILE**: Before scoring D3, you MUST read [`references/anti-patterns.md`](references/anti-patterns.md) completely from start to finish.
**NEVER set any range limits when reading this file.**
**Do NOT load** `references/failure-patterns.md` for this dimension. Failure-patterns reference the same anti-pattern heuristics and will cause circular scoring.
**Validate**: After scoring, run `python scripts/judge_skill.py evaluate --skill . --format json` and compare the D3 score against your manual assessment. A discrepancy >2 points indicates the heuristic drifted or you misclassified an anti-pattern as specific when it was vague.

### When Evaluating Progressive Disclosure (D5)
**MANDATORY - READ ENTIRE FILE**: Before scoring D5, you MUST read [`references/failure-patterns.md`](references/failure-patterns.md) completely from start to finish.
**NEVER set any range limits when reading this file.**
**Do NOT load** `references/anti-patterns.md` or `references/edge-cases.md` for this dimension. Anti-patterns and edge-cases are evaluated in D3 and D1 respectively; loading them here creates cross-dimensional contamination.
**Validate**: After scoring, run `python scripts/judge_skill.py evaluate --skill . --format json` and compare the D5 score against your manual assessment. A discrepancy >2 points indicates the heuristic drifted or you misjudged the trigger quality.

### When Generating Final Report
**MANDATORY - READ ENTIRE FILE**: Before generating the evaluation report, you MUST read [`references/quick-reference.md`](references/quick-reference.md) completely from start to finish.
**NEVER set any range limits when reading this file.**
This ensures the Quick Reference Checklist is applied consistently across all evaluations.
**Do NOT load** any other reference file during report generation — the report must reflect only the dimension scores already computed, not additional heuristic inputs.
**Validate**: After generating the report, run `python scripts/judge_skill.py evaluate --skill . --format markdown` to produce a machine-readable baseline, then run `python scripts/judge_skill.py certify --skill . --level strong` to verify the grade passes the quality gate.
---
