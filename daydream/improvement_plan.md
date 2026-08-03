# Improvement Plan: daydream

## Current State Assessment

**Tier:** 🟡 Strong Core (Needs Structure/Polish)
**Lines:** 47 | **Version:** 1.0 (implied)

### Strengths
- Clear multi-agent architecture with parallel synthesis/critique
- Recency-weighted random pair sampling
- Quality filtering with score threshold (>=7.0)
- Structured output: insights, digests, daily notes, history
- No external dependencies (pure Opencode tools)
- Vault auto-detection

### Gaps Identified
1. **No configuration** - Hardcoded parameters (50 pairs, 7.0 threshold, 120 days)
2. **No insight quality metrics** - Only critic score, no diversity/novelty
3. **No deduplication across runs** - History tracks pairs but not semantic duplicates
4. **No topic steering** - Can't guide toward specific themes
5. **No insight linking** - Insights don't connect to form knowledge graph
6. **No export/integration** - Obsidian-only output
7. **No scheduling** - Manual `/daydream` invocation only
8. **No critic calibration** - Fixed model, no quality validation
9. **No insight evolution** - Insights don't update/merge over time
10. **No analytics** - No metrics on insight quality, user engagement

---

## Improvement Roadmap

### Phase 1: Configuration & Quality (Week 1)
- [ ] Add `.daydream.yml` config with all tunable parameters
- [ ] Implement semantic deduplication (embedding-based)
- [ ] Add insight quality dimensions: novelty, actionability, connectivity
- [ ] Create critic calibration with golden set

### Phase 2: Intelligence & Steering (Week 2)
- [ ] Add topic steering (tags, keywords, note selection bias)
- [ ] Implement insight linking (auto-wikilink related insights)
- [ ] Add knowledge graph generation (insights as nodes, connections as edges)
- [ ] Create insight evolution (merge similar, update outdated)

### Phase 3: Automation & Integration (Week 3)
- [ ] Add cron/systemd scheduling with configurable frequency
- [ ] Implement export formats: JSON, GraphML, Markdown index
- [ ] Add Obsidian plugin integration (ribbon, commands, views)
- [ ] Create API for external consumption

### Phase 4: Analytics & Learning (Week 4)
- [ ] Build insight analytics dashboard
- [ ] Implement user feedback loop (rate insights, improve critic)
- [ ] Add insight-to-action tracking (which insights led to work)
- [ ] Create collective intelligence (cross-vault patterns)

---

## Specific Technical Tasks

### Configuration
```yaml
# .daydream.yml
vault:
  path: "auto"  # or explicit path
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
  prompt_template: "references/synthesis_prompt.md"

critique:
  model: "opencode/north-mini-code-free"
  batch_size: 5
  timeout_seconds: 30
  dimensions:
    - name: "novelty"
      weight: 0.3
      description: "How surprising/new is this connection?"
    - name: "actionability"
      weight: 0.3
      description: "Can this insight lead to concrete action?"
    - name: "connectivity"
      weight: 0.2
      description: "Does it link previously separate concepts?"
    - name: "evidence"
      weight: 0.2
      description: "Is it grounded in the source notes?"
  threshold: 7.0
  calibration_set: "references/golden_insights.json"

output:
  insight_dir: "Daydreams/"
  digest_dir: "Daydreams/digests/"
  daily_note_section: "Daydream"
  history_file: ".agents/skills/daydream/history.json"
  graph_file: "Daydreams/knowledge_graph.graphml"

scheduling:
  enabled: false
  cron: "0 3 * * *"  # 3 AM daily
  max_runs_per_day: 1

steering:
  enabled: false
  tags: []  # e.g., ["project:alpha", "area:research"]
  keywords: []
  boost_recent: true
```

### Semantic Deduplication
```python
# deduplication.py
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticDeduplicator:
    def __init__(self, threshold: float = 0.85):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = threshold
        self.embeddings_cache = {}
    
    def is_duplicate(self, new_insight: Insight, existing: List[Insight]) -> bool:
        new_emb = self.embed(new_insight.content)
        for ex in existing:
            ex_emb = self.embed(ex.content)
            similarity = np.dot(new_emb, ex_emb)
            if similarity > self.threshold:
                return True
        return False
    
    def embed(self, text: str) -> np.ndarray:
        if text not in self.embeddings_cache:
            self.embeddings_cache[text] = self.model.encode(text)
        return self.embeddings_cache[text]
```

### Knowledge Graph
```python
# knowledge_graph.py
import networkx as nx

class InsightGraph:
    def __init__(self):
        self.graph = nx.Graph()
    
    def add_insight(self, insight: Insight):
        # Add node
        self.graph.add_node(insight.id, 
                           content=insight.content,
                           score=insight.score,
                           date=insight.date,
                           tags=insight.tags)
        
        # Add edges to related insights
        for related_id in insight.related_insights:
            if self.graph.has_node(related_id):
                self.graph.add_edge(insight.id, related_id, 
                                  weight=insight.connection_strength)
    
    def get_clusters(self, min_size: int = 3) -> List[List[str]]:
        # Community detection for thematic clusters
        communities = nx.algorithms.community.greedy_modularity_communities(self.graph)
        return [list(c) for c in communities if len(c) >= min_size]
    
    def export_graphml(self, path: Path):
        nx.write_graphml(self.graph, path)
```

### Scheduling
```bash
# scripts/schedule_daydream.sh
#!/bin/bash
# Install as systemd timer or cron job

# Systemd:
# [Unit]
# Description=Daily Vault Daydream
# [Timer]
# OnCalendar=daily
# Persistent=true
# [Install]
# WantedBy=timers.target

# Cron:
# 0 3 * * * /path/to/daydream/run.sh >> /var/log/daydream.log 2>&1
```

---

## Acceptance Criteria
- [ ] Config file controls all parameters with validation
- [ ] Semantic deduplication reduces duplicate insights >90%
- [ ] Quality dimensions correlate with user ratings >0.7
- [ ] Topic steering increases relevant insights >50%
- [ ] Knowledge graph shows meaningful clusters
- [ ] Scheduling runs reliably for 30+ days
- [ ] Export formats work with Obsidian plugins
- [ ] Analytics dashboard shows insight quality trends

---

## Dependencies
- `code-quality` (script validation)
- `verification-before-completion` (quality claims)
- `writing-skills` (prompt templates)
- `skill-creator` (if making this a distributable skill)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Model hallucination | Medium | High | Golden set calibration, evidence grounding |
| Vault size scaling | Low | Medium | Incremental indexing, sampling |
| Insight noise | High | Medium | Multi-dimension critique, user feedback |
| Scheduling failures | Low | High | Health checks, alerting, manual trigger |

---

## Success Metrics
- Insight quality score: avg >7.5/10
- Novelty rate: >60% new connections per run
- User engagement: >30% insights rated/actioned
- Deduplication: >90% semantic duplicates caught
- Graph clustering: >5 meaningful clusters/vault
- Scheduling uptime: >99%