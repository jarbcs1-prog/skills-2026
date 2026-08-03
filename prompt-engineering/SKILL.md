---
name: prompt-engineering
description: |
  Master prompt engineering for AI models (LLMs, image, video). Write, optimize and evaluate prompts using structured workflows, EARS methodology, domain theory grounding and automated evaluation. Use when: designing prompts for new LLM applications, optimizing existing prompts, implementing chain-of-thought/few-shot, creating system prompts with guardrails, building JSON/function-calling schemas, developing prompt evaluation frameworks, converting vague requirements to testable specifications.
version: "3.0.0"
---

# Prompt Engineering — Unified Skill

Expert prompt engineering for LLMs, image generators and video models. Combines structured workflows, EARS requirements transformation, domain theory grounding and automated evaluation.

## When to Use

- Designing prompts for new LLM applications
- Optimizing existing prompts for accuracy/efficiency
- Implementing chain-of-thought, few-shot, ReAct, tree-of-thoughts
- Creating system prompts with personas and guardrails
- Building structured output schemas (JSON mode, function calling)
- Developing prompt evaluation and testing frameworks
- Converting vague requirements to precise specifications (EARS)
- Debugging inconsistent LLM outputs
- Migrating prompts between models/providers
- Image/video prompt engineering (FLUX, Veo, etc.)

## Core Workflow (6 Steps)

### 1. Understand Requirements
Define task, success criteria, constraints, edge cases. Identify if requirement is vague and needs EARS optimization.

### 2. Design Initial Prompt
Choose pattern (zero-shot, few-shot, CoT, ReAct). Write clear instructions with role, task, constraints, output format.

### 3. Apply EARS Optimization (if vague)
Transform requirements using EARS syntax:
- **Ubiquitous**: `The system shall <action>`
- **Event-driven**: `When <trigger>, the system shall <action>`
- **State-driven**: `While <state>, the system shall <action>`
- **Conditional**: `If <condition>, the system shall <action>`
- **Unwanted behavior**: `If <condition>, the system shall prevent <unwanted action>`

### 4. Ground in Domain Theories
Map to frameworks: GTD, BJ Fogg, Hick's Law, Zero Trust, etc. Cite theories in prompt.

### 5. Test and Evaluate
Run diverse test cases, measure accuracy/consistency/latency/cost. Use evaluation framework.

### 6. Iterate and Deploy
One change at a time. Version prompts. Monitor production for degradation.

---

## LLM Prompting Patterns

### Basic Structure
```
[Role/Context] + [Task] + [Constraints] + [Output Format]
```

### Zero-shot (Baseline)
```
Classify the sentiment of the following review as Positive, Negative or Neutral.

Review: {{review}}
Sentiment:
```

### Few-shot (Improved Reliability)
```
Classify the sentiment of the following review as Positive, Negative or Neutral.

Review: "The battery life is incredible, lasts all day."
Sentiment: Positive

Review: "Stopped working after two weeks. Very disappointed."
Sentiment: Negative

Review: "It arrived on time and matches the description."
Sentiment: Neutral

Review: {{review}}
Sentiment:
```

### Chain-of-Thought
```
Solve this step by step:

A store sells apples for $2 each and oranges for $3 each. If someone buys 5 fruits and spends $12, how many of each fruit did they buy?

Think through this step by step before giving the final answer.
```

### ReAct (Reasoning + Acting)
```
You have access to tools: search, calculate, read_file.

Question: What's the population of Tokyo?

Thought: I need to search for current Tokyo population.
Action: search("Tokyo population 2024")
Observation: 37.4 million (metro area)
Thought: Found the answer.
Final Answer: Tokyo metro population is approximately 37.4 million.
```

### Structured Output (JSON/Function Calling)
```
Analyze sentiment of these reviews. Return JSON array with objects containing "text", "sentiment" (positive/negative/neutral), "confidence" (0-1).

Reviews:
1. "Great product, fast shipping!"
2. "Meh, its okay I guess"
3. "Worst purchase ever, total waste of money"

Return only valid JSON, no explanation.
```

### Constraint Setting
```
Summarize this article in exactly 3 bullet points. Each bullet must be under 20 words. Focus only on actionable insights, not background information.

[article text]
```

---

## EARS Requirements Transformation

### When to Apply
- Vague feature requests ("build a dashboard", "create a reminder app")
- Missing triggers, conditions, or measurable outcomes
- Natural language needing conversion to testable specs

### Six-Step EARS Workflow

**Step 1: Analyze Original Requirement**
Identify weaknesses: overly broad, missing triggers, ambiguous actions, no constraints.

**Step 2: Apply EARS Transformation**
Convert to EARS patterns (5 core patterns above).

