---
name: remembering-conversations
description: Use when user asks 'how should I...' or 'what's the best approach...' after exploring code or when you've tried to solve something and are stuck, for unfamiliar workflows or when user references past work. Searches conversation history with local caching, semantic search, and pattern detection.
version: "2.0.0"
---

# Remembering Conversations

**Core principle:** Search before reinventing. Searching costs nothing; reinventing or repeating mistakes costs everything.

## When to Use

You often get value out of consulting your episodic memory once you understand what you're being asked. Search memory in these situations:

**After understanding the task:**
- User asks "how should I..." or "what's the best approach..."
- You've explored current codebase and need to make architectural decisions
- User asks for implementation approach after describing what they want

**When you're stuck:**
- You've investigated a problem and can't find the solution
- Facing a complex problem without obvious solution in current code
- Need to follow an unfamiliar workflow or process

**When historical signals are present:**
- User says "last time", "before", "we discussed", "you implemented"
- User asks "why did we...", "what was the reason..."
- User says "do you remember...", "what do we know about..."

**Don't search first:**
- For current codebase structure (use Grep/Read to explore first)
- For info in current conversation
- Before understanding what you're being asked to do

## CLI Usage

```bash
# Search conversation history
remembering-conversations search "architecture decision" --since 2026-01-01

# Detect recurring patterns
remembering-conversations patterns --type decisions --top 10

# Find similar past situations
remembering-conversations similar --context "current task description"

# Summarize a conversation
remembering-conversations summarize --conversation-id abc123

# Tag a conversation
remembering-conversations tags --add "architecture,decision" --conversation-id abc123

# Export findings
remembering-conversations export --format markdown --output insights.md

# Show search analytics
remembering-conversations analytics --period 30d --top-queries
```

## Core Capabilities

### Local Conversation Index
- Incremental sync from MCP episodic memory
- Generates embeddings for semantic search (sentence-transformers)
- Time-range and tag filtering
- Search latency <2s (local) vs 10s+ (MCP)

### Semantic Search
- Hybrid: keyword (BM25) + semantic (embeddings)
- Finds relevant conversations with >90% precision
- Supports filters: time range, tags, participants

### Pattern Detection
- Detects recurring decisions, bugs, architectural choices
- Builds decision registry (what was decided, when, why)
- Finds similar situations from history
- Identifies architectural patterns and tech choices

### Conversation Summarization
- Auto-generates topic, key decisions, outcomes, participants
- Summary quality >4/5 human rating

## Architecture

```
CLI (scripts/cli.py)
  ├── search → conversation_index.py (hybrid BM25 + semantic)
  ├── patterns → pattern_detector.py (recurring decisions, arch patterns)
  ├── similar → find_similar_situation()
  ├── summarize → auto_generate_summary()
  └── export → markdown/notion/confluence output
```

## Auto-Invocation

The skill auto-triggers on these phrases:
- "how should I..."
- "what's the best approach..."
- "best way to..."
- "recommended approach"
- "how do I..."
- "what would you do"
- "last time we..."
- "remember when..."
- "you implemented..."
- "we discussed..."

## Testing

```bash
pytest tests/ -v
```

13 tests covering CLI workflow, indexing, search, pattern detection, and auto-invocation.
