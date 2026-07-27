---
name: collaborative-skill-engineering
description: |
  Guide for AI agents to collaboratively define, develop and validate new skills with users. This skill codifies an interactive, step-by-step workflow to ensure effective skill creation, leveraging user input for requirements, content and iterative refinement. Use this skill when a user requests to create a new skill or significantly update an existing one, facilitating a structured and collaborative development process.
---

# Collaborative Skill Engineering

This skill provides a structured, interactive workflow for AI agents to collaborate with users in the definition, development and validation of new skills. It ensures that skills are built effectively, meet user requirements and adhere to best practices.

## Workflow for Collaborative Skill Creation

Creating a new skill collaboratively involves the following sequential steps, with continuous user interaction and feedback:

### Step 1: Understand Skill Requirements

Engage with the user to gather a clear understanding of the desired skill. This involves asking clarifying questions and requesting concrete examples of how the skill will be used. Focus on:
-   **Primary Goal**: What is the main purpose of the skill?
-   **Functionality**: What specific tasks or capabilities should it support?
-   **Usage Scenarios**: Provide examples of how the skill would be invoked and what outcomes are expected.

*Agent Action*: Use `message` with `type="ask"` to prompt the user for detailed requirements.

### Step 2: Plan Skill Contents

Based on the gathered requirements, plan the reusable components of the skill. This includes identifying potential `scripts/`, `references/` and `templates/` that will be needed. Consider:
-   **Scripts**: For repetitive or deterministic tasks (e.g.data processing, file manipulation).
-   **References**: For domain-specific knowledge, API documentation or detailed guidelines.
-   **Templates**: For boilerplate code, output formats or visual assets.

*Agent Action*: Internally formulate a plan for the skill's structure and required resources.

### Step 3: Initialize the Skill Directory

Create the basic directory structure for the new skill using the local `init_skill.py` script. This sets up the `SKILL.md` template and example resource directories.

```bash
python scripts/init_skill.py <skill-name>
```

*Agent Action*: Use `shell` to execute the `init_skill.py` script.

### Step 4: Develop Skill Resources and SKILL.md

This is an iterative phase where the agent implements the planned resources and writes the `SKILL.md` content. Throughout this step, maintain active communication with the user for feedback and to provide updates.

#### 4.1 Implement Resources

Create or modify files within `scripts/`, `references/` and `templates/` as identified in Step 2. Ensure scripts are functional and references are comprehensive.

*Agent Action*: Use `file` (write/append) to create resource files. Use `shell` to test scripts.

#### 4.2 Write SKILL.md

Populate the `SKILL.md` file with the skill's frontmatter (name, description) and detailed instructions. Follow the guidelines from `skill-creator` for conciseness, appropriate degrees of freedom and progressive disclosure.

*Agent Action*: Use `file` (write/edit) to update `SKILL.md`.

#### 4.3 Iterative Feedback Loop

After initial development or significant updates, present the work to the user for review. Be prepared to revise based on their feedback.

*Agent Action*: Use `message` with `type="ask"` or `type="info"` to share progress and request feedback.

### Step 5: Validate the Skill

Once the skill's content is complete, validate its structure using the local `validate_skill.py` script. Address any reported errors.

```bash
python scripts/validate_skill.py <skill-directory>
```

*Agent Action*: Use `shell` to execute the `validate_skill.py` script. Use `file` (edit) to fix errors.

### Step 6: Deliver the Skill

Present the validated skill to the user. The system will automatically package and offer options to add, download or preview the skill.

*Agent Action*: Use `message` with `type="result"` and attach the `SKILL.md` file.

## References

-   `references/skill_structure_guide.md` — Skill directory anatomy, frontmatter format and naming conventions.