**Step 3: Identify Domain Theories**
Map to frameworks:
- Productivity → GTD, Pomodoro, Eisenhower Matrix
- Behavior Change → BJ Fogg (B=MAT), Atomic Habits
- UX Design → Hick's Law, Fitts's Law, Gestalt Principles
- Security → Zero Trust, Defense in Depth, Privacy by Design
- Learning → Spaced Repetition, Feynman Technique, Bloom's Taxonomy

**Step 4: Extract Concrete Examples**
Real data, not placeholders: "Product: 'Laptop', Price: $999, Stock: 15"

**Step 5: Generate Enhanced Prompt**
Structure: Role → Skills → Workflows → Examples → Formats

**Step 6: Present Optimization Results**
Structured format with Original → Issues → EARS → Domain → Enhanced Prompt

---

## Image Generation Prompting (FLUX, Midjourney, DALL-E)

### Basic Structure
```
[Subject] + [Style] + [Composition] + [Lighting] + [Technical]
```

### Subject Description
```
# Bad: vague
"a cat"

# Good: specific
"A fluffy orange tabby cat with green eyes, sitting on a vintage leather armchair"
```

### Style Keywords
```
"Portrait photograph of a woman, shot on Kodak Portra 400 film, soft natural lighting, shallow depth of field, nostalgic mood, analog photography aesthetic"
```

### Composition Control
```
"Wide establishing shot of a cyberpunk city skyline at night, rule of thirds composition, neon signs in foreground, towering skyscrapers in background, rain-slicked streets"
```

### Quality Keywords
```
photorealistic, 8K, ultra detailed, sharp focus, professional, masterpiece, high quality, best quality, intricate details
```

### Negative Prompts
```
"Professional headshot portrait, clean background"
Negative: "blurry, distorted, extra limbs, watermark, text, low quality, cartoon, anime"
```

---

## Video Prompting (Veo, Sora, Runway)

### Basic Structure
```
[Shot Type] + [Subject] + [Action] + [Setting] + [Style]
```

### Camera Movement
```
"Slow tracking shot following a woman walking through a sunlit forest, golden hour lighting, shallow depth of field, cinematic, 4K"
```

### Action Description
```
"Close-up of hands kneading bread dough on a wooden surface, flour dust floating in morning light, slow motion, cozy baking aesthetic"
```

### Temporal Keywords
```
slow motion, timelapse, real-time, smooth motion, continuous shot, quick cuts, frozen moment
```

---

## Advanced Techniques

### System Prompts
```
System: "You are a helpful coding assistant. Always provide code with comments. If unsure, say so rather than guessing."
Prompt: "Write a Python function to validate email addresses using regex."
```

### Structured Output with Schema
```
Extract information and return as JSON:
"John Smith, CEO of TechCorp, announced yesterday that the company raised $50 million in Series B funding. The round was led by Venture Partners."

Schema:
{
  "person": string,
  "title": string,
  "company": string,
  "event": string,
  "amount": string,
  "investor": string
}
```

### Iterative Refinement
```
# 1. Start broad
"A castle on a hill"

# 2. Add specifics
"A medieval stone castle on a grassy hill"

# 3. Add style
"A medieval stone castle on a grassy hill, dramatic sunset sky, fantasy art style, epic composition"

# 4. Add technical
"A medieval stone castle on a grassy hill, dramatic sunset sky, fantasy art style by Greg Rutkowski, epic composition, 8K, highly detailed"
```

### Multi-Turn Reasoning
```
# Turn 1: Analyze
"Analyze this business problem: Our e-commerce site has 70% cart abandonment. List potential causes."

# Turn 2: Prioritize  
"Given these causes: [previous output], rank by impact and ease of fixing. Format as priority matrix."

# Turn 3: Action Plan
"For top 3 causes, provide specific A/B tests to validate and fix each issue."
```

---

## Model-Specific Guidance

| Model | Strengths | Prefers | Avoids |
|-------|-----------|---------|--------|
| Opencode | Nuanced instructions, role-playing, complex constraints | Explicit output formats | Ambiguity |
| GPT-4o / o1 | Code generation, reasoning, structured output | Examples, "think step by step" | Terse instructions |
| Claude Sonnet 4 | Reasoning, analysis, long context, nuance | XML tags, detailed instructions, constitutional AI | Assumed context |
| FLUX | Detailed subjects, style references, lighting | Specific descriptions, quality keywords | Vague subjects |
| Veo | Camera movement, cinematic language, action | Temporal context, shot types | Static descriptions |

---

## Evaluation Framework

### Metrics
- **Accuracy**: Correct outputs / total test cases
- **Consistency**: Standard deviation across runs (lower = better)
- **Latency**: Average response time
- **Cost**: Tokens × model pricing
- **Token Efficiency**: Output quality per token

### Test Case Design
- Diverse, realistic inputs including edge cases
- Empty inputs, unusual formats, adversarial cases
- Match target distribution for few-shot examples

