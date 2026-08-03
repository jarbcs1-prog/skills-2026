# Skill Improvement Plan
**Skill:** skill-judge  
**File:** improvements_fixes_plan.md  
**Location:** `skill-judge/improvements_fixes_plan.md`

---  

## 1. Critical Issues Identified
1. **Excessive length** – The SKILL.md file is overly verbose, diluting expert-only knowledge.  
2. **Missing decision prompts** – Decision‑tree triggers for edge‑case handling are absent.  
3. **Edge‑case coverage** – Edge‑case handling is insufficiently detailed, especially around anti‑pattern avoidance.

---  

## 2. Critical Issues Fixes

### 2.1 Split CLI Documentation
- **Action:** Move detailed CLI reference material from the core SKILL.md to an external `cli-reference.md` file.  
- **Location:** Create `skill-judge/cli-reference.md` with all CLI‑specific examples and usage notes.  
- **Benefit:** Reduces core SKILL.md size below 300 lines, preserving token budget for expert content.

### 2.2 Add Decision‑Prompt Triggers
- **Action:** Insert explicit decision‑prompt markers in the SKILL.md workflow steps where edge‑case handling is required.  
- **Example Trigger:**  
  ```markdown
  ### Handling Anti‑Pattern Cases
  **MANDATORY - READ ENTIRE FILE**: Review [`anti-patterns.md`](anti-patterns.md) completely before proceeding.  
  **Do NOT Load** `generic-best-practices.md` for this scenario.
  ```  
- **Benefit:** Forces the agent to load only the relevant reference at the precise moment it is needed.

### 2.3 Expand Edge‑Case Coverage
- **Action:** Create/add `edge-cases.md` documenting specific anti‑patterns, reasons and corrective actions.  
- **Implementation:** Populate with concrete examples such as “NEVER use Inter font for branding” with rationale.  
- **Benefit:** Provides clear, experience‑based “NEVER” lists that AI Agent would not otherwise know.

---  

## 3. Top 3 Improvements

### 3.1 Trim to Expert‑Only Knowledge Core
- **Goal:** Ensure >70% of the remaining SKILL.md content is pure expert knowledge.  
- **Steps:**  
  1. Identify and remove all “What is PDF”, “How to write a loop” sections.  
  2. Keep only decision trees, trade‑offs and domain‑specific procedures.  
  3. Validate via the Knowledge Delta scoring rubric (>70% Expert).

### 3.2 Implement Progressive Disclosure Controls
- **Goal:** Enforce the three‑layer loading model (metadata, body, resources).  
- **Steps:**  
  1. Keep core SKILL.md under 300 lines.  
  2. Move all heavy references to `references/` directory.  
  3. Add mandatory “READ ENTIRE FILE” statements right before each reference load.  
  4. Add “Do NOT Load” directives for irrelevant references.

### 3.3 Strengthen Anti‑Pattern Documentation
- **Goal:** Provide expert‑grade “NEVER” lists with concrete, non‑obvious reasons.  
- **Steps:**  
  1. Populate `anti-patterns.md` with specific patterns such as “Overused font families (Inter, Roboto, Arial)”.  
  2. Include the underlying technical or aesthetic reasoning for each pattern.  
  3. Reference this file from decision‑prompt triggers to ensure it is loaded only when relevant.

---  

## 4. Verification Checklist
- **Length Check:** Core SKILL.md ≤ 300 lines after modifications.  
- **Token Ratio:** Expert‑only knowledge > 70% of remaining content.  
- **Decision Prompt Presence:** At least one “MANDATORY - READ ENTIRE FILE” per critical workflow.  
- **Anti‑Pattern Completeness:** `anti-patterns.md` contains ≥5 concrete NEVER items with rationale.  
- **Progressive Disclosure Compliance:** All references have explicit loading triggers and “Do NOT Load” statements.  

---  

**Outcome:** A leaner, higher‑signal Skill that loads only the necessary expert knowledge at the precise moment, dramatically improving activation relevance and reducing token waste.