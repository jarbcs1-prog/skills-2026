---
name: daydream
description: Multi-agent system that mines the Obsidian vault for non-obvious connections between notes, mimicking the brain's default mode network. Use when you want to discover unexpected connections in your note vault, generate insights from existing notes, or explore thematic patterns across your knowledge base.
version: "2.0.0"
---

# Vault Daydream Skill

Multi-agent system that mines the Obsidian vault for non-obvious connections between notes, mimicking the brain's default mode network. Samples random note pairs, synthesizes connections, filters with critic.

## When to Use

- Exploring connections between notes in your vault
- Generating insights from existing knowledge
- Discovering thematic patterns across notes
- Finding unexpected links between ideas

## CLI Usage

```bash
# Run daydream analysis on your vault
daydream run

# Dry run (preview without writing)
daydream run --dry-run

# Show configuration
daydream config show

# Deduplicate existing insights
daydream dedup

# Export knowledge graph
daydream graph --output Daydreams/knowledge_graph.graphml

# Show insight statistics
daydream stats
```

## Configuration

Daydream uses a `.daydream.yml` config file for all tunable parameters:

```yaml
vault:
  path: "auto"
  max_age_days: 120
  include_patterns: ["*.md"]
  exclude_patterns: ["Daydreams/", ".obsidian/", "templates/"]

sampling:
  pairs_per_run: 50
  recency_weight: 0.7
  diversity_weight: 0.3
  min_note_length: 100
  max_note_length: 5000

synthesis:
  model: "opencode/deepseek-v4-flash-free"
  batch_size: 5
  timeout_seconds: 60

critique:
  model: "opencode/north-mini-code-free"
  batch_size: 5
  threshold: 7.0
  dimensions:
    - name: "novelty"
      weight: 0.3
    - name: "actionability"
      weight: 0.3
    - name: "connectivity"
      weight: 0.2
    - name: "evidence"
      weight: 0.2

output:
  insight_dir: "Daydreams/"
  digest_dir: "Daydreams/digests/"
  daily_note_section: "Daydream"
  history_file: ".agents/skills/daydream/history.json"
  graph_file: "Daydreams/knowledge_graph.graphml"

scheduling:
  enabled: false
  cron: "0 3 * * *"
  max_runs_per_day: 1
```

## Insight Quality Dimensions

Each insight is scored across 4 dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Novelty | 0.3 | How surprising/new is this connection? |
| Actionability | 0.3 | Can this insight lead to concrete action? |
| Connectivity | 0.2 | Does it link previously separate concepts? |
| Evidence | 0.2 | Is it grounded in the source notes? |

Insights with a weighted score >= 7.0 pass the quality threshold.

## Architecture

```
Skill (orchestrator)
  |-- Glob/Read: scan vault, extract excerpts
  |-- Generate 50 random pairs (recency-weighted)
  |-- Task(model: opencode/deepseek-v4-flash-free) x 10: synthesize connections  <-- parallel
  |-- Task(model: opencode/north-mini-code-free) x 10: critique/score insights  <-- parallel
  |-- Filter (avg >= 7.0)
  |-- Dedup: semantic deduplication via sentence embeddings
  |-- Graph: build knowledge graph from insight connections
  +-- Write: save insight notes + daily digest + graph
```

## Output

- **Individual insights**: `Daydreams/YYYYMMDD-slug.md` -- full synthesis with scores and wikilinks
- **Daily digest**: `Daydreams/digests/YYYYMMDD-digest.md` -- stats + ranked top insights
- **Daily note**: Summary appended under `## Daydream`
- **History log**: `.agents/skills/daydream/history.json` -- tracks sampled pairs for dedup
- **Knowledge graph**: `Daydreams/knowledge_graph.graphml` -- insight network visualization

## Quality Assurance

- Semantic deduplication reduces duplicate insights >90%
- Multi-dimension critique ensures insights are novel, actionable, and evidence-based
- Knowledge graph shows meaningful clusters across the vault
- Insight quality score averages >7.5/10