### Automated Evaluation
```python
# evaluator.py
class PromptEvaluator:
    def evaluate(self, prompt: str, test_cases: List[TestCase], model: str) -> EvaluationResult:
        results = []
        for tc in test_cases:
            output = run_prompt(prompt, tc.input, model)
            scores = {
                "accuracy": accuracy_score(output, tc.expected),
                "format_compliance": format_check(output, tc.schema),
                "latency": measure_latency(),
                "tokens": count_tokens(output)
            }
            results.append(TestResult(input=tc.input, output=output, scores=scores))
        return aggregate(results)
```

### A/B Testing
- Random assignment, sequential testing
- Statistical significance (p < 0.05)
- Effect size (Cohen's d)
- Minimum sample size calculation

---

## Constraints

### MUST DO
- Test with diverse, realistic inputs including edge cases
- Measure with quantitative metrics (accuracy, consistency, latency, cost)
- Version prompts and track changes systematically
- Document expected behavior and known limitations
- Use few-shot examples matching target distribution
- Validate structured outputs against schemas
- Consider token costs and latency in design
- Test across model versions before production

### MUST NOT DO
- Deploy without systematic evaluation
- Use few-shot examples contradicting instructions
- Ignore model-specific capabilities/limitations
- Skip edge case testing
- Make multiple simultaneous changes when debugging
- Hardcode sensitive data in prompts
- Assume prompts transfer perfectly between models
- Neglect production monitoring for degradation

---

## Output Templates

When delivering prompt work, provide:
1. **Final prompt** with clear sections (role, task, constraints, format)
2. **Test cases** and evaluation results
3. **Usage instructions** (temperature, max tokens, model version)
4. **Performance metrics** and comparison with baselines
5. **Known limitations** and edge cases

---

## Reference Files (Load On-Demand)

| File | Purpose | Load When |
|------|---------|-----------|
| `references/prompt-patterns.md` | Zero-shot, few-shot, CoT, ReAct, ToT | Choosing pattern |
| `references/prompt-optimization.md` | Iterative refinement, A/B testing, token reduction | Optimizing |
| `references/evaluation-frameworks.md` | Metrics, test suites, automated evaluation | Testing |
| `references/structured-outputs.md` | JSON mode, function calling, schema design | Structured output |
| `references/system-prompts.md` | Persona design, guardrails, context management | System prompts |
| `references/ears_syntax.md` | Complete EARS syntax, 5 patterns, guidelines | EARS transformation |
| `references/domain_theories.md` | 40+ theories across 10 domains | Domain grounding |
| `references/examples.md` | 4 complete transformations with templates | Learning by example |
| `references/advanced_techniques.md` | Multi-stakeholder, non-functional, complex logic | Complex scenarios |

---

## Quick Reference

### Do's
✅ Break compound requirements (one EARS statement each)
✅ Specify measurable criteria (numbers, timeframes, percentages)
✅ Include error/edge cases
✅ Ground in established theories
✅ Use concrete examples with real data

### Don'ts
❌ Avoid vague language ("fast", "user-friendly")
❌ Don't assume implicit knowledge
❌ Don't mix multiple actions in one statement
❌ Don't use placeholders in examples

---

## Inference.sh CLI Examples

```bash
# Install
curl -fsSL https://cli.inference.sh | sh && infsh login

# LLM prompt
infsh app run opencode/north-mini-code-free --input '{
  "prompt": "You are a senior software engineer. Review this code for security vulnerabilities:\n\n```python\nuser_input = request.args.get(\"query\")\nresult = db.execute(f\"SELECT * FROM users WHERE name = {user_input}\")\n```\n\nProvide specific issues and fixes."
}'

# Image generation
infsh app run falai/flux-dev --input '{
  "prompt": "A fluffy orange tabby cat with green eyes, sitting on a vintage leather armchair"
}'

# Video generation
infsh app run google/veo-3-1-fast --input '{
  "prompt": "Slow tracking shot following a woman walking through a sunlit forest, golden hour lighting, shallow depth of field, cinematic, 4K"
}'

# List all apps
infsh app list
```

---

## Related Skills

- `skill-creator` — For creating new prompt engineering skills
- `skill-judge` — For evaluating prompt engineering skill quality
- `test-driven-development` — TDD applied to prompt evaluation
- `systematic-debugging` — Debugging prompt failures
- `verification-before-completion` — Verify prompt improvements before claiming success

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2026-08-03 | Unified prompt-engineer + prompt-engineering + prompt-optimizer |
| 2.0.0 | 2026-07-30 | Added image/video prompting, inference.sh CLI |
| 1.0.0 | 2026-07-01 | Initial prompt-engineer workflow |

---

## License

MIT License — Use freely with your AI agents.