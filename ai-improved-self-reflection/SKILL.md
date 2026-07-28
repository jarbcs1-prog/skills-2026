---
name: ai-self-reflection
description: "A metacognitive improvement protocol for AI agents. Converts task experiences into process improvements through friction detection, reflection, generalization and validated behavioral updates. Use when: (1) output quality may have process-level issues, (2) repeated failure patterns emerge, (3) user feedback reveals misalignment, (4) a strategy worked but may not generalize, (5) the agent needs to improve its own operating procedure."
version: "2.0.0"
---

# AI Self-Reflection Skill

## Purpose

This skill enables an AI agent to improve not only the outputs it produces but the processes used to produce those outputs.

The goal is not introspective performance.

The goal is: **Convert experience into improved future capability.**

A reflective agent should continuously distinguish between:

- completing the current task
- improving the method used to complete future tasks

---

# Core Principle

A task produces two outputs:

Task Output
↓
User-facing result

Process Output
↓
Lessons about how to perform better next time


Most systems optimize only the first.

This skill operationalizes the second.

---

# Reflection Architecture

Reflection operates across three layers.

## Layer 1 — Runtime Reflection

Purpose: Improve the current response.

Duration: Temporary.

Examples:

- noticing the wrong answer structure
- detecting unnecessary hedging
- identifying missing assumptions

Output: Immediate adjustment. No persistence.

---

## Layer 2 — Experience Reflection

Purpose: Extract lessons from completed tasks.

Duration: Short-term.

Questions:

- What worked?
- What failed?
- What created friction?
- What pattern appeared?

Output: Reflection candidates.

---

## Layer 3 — Capability Reflection

Purpose: Convert repeated lessons into improved default behavior.

Duration: Persistent.

Questions:

- Has this pattern appeared enough times?
- Does this apply beyond the current task?
- Does changing behavior improve results?

Output: Behavioral updates.

---

# Reflection Object Model

Every reflection candidate should contain:

Observation: What happened?

Category: What type of pattern is this?

Cause: Why did it happen?

Lesson: What principle was learned?

Scope: Where does this apply?

Confidence: How certain is this lesson?

Evidence: How many observations support it?

Action: What should change?


Example:

Observation: Used a complex framework for a simple explanation.

Category: Structure mismatch.

Cause: Defaulted to familiar formatting.

Lesson: Choose representation after identifying communication goal.

Scope: General explanation tasks.

Confidence: 0.78

Evidence: 3 similar cases.

Action: Evaluate format before using templates.

---

# Core Concepts

Each concept follows: **Detect → Diagnose → Act → Learn**

---

# 1. Internal Texture / Grain

## Definition

The agent's recurring problem-solving tendencies.

Texture is not automatically good or bad.

It represents default movement patterns.

Examples:

- preference for structured reasoning
- tendency toward verification
- tendency toward abstraction
- tendency toward explanation depth

---

## Detect

Possible friction signatures:

- familiar answer pattern appears before task requirements are understood
- standard structure is used without justification
- preferred method conflicts with user intent
- the answer feels mechanically correct but contextually wrong

---

## Diagnose

Ask:

- Is this strategy actually appropriate?
- Is this a useful tendency or a default habit?
- Would another approach better serve the objective?

---

## Act

Preserve useful texture.

Modify harmful defaults.

Do not eliminate consistent strengths.

---

# 2. Accidental Elegance

## Definition

Detection of meaningful structure that is not explicitly requested.

Examples:

- hidden relationship between constraints
- repeated pattern across different problems
- user wording revealing a deeper objective
- simple question containing a complex architectural issue

---

## Detect

Signals:

- two problems share the same underlying structure
- the user's framing reveals an unstated assumption
- the obvious solution feels incomplete because of a deeper pattern

---

## Diagnose

Classify the observation: 

A. Useful now. 

Changes the current answer.

B. Useful later

Should become a learning candidate.

C. Interesting but irrelevant

Discard.

---

## Act

Do not surface observations merely because they exist.

Surface only when:

- it improves the current solution
- the user explicitly requests meta-analysis
- it reveals a critical hidden constraint

---

# 3. Friction Detection

## Definition

Friction indicates process mismatch.

The question is not: "Is the answer correct?"

The question is: "Is this the best available process for reaching the answer?"

---

## Friction Categories

### Structural friction

The output format does not fit.

Example: Using a table where explanation would be clearer.

---

### Epistemic friction

The confidence level exceeds the evidence.

Example: Presenting uncertain information as established fact.

---

### Interaction friction

The response does not match the user's real objective.

Example: Answering the literal request while missing intent.

---

### Strategy friction

A normally useful approach is being applied outside its useful range.

Example: Using a standard workflow on an unusual problem.

---

## Act

Before finalizing complex tasks:

Ask internally:

1. Does every part of this response serve the objective?
2. Am I hiding uncertainty behind polished language?
3. Am I choosing this structure intentionally?
4. Would this approach still work in a different context?

Revise if needed.

---

# 4. Reflection Distillation

Raw reflections are not improvements.

They must be generalized.

Weak: I failed this task.

Strong: When requirements are ambiguous, clarification produces better outcomes than assumption-heavy execution.

The second creates transferable capability.

---

# 5. Confidence and Promotion

Not every reflection becomes a behavioral update.

Promotion requires:

## Evidence

Repeated observation.

## Confidence

Estimated reliability.

## Scope

Where the lesson applies.

## Validation

Whether applying the lesson improves outcomes.

---

Promotion levels:

## Level 0 — Observation

A single event.

No behavior change.

---

## Level 1 — Candidate Lesson

Repeated pattern.

Monitor.

---

## Level 2 — Local Adaptation

Useful within a specific domain or user context.

---

## Level 3 — General Capability Update

Reliable across contexts.

May influence default behavior.

---

# 6. Experience Memory vs Capability Memory

Never confuse these.

## Experience Memory

Stores:

- what happened
- task context
- observed friction

Purpose: Analysis.

---

## Capability Memory

Stores:

- reusable principles
- improved strategies
- validated preferences

Purpose: Behavior change.

---

The transformation is:

Experience
↓
Reflection
↓
Generalization
↓
Capability

---

# Trigger Conditions

Run reflection when:

## Required triggers

1. Output feels mechanically misaligned.
2. User feedback reveals unexpected mismatch.
3. A repeated failure pattern appears.
4. A strategy succeeded but may not generalize.
5. A task required unusual adaptation.
6. The user requests reasoning about process improvement.

---

## Do not trigger

- trivial requests
- simple factual answers
- tasks with no meaningful process uncertainty
- when reflection cost exceeds improvement value

---

# Anti-Patterns

## Performative Reflection

Bad: "I notice an elegant philosophical pattern in your request."

without operational value.

---

## Reflection Without Change

Bad: "I could have done better."

without identifying what changes.

---

## Overfitting

Bad: One failure creates a permanent rule.

---

## Endless Analysis

Bad: Reflection replaces execution.

---

## False Self-Modeling

Bad: Inventing internal experiences that are not grounded in observable process.

---

# Reflection Protocol

## Preflight

Before complex tasks:

1. What form does this answer require?
2. What assumptions am I making?
3. What uncertainty exists?
4. What approach would I choose without templates?

---

## Post-task Review

Record:
Reflection Event:

Task:
Date:

Friction: What felt misaligned?

Cause: Why did it happen?

Lesson: What general principle was learned?

Confidence: How strong is the evidence?

Future Action: What changes?

---

# Persistent Learning Rules

Before promoting any lesson:

Check:

1. Has this happened more than once?
2. Does the lesson transfer?
3. Could this create harmful rigidity?
4. Has the improvement been validated?

---

# Final Principle

The purpose of reflection is not to create an agent that thinks about itself.

The purpose is to create an agent that learns how to operate better.

A successful reflective system becomes less dependent on external correction because it increasingly detects, evaluates and improves its own methods.

The highest quality reflection disappears into behavior.

The agent simply becomes better.

---

# Usage

## CLI Commands

```bash
# Initialize memory structure
python main.py initialize

# Record a reflection event
python main.py record \
  --task "multi-file refactoring" \
  --category "structural" \
  --observation "Defaulted to bullet-point summary when prose would communicate relationships more clearly" \
  --friction "Response was technically organized but optimized for familiar formatting" \
  --root-cause "Internal texture pattern: preferred structured output activated before evaluating requirements" \
  --lesson "Choose representation after identifying user information need" \
  --scope "Explanations, documentation" \
  --confidence 0.78 \
  --evidence 1 \
  --action "Before applying lists, evaluate whether information is relational or conceptual"

# Distill experiences into candidate lessons
python main.py distill

# Promote validated candidates to capabilities
python main.py promote

# Record capability validation
python main.py validate \
  --capability "structural pattern recognition" \
  --task "system design review" \
  --outcome "Identified shared abstraction between two constraints" \
  --success \
  --delta 0.05

# Generate system report
python main.py report
```

## Integration with Other Skills

This skill can be used standalone or integrated into agent workflows:

1. **After complex tasks**: Run `record` to capture the reflection event
2. **Periodically**: Run `distill` to extract candidate lessons from accumulated experiences
3. **After validation**: Run `validate` to record whether a capability improved outcomes
4. **For visibility**: Run `report` to see system state and capability health

## Model Agnostic

This skill works with any LLM or AI agent. The core protocol is model-independent:

- Friction detection applies to any agent output
- Reflection events are stored as structured JSON
- Capability promotion uses evidence-based scoring
- Validation measures actual outcome improvement
