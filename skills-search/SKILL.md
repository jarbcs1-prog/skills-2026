---
name: skills-search
description: |
  Unified skill discovery, installation, and management for AI agent skills ecosystem. Combines semantic search, quality verification, dependency resolution, and OpenCode CLI integration. Use when: searching for skills, discovering capabilities, installing/updating/removing skills, getting recommendations, managing skill dependencies, or bootstrapping the skills ecosystem.
version: "2.0.0"
---

# Skills Search — Unified Skill Discovery & Management

Unified skill search combining semantic discovery, quality verification, dependency resolution, and OpenCode CLI integration.

## When to Use

- **Search/Discover:** "find skills for X", "search X skills", "what skills exist for Y"
- **Install/Manage:** "install X", "add X skill", "update skills", "remove X", "list my skills"
- **Learn:** "what does X do", "tell me about X skill"
- **Recommend:** "I need help with PDF/React/testing...", "recommend skills for my project"
- **Compose:** "combine code-reviewer and TDD into workflow"
- **Bootstrap:** First-time setup of skills ecosystem

---

## Quick Start

```bash
# Auto-bootstrap (installs opencode CLI if needed)
skills-search bootstrap

# Search with semantic understanding
skills-search find "react performance optimization" --semantic --limit 10

# Popular/recent discovery
skills-search popular --limit 20
skills-search recent --limit 10

# Install with quality verification
skills-search install vercel-labs/agent-skills@react-best-practices --verify --quality-gate 70

# Manage installed skills
skills-search list --format table
skills-search info react-best-practices --detailed
skills-search update --all --dry-run
skills-search uninstall old-skill

# Project-aware recommendations
skills-search recommend --project . --top 5

# Skill composition
skills-search compose --skills "code-reviewer,test-driven-development" --name my-workflow

# Dependency management
skills-search lock --generate lock.json
skills-search sync --offline
```

---

## Core Capabilities

### 1. Semantic Search
- Local embedding index (cached from skills.sh + local skills)
- Hybrid search: keyword (BM25) + semantic (embeddings)
- Offline-capable with cached index
- Filters: category, min_installs, source, tags, author

### 2. Quality Verification
- Install count thresholds (5K+ preferred, <1K caution)
- Source reputation (official orgs preferred)
- GitHub stars validation (>100 stars)
- **Skill-judge integration** — blocks skills <70/120
- Post-install validation (structure, tests, triggers)

### 3. Dependency Resolution
- Skill manifest parsing (skill.yaml)
- Conflict detection (version, circular)
- Lock file generation (lock.json)
- Topological install order

### 4. Project-Aware Recommendations
- Analyzes project structure (package.json, Cargo.toml, etc.)
- Maps tech stack to relevant skills
- Suggests skill compositions (common combinations)

### 5. OpenCode CLI Integration
- Direct `opencode` command execution
- Auto-bootstrap (installs opencode if missing)
- MCP server support for native integration
- Namespaced skills (`@org/skill-name`)

---

## Search & Discovery

### Semantic Search
```bash
# Natural language queries
skills-search find "how to optimize React rendering" --semantic
skills-search find "database migration tools" --semantic --category devops

# Keyword search (fallback)
skills-search find "react performance" --keyword

# With filters
skills-search find "testing" --min-installs 5000 --author vercel-labs --tags "react,frontend"
```

### Discovery Commands
```bash
# Most downloaded
skills-search popular --limit 20 --category "Web Development"

# Recently published/updated
skills-search recent --limit 10 --days 30

# By category
skills-search category "Testing" --limit 15

# Detailed skill info
skills-search info react-best-practices --detailed --show-dependencies
```

---

## Installation & Management

### Install with Verification
```bash
# Basic install (user-level)
skills-search install vercel-labs/agent-skills@react-best-practices

# Project-level install
skills-search install @daymade/skill-creator --project

# Force reinstall
skills-search install skill-name --force

# With quality gate (requires skill-judge >= 70)
skills-search install skill-name --verify --quality-gate 70

# Dry-run (show what would happen)
skills-search install skill-name --dry-run
```

### Post-Install
```
> Skill installed successfully. Please restart your agent (or start a new conversation) for the skill to become available.
```

### Update & Maintenance
```bash
# Update specific skill
skills-search update react-best-practices

# Update all skills
skills-search update --all

# Dry-run updates
skills-search update --all --dry-run

# Check for updates without installing
skills-search check --outdated
```

### Uninstall
```bash
skills-search uninstall skill-name
skills-search uninstall @org/skill-name --project
```

### List & Info
```bash
# List installed
skills-search list --format table|json|yaml

# Detailed info
skills-search info skill-name --detailed
skills-search info skill-name --show-dependencies
skills-search info skill-name --show-versions
```

---

## Recommendations & Composition

