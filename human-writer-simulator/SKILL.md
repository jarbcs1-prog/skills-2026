---
name: human-writer-simulator
description: Simulate human author writing style with AI detection, style profiles, and rewrite capabilities
---

# Human Writer Simulator

Simulate human author writing style with AI detection, style profiles, and rewrite capabilities.

## Description

Rewrites AI-generated content to feature characteristics of a real human author while preserving the original information and viewpoints. Includes AI text detection, style profiling, quality validation, and domain adaptation.

## Core Capabilities

1. **AI Text Detection** — Identify AI-generated text using perplexity, burstiness, and stylometric features
2. **Human-Likeness Scoring** — Multi-dimensional scoring across naturalness, personality, imperfection, coherence, emotional range, and contextual fit
3. **Style Profiles** — Configurable writing styles: conversational, technical, executive, creative, academic
4. **Rewrite Engine** — Constrained rewrite with calibrated imperfection injection and tone preservation
5. **Batch Processing** — Process multiple files with progress tracking
6. **Quality Validation** — Automated scoring and comparison of rewrite variants

## CLI Commands

```bash
# Detect AI-generated text
human-writer detect "text to analyze" --detailed

# Analyze human-likeness
human-writer analyze document.md --style-profile technical

# Rewrite with human-like style
human-writer rewrite input.txt --style conversational --imperfections 0.4

# Batch process a directory
human-writer batch input_dir/ --output output_dir/ --style executive

# Compare original and rewritten
human-writer compare original.txt rewritten.txt --blind-test

# Calibrate detector with sample corpora
human-writer calibrate --human-samples human_samples/ --ai-samples ai_samples/
```

## Style Profiles

| Profile | Formality | Vocabulary | Sentence Complexity | Hedging | Personal Voice |
|---------|-----------|------------|--------------------|---------|----------------|
| conversational | 0.2 | 0.4 | 0.3 | 0.5 | 0.9 |
| technical | 0.7 | 0.8 | 0.6 | 0.3 | 0.2 |
| executive | 0.8 | 0.7 | 0.5 | 0.2 | 0.4 |
| creative | 0.4 | 0.8 | 0.7 | 0.4 | 0.8 |
| academic | 0.9 | 0.9 | 0.8 | 0.4 | 0.1 |

## Detection Features

- Perplexity (vocabulary diversity)
- Burstiness (sentence length variation)
- Repetition (word reuse patterns)
- Transition word frequency
- Sentence structure uniformity
- Hedging language detection
- Structural uniformity (bullet points, lists)

## Workflow

1. **Detect** — Run AI detection on input text to get baseline probability
2. **Analyze** — Score human-likeness across all dimensions
3. **Rewrite** — Generate human-like rewrite with configurable style and imperfection level
4. **Validate** — Compare original and rewrite to measure improvement
5. **Batch** — Process multiple files for large-scale rewriting

## Integration

- Complements `stop-slop` for removing AI patterns
- Works with `ghostwriter-pro-ai` for professional writing
- Integrates with `writing-skills` for style consistency

## Quality Metrics

- AI detection AUC target: >0.9 on benchmark corpus
- Human-likeness correlation with human judges: >0.8
- Meaning preservation (semantic similarity): >0.95
- Style profile adherence: >90%
- Blind test human/AI confusion: >40% misclassification
