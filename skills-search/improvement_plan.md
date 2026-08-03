# Improvement Plan: skills-search

## Current State Assessment

**Tier:** 🟡 Strong Core (Needs Structure/Polish)
**Lines:** 107 | **Version:** 1.0 (implied)

### Strengths
- Auto-bootstrap sequence (install opencode if missing)
- Clear intent mapping table (user intent → opencode command)
- Opencode-native MCP integration
- Direct execution mandate (no copy-paste)
- Comprehensive command reference
- Post-install refresh guidance
- Troubleshooting section
- Namespaced skill support

### Gaps Identified
1. **Duplicate with find-skills** - Both search/install skills, should merge
2. **No semantic search** - Keyword only via opencode CLI
3. **No local skill index** - Depends entirely on opencode registry
4. **No skill recommendations** - No context-aware suggestions
5. **No dependency resolution** - Can't handle skill chains
6. **No version management** - No pinning, upgrading, rollback
7. **No offline mode** - Requires internet
8. **No analytics** - No search/usage metrics
9. **No skill composition** - Can't combine skills
10. **No quality verification** - Installs without validation

---

## Improvement Roadmap

### Phase 1: Merge with find-skills (Week 1)
- [ ] **Merge into unified `skills-search` skill** (find-skills is more comprehensive)
- [ ] Keep opencode CLI integration from this skill
- [ ] Add semantic search from find-skills
- [ ] Unify command interface

### Phase 2: Local Intelligence (Week 2)
- [ ] Build local skill index with embeddings
- [ ] Add skill recommendation engine
- [ ] Implement dependency resolution
- [ ] Add version lock file

### Phase 3: Quality & Safety (Week 3)
- [ ] Post-install validation (run skill tests)
- [ ] Quality gate (skill-judge score threshold)
- [ ] Security scan before install
- [ ] Rollback on failed validation

### Phase 4: Ecosystem (Week 4)
- [ ] Team skill sharing
- [ ] Skill composition (workflow builder)
- [ ] Analytics dashboard
- [ ] Offline mode with cached index

---

## Merge Recommendation

**STRONGLY RECOMMEND MERGE** with `find-skills` because:

1. **Same purpose**: Both search, discover, install, manage skills
2. **Complementary strengths**:
   - find-skills: 6-step process, quality verification, leaderboard check, semantic search design
   - skills-search: opencode CLI integration, auto-bootstrap, direct execution, MCP support
3. **User confusion**: Two skills for same task
4. **Maintenance burden**: Duplicate functionality

---

## Merge Plan

### Unified Skill: `skills-search` (enhanced)

#### Combined Capabilities
1. **opencode CLI integration** (from skills-search)
   - Direct command execution
   - Auto-bootstrap
   - MCP server support
2. **Quality verification** (from find-skills)
   - Install count thresholds
   - Source reputation check
   - GitHub stars validation
4. **Semantic search** (from find-skills design)
   - Local embedding index
   - Hybrid keyword + semantic
   - Offline capable
5. **Dependency management** (new)
   - Skill manifest parsing
   - Conflict detection
   - Lock file generation
6. **Recommendations** (new)
   - Project context awareness
   - Skill composition suggestions

#### Unified Interface
```bash
# Search
skills-search find "react performance" --semantic --limit 10
skills-search popular --limit 20
skills-search recent --limit 10

# Install with validation
skills-search install vercel-labs/agent-skills@react-best-practices --verify --quality-gate 70

# Manage
skills-search list --format table
skills-search info react-best-practices --detailed
skills-search update --all --dry-run
skills-search uninstall old-skill

# Advanced
skills-search recommend --project . --top 5
skills-search compose --skills "code-reviewer,test-driven-development" --name my-workflow
skills-search lock --generate lock.json
skills-search sync --offline
```

---

## Acceptance Criteria (Post-Merge)
- [ ] Single skill handles all skill management
- [ ] Semantic search finds relevant skills >90% precision
- [ ] Quality gate blocks <70/120 skill-judge skills
- [ ] Dependency resolution handles 10+ skill chains
- [ ] Offline mode works for cached skills
- [ ] Recommendations match project needs >80%
- [ ] Auto-bootstrap works on fresh machine

---

## Dependencies
- `find-skills` (merge source - comprehensive process)
- `skill-judge` (quality gate)
- `skill-creator` (validation)
- `code-quality` (CLI code)
- `verification-before-completion` (install verification claims)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| CLI breaking changes | Medium | High | Version pinning, compatibility layer |
| Registry API changes | Medium | High | Multiple registry support |
| Semantic search accuracy | Medium | Medium | Fallback to keyword, user feedback |

---

## Success Metrics
- Search relevance: >90% user satisfaction
- Install success rate: >95%
- Recommendation click-through: >40%
- Offline usage: >20% of searches
- Skill composition adoption: >10 workflows created