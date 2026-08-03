# Improvement Plan: remembering-conversations

## Current State Assessment

**Tier:** 🟡 Strong Core (Needs Structure/Polish)
**Lines:** 65 | **Version:** 1.0 (implied)

### Strengths
- Clear core principle (search before reinventing)
- Mandatory search agent dispatch with exact template
- 4 trigger categories with specific scenarios
- Discourages direct MCP tool usage (saves context)
- Context saving claim (50-100x vs raw conversations)

### Gaps Identified
1. **No local caching** - Every search hits MCP, no local index
2. **No semantic search** - Keyword only, no embedding-based
3. **No conversation summarization** - Raw results only
4. **No pattern detection** - Can't find recurring themes/decisions
5. **No integration with skills** - Standalone, not auto-invoked
6. **No search analytics** - No metrics on search effectiveness
7. **No conversation tagging** - Can't categorize conversations
8. **No export/sharing** - Can't share findings with team
9. **No time-range filtering** - All history or nothing
10. **No search suggestions** - No autocomplete or related queries

---

## Improvement Roadmap

### Phase 1: Local Intelligence (Week 1)
- [ ] Build local conversation index (incremental sync from MCP)
- [ ] Add semantic search with embeddings
- [ ] Implement conversation summarization (auto-generate topics)
- [ ] Add time-range and tag filtering

### Phase 2: Pattern Detection (Week 2)
- [ ] Detect recurring patterns (decisions, bugs, architectural choices)
- [ ] Build decision registry (what was decided, when, why)
- [ ] Add "similar situation" detection
- [ ] Create knowledge graph from conversations

### Phase 3: Automation & Integration (Week 3)
- [ ] Auto-invoke on trigger phrases ("how should I", "best approach")
- [ ] Integrate with `skill-creator` (reuse past skill patterns)
- [ ] Integrate with `project-planner` (reuse past plans)
- [ ] Add search suggestions/autocomplete

### Phase 4: Team & Analytics (Week 4)
- [ ] Team-shared conversation index (with privacy controls)
- [ ] Search analytics dashboard (what's searched, what's found)
- [ ] Export findings as markdown/notion/confluence
- [ ] Add conversation tagging UI

---

## Specific Technical Tasks

### Local Index
```python
# index.py
class ConversationIndex:
    def __init__(self, cache_dir: Path = Path(".conversation_cache")):
        self.cache_dir = cache_dir
        self.embeddings_path = cache_dir / "embeddings.npy"
        self.metadata_path = cache_dir / "metadata.json"
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def sync(self, since: datetime = None):
        # Incremental sync from MCP episodic memory
        # Generate embeddings for new conversations
        # Update metadata (participants, topics, timestamps)
        pass
    
    def search(self, query: str, k: int = 10,
               time_range: TimeRange = None,
               tags: List[str] = None) -> List[SearchResult]:
        # Hybrid: keyword (BM25) + semantic (embeddings)
        # Apply filters
        # Return ranked results with snippets
        pass
    
    def get_summary(self, conversation_id: str) -> ConversationSummary:
        # Auto-generate: topic, key decisions, outcomes, participants
        pass
```

### Pattern Detection
```python
# patterns.py
class PatternDetector:
    def detect_recurring_decisions(self, conversations: List[Conversation]) -> List[DecisionPattern]:
        # Cluster similar decisions
        # Extract: context, options considered, choice made, rationale
        # Return patterns with frequency and outcomes
        pass
    
    def detect_architectural_patterns(self, conversations: List[Conversation]) -> List[ArchPattern]:
        # Find: tech choices, framework selections, design patterns
        # Track: adoption, migration, deprecation
        pass
    
    def find_similar_situation(self, current_context: str) -> List[SimilarSituation]:
        # Embed current context
        # Find similar past situations
        # Return: what was done, outcome, lessons
        pass
```

### Auto-Invocation
```python
# auto_invoke.py
TRIGGER_PHRASES = [
    "how should i",
    "what's the best approach",
    "best way to",
    "recommended approach",
    "how do i",
    "what would you do",
    "last time we",
    "remember when",
    "you implemented",
    "we discussed"
]

def should_search(message: str) -> bool:
    message_lower = message.lower()
    return any(phrase in message_lower for phrase in TRIGGER_PHRASES)

async def auto_search(message: str, context: ConversationContext) -> SearchResult:
    # Extract key terms from message
    # Search with context-aware query
    # Return synthesized insights
    pass
```

### CLI Design
```bash
# remembering-conversations search "architecture decision" --since 2026-01-01
# remembering-conversations patterns --type decisions --top 10
# remembering-conversations similar --context "current task description"
# remembering-conversations summarize --conversation-id abc123
# remembering-conversations tags --add "architecture,decision" --conversation-id abc123
# remembering-conversations export --format markdown --output insights.md
# remembering-conversations analytics --period 30d --top-queries
```

---

## Acceptance Criteria
- [ ] Local index syncs in <30s for 1000 conversations
- [ ] Semantic search finds relevant conversations >90% precision
- [ ] Pattern detection identifies >80% of recurring decisions
- [ ] Auto-invoke triggers on >90% of trigger phrases
- [ ] Search latency <2s (local) vs 10s+ (MCP)
- [ ] Summary quality >4/5 human rating
- [ ] Export produces usable documentation

---

## Dependencies
- `skill-creator` (pattern reuse)
- `project-planner` (plan reuse)
- `ai-self-reflection` (conversation analysis)
- `code-quality` (CLI code)
- `verification-before-completion` (search effectiveness claims)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Privacy concerns | Medium | High | Local-only, opt-in sharing, encryption |
| Index staleness | Medium | Low | Incremental sync, manual refresh |
| Embedding drift | Low | Medium | Periodic re-indexing |
| False pattern detection | Medium | Medium | Confidence thresholds, human validation |

---

## Success Metrics
- Search usage: >5 searches/session
- Pattern reuse: >30% of decisions reference past
- Auto-invoke accuracy: >85% relevant
- Time saved: >50% vs manual search
- Team adoption: >60% of team members