### Project-Aware Recommendations
```bash
# Analyze current project and recommend skills
skills-search recommend --project . --top 5

# With specific context
skills-search recommend --project . --context "adding authentication" --top 3

# Export recommendations
skills-search recommend --project . --output recommendations.md
```

### Skill Composition
```bash
# Create workflow from multiple skills
skills-search compose --skills "code-reviewer,test-driven-development,systematic-debugging" --name quality-workflow

# With custom orchestration
skills-search compose --skills "prompt-engineering,skill-creator" --name prompt-dev --orchestration sequential

# Export composed workflow
skills-search compose --skills "..." --name my-workflow --export workflow.yaml
```

---

## Dependency Management

### Lock File
```bash
# Generate lock file from installed skills
skills-search lock --generate lock.json

# Install from lock file (reproducible)
skills-search lock --install lock.json

# Check for updates respecting lock
skills-search lock --check-updates lock.json
```

### Dependency Resolution
```bash
# Show dependency tree
skills-search deps --tree

# Check for conflicts
skills-search deps --conflicts

# Resolve and install missing deps
skills-search deps --install-missing
```

---

## Offline Mode

```bash
# Sync index for offline use
skills-search sync --offline --cache-dir .skills_cache

# Search offline
skills-search find "react hooks" --offline

# Full offline install (from cached .skill files)
skills-search install skill-name --offline --cache-dir .skills_cache
```

---

## Quality Verification Details

### Pre-Install Checks
1. **Structure validation** — SKILL.md, scripts/, references/, tests/
2. **Trigger precision** — Description matches triggering scenarios
3. **Skill-judge score** — Must pass threshold (default 70/120)
4. **Security scan** — No hardcoded secrets, safe scripts
5. **Test execution** — Runs skill's test suite if present

### Post-Install Validation
```bash
skills-search verify --skill ./skill-name --strict
```

### Quality Tiers
| Tier | Min Installs | Source | Skill-Judge | Use Case |
|------|-------------|--------|-------------|----------|
| **Verified** | 10K+ | Official orgs | 90+ | Production |
| **Trusted** | 5K+ | Known orgs | 80+ | General use |
| **Community** | 1K+ | Any | 70+ | Evaluation |
| **Experimental** | <1K | Any | <70 | Testing only |

---

## Configuration

### Config File (`~/.config/skills-search/config.yaml`)
```yaml
version: 2
registry:
  primary: "https://skills.sh/api"
  fallback: ["https://registry.npmmirror.com", "local"]
  cache_ttl_hours: 24

search:
  semantic_enabled: true
  embedding_model: "all-MiniLM-L6-v2"
  hybrid_weight_keyword: 0.4
  hybrid_weight_semantic: 0.6
  max_results: 20

quality:
  min_installs_preferred: 5000
  min_installs_caution: 1000
  preferred_sources: ["vercel-labs", "anthropics", "microsoft", "daymade"]
  skill_judge_threshold: 70
  require_tests: false

install:
  default_scope: "user"  # user | project
  auto_verify: true
  verify_timeout: 120
  post_install_restart_reminder: true

recommendations:
  project_analysis_enabled: true
  composition_suggestions: true
  max_recommendations: 5

offline:
  enabled: false
  cache_dir: "~/.skills_cache"
  sync_on_startup: true

mcp:
  enabled: true
  server: "skills-search-mcp"
```

---

## OpenCode CLI Integration

### Direct Command Execution
The skill **MUST directly execute** `opencode` commands via shell tool:

```bash
# Search
opencode search "react performance" --limit 10

# Popular
opencode popular --limit 20

# Install
opencode install vercel-labs/agent-skills@react-best-practices

# List
opencode list

# Info
opencode info react-best-practices

# Update
opencode update --all

# Uninstall
opencode uninstall skill-name
```

### Fallback
If `opencode` not found:
```bash
npx @opencode-cli search "react performance"
```

### MCP Server (Native Integration)
```json
{
  "mcpServers": {
    "skill-search": {
      "command": "npx",
      "args": ["-y", "skills-search-mcp"]
    }
  }
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `opencode: command not found` | Run `skills-search bootstrap` or `npm install -g @opencode-cli` |
| Skill not available after install | Restart agent — skills load at startup |
| Permission errors | Check `~/.agents/skills/` write access; use `--project` flag |
| Registry unreachable | Use `--offline` mode with cached index |
| Quality gate failed | Check skill-judge output; try `--quality-gate 60` or install anyway |
| Dependency conflict | Run `skills-search deps --conflicts` and resolve manually |
| Semantic search not working | Run `skills-search sync` to rebuild index |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-08-03 | Unified find-skills + skills-search; semantic search, quality gates, dependency resolution, composition |
| 1.0.0 | 2026-07-15 | Initial find-skills |
| 1.0.0 | 2026-07-20 | Initial skills-search |

---

## License

MIT License — Use freely with your AI agents.

## Testing

```bash
pytest tests/ -v
```

23 tests covering CLI commands, local index, semantic search, dependency resolution, and skill composition.