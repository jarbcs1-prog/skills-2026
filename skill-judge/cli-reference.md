# cli-reference.md

## Evaluation Protocol

### Step 1: First Pass - Knowledge Delta Scan
1. Read the SKILL.md completely.
2. For each section, determine if it's E (Expert), A (Activation) or R (Redundant).
3. Calculate the E:A:R ratio.

### Step 2: Structure Analysis
1. Check frontmatter validity (`name` and `description` fields).
2. Count the total lines in SKILL.md.
3. List all reference files (e.g. cli-reference.md, improvements_fixes_plan.md, SKILL.md) and their sizes.
4. Identify the pattern the Skill follows (e.g. Tool pattern).
5. Check for loading triggers in workflow steps.

### Step 3: Score Each Dimension
1. For each dimension (D1 to D8):
   a. Find specific evidence from SKILL.md.
   b. Assign a score (0-20 or 0-15 depending on dimension).
   c. Note validations and improvements needed.

### Step 4: Calculate Total & Grade
1. Sum all dimension scores.
2. Determine the percentage and grade (A-F).

### Step 5: Generate Report
1. Create a markdown report using the template provided in the skill-judge description.
2. Include all dimension scores, critical issues, top improvements.

### Decision-Prompt Triggers
- When evaluating D1: Mandatory to read edge-cases.md.
- When evaluating D3: Mandatory to read anti-patterns.md.
- When evaluating D5: Mandatory to read failure-patterns.md.
- Before generating the report: Mandatory to read quick-reference.md.

---