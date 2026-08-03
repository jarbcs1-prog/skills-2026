# Summarization Schemas — Complete Reference

This document defines all structured summarization schemas used in the Dynamic Context Pruning Skill.

---

## Core Principle: Structured Outputs Only

**Never use free-form summarization.** Always use structured outputs with explicit schemas.

**Why:**
- Free-form text loses critical information
- Ambiguity in extraction
- Hard to validate quality
- Hard to use programmatically
- Higher hallucination risk

**Schema enforces:** Specific, actionable, extractable data points.

---

## Available Schemas

### 1. `agent_default` — General Agent Summary (6 Fields)
**Best for:** Generic agents, coding assistants, general tasks

```json
{
  "fields": [
    "files_modified",
    "user_goals",
    "current_state",
    "pending_actions",
    "errors_encountered",
    "key_decisions"
  ],
  "required": ["user_goals", "current_state"],
  "description": "General agent summary with 6 fields"
}
```

#### Field Specifications

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `files_modified` | `string[]` | Files created/modified/deleted with brief change description | `["src/auth.py: Added JWT validation", "tests/test_auth.py: Added expiry tests"]` |
| `user_goals` | `string[]` | Primary user objectives/requests (last 5) | `["Refactor auth to JWT", "Add rate limiting"]` |
| `current_state` | `string` | Concise agent state: key vars, active processes, env factors | `"Implementing JWT validation in auth.py. Tests passing. Next: refresh token support."` |
| `pending_actions` | `string[]` | Immediate next steps/planned actions | `["Add refresh token endpoint", "Add token revocation", "Update docs"]` |
| `errors_encountered` | `string[]` | Significant errors/warnings with resolution status | `["JWT decode failed: expired token - fixed by adding expiry check"]` |
| `key_decisions` | `string[]` | Important decisions with rationale/alternatives | `["Chose HS256 over RS256: simpler for single-service deployment"]` |

---

### 2. `opencode_5_heading` — OpenCode Standard (5 Fields)
**Best for:** OpenCode agents, follows OpenCode's 5-heading convention

```json
{
  "fields": [
    "current_state",
    "completed_actions",
    "pending_actions",
    "key_decisions",
    "errors_encountered"
  ],
  "required": ["current_state", "pending_actions"],
  "description": "OpenCode standard 5-heading summary"
}
```

#### Field Specifications

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `current_state` | `string` | What the agent is currently doing, key context | `"Refactoring auth module to use JWT tokens. In progress: token validation middleware."` |
| `completed_actions` | `string[]` | What was finished in this phase | `["Designed JWT payload schema", "Implemented token validation", "Wrote unit tests"]` |
| `pending_actions` | `string[]` | Immediate next steps | `["Add token refresh endpoint", "Add revocation list", "Integration tests"]` |
| `key_decisions` | `string[]` | Architectural/design choices made | `["Use HS256 for simplicity", "Store refresh tokens in Redis with TTL"]` |
| `errors_encountered` | `string[]` | Significant issues with resolution | `["Token expiry not validated - fixed by adding exp claim check"]` |

---

### 3. `minimal` — Token-Critical (2 Fields)
**Best for:** Severe token pressure, emergency summarization

```json
{
  "fields": [
    "current_state",
    "pending_actions"
  ],
  "required": ["current_state", "pending_actions"],
  "description": "Minimal 2-field summary for token-critical situations"
}
```

#### Field Specifications

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `current_state` | `string` | Essential state only | `"Auth refactor 80% done. JWT validation working. Pending: refresh tokens."` |
| `pending_actions` | `string[]` | Only critical next steps | `["Add refresh token endpoint", "Deploy to staging"]` |

---

## Schema Definition Format

```json
{
  "fields": ["field1", "field2", ...],
  "required": ["field1", "field2"],
  "description": "Human-readable description"
}
```

### Validation Rules
1. **All required fields MUST be present** in output
2. **No unknown fields** allowed in output
3. **Field types** must match specification (array vs string)
4. **Content must be derived** from context, not hallucinated

---

## Custom Schema Definition

Users can define custom schemas for domain-specific needs:

```json
{
  "name": "security_audit",
  "fields": [
    "vulnerabilities_found",
    "compliance_status",
    "remediation_actions",
    "risk_score",
    "files_scanned"
  ],
  "required": ["vulnerabilities_found", "compliance_status", "risk_score"],
  "description": "Security audit summary schema"
}
```

### Custom Schema Guidelines
1. **Field names**: snake_case, descriptive
2. **Types**: Prefer arrays for multiple items, strings for narratives
3. **Required**: Minimum 2, maximum 4 required fields
4. **Total fields**: 3-8 recommended (more = more tokens)
4. **Domain alignment**: Fields should map to context entry types

---

## Schema Selection Logic

| Platform | Auto-Selects | Rationale |
|----------|--------------|-----------|
| Generic | `agent_default` | Full context, all fields useful |
| OpenCode | `opencode_5_heading` | Matches OpenCode conventions |
| Token-critical | `minimal` | Emergency reduction |
| Custom | User-defined | Domain-specific needs |

**Auto-selection:**
```python
def select_schema(platform: str, force: str = None) -> str:
    if force: return force
    if platform == "opencode": return "opencode_5_heading"
    return "agent_default"
```

---

## Schema Validation

### Automated Validation
```python
def validate(summary: dict, schema: SummarySchema) -> ValidationResult:
    errors = []
    
    # Check required fields
    for field in schema.required:
        if field not in summary:
            errors.append(f"Missing required field: {field}")
    
    # Check unknown fields
    for field in summary:
        if field not in schema.fields:
            errors.append(f"Unknown field: {field}")
    
    # Type validation
    for field, value in summary.items():
        if field in schema.field_types:
            expected = schema.field_types[field]
            if not isinstance(value, expected):
                errors.append(f"Field {field}: expected {expected}, got {type(value)}")
    
    return ValidationResult(valid=len(errors)==0, errors=errors)
```

### Field Type Mapping
| Field | Expected Type |
|-------|---------------|
| `files_modified` | `list[str]` |
| `user_goals` | `list[str]` |
| `current_state` | `str` |
| `pending_actions` | `list[str]` |
| `errors_encountered` | `list[str]` |
| `key_decisions` | `list[str]` |
| `completed_actions` | `list[str]` |

---

## Summarization Prompt Template

### For `agent_default`
```
Summarize the context below into this EXACT JSON schema:
{
  "files_modified": ["string"],
  "user_goals": ["string"],
  "current_state": "string",
  "pending_actions": ["string"],
  "errors_encountered": ["string"],
  "key_decisions": ["string"]
}

Required: user_goals, current_state
Rules:
- Extract from context ONLY, no hallucination
- Max 5 items per array
- current_state: 1-2 sentences max
- user_goals: last 5 distinct goals from user messages
- files_modified: only files actually touched
- errors_encountered: only significant issues with resolution
- key_decisions: architectural choices with rationale

Context:
{{context_history}}
```

### For `opencode_5_heading`
```
Summarize into this EXACT JSON schema:
{
  "current_state": "string",
  "completed_actions": ["string"],
  "pending_actions": ["string"],
  "key_decisions": ["string"],
  "errors_encountered": ["string"]
}

Required: current_state, pending_actions
Rules:
- OpenCode 5-heading format
- completed_actions: what finished this phase
- pending_actions: immediate next steps (max 5)
- current_state: 1-2 sentences, what/where/why
- errors_encountered: only significant with resolution

Context:
{{context_history}}
```

---

## Quality Metrics

### Coverage Checklist
- [ ] All required fields populated
- [ ] No unknown fields
- [ ] Array fields have ≤5 items
- [ ] String fields ≤500 chars
- [ ] Content traceable to context
- [ ] No hallucinated information

### Automated Validation
```python
def validate_summary(summary, schema_name):
    schema = SCHEMAS[schema_name]
    errors = []
    
    # Required fields
    for req in schema.required:
        if req not in summary:
            errors.append(f"Missing required: {req}")
    
    # Unknown fields
    for field in summary:
        if field not in schema.fields:
            errors.append(f"Unknown field: {field}")
    
    # Type checks
    for field, value in summary.items():
        if field in ["files_modified", "user_goals", "pending_actions", "errors_encountered", "key_decisions", "completed_actions"]:
            if not isinstance(value, list):
                errors.append(f"{field}: expected list, got {type(value)}")
        elif field in ["current_state"]:
            if not isinstance(value, str):
                errors.append(f"{field}: expected string, got {type(value)}")
    
    return {"valid": len(errors) == 0, "errors": errors}
```

---

## Schema Evolution

### Versioning
```json
{
  "schema_version": "1.1",
  "compatible_with": ["1.0"],
  "changes": [
    "Added 'risk_level' to key_decisions",
    "Made 'files_modified' optional"
  ]
}
```

### Migration
```python
def migrate_summary(summary: dict, from_version: str, to_version: str) -> dict:
    if from_version == "1.0" and to_version == "1.1":
        # Add default for new field
        for decision in summary.get("key_decisions", []):
            if "risk_level" not in decision:
                decision["risk_level"] = "medium"
        summary.setdefault("files_modified", [])
    return summary
```

---

## Testing

```bash
# Validate schema compliance
python scripts/test_summarization_schema.py

# Test all schemas
python scripts/test_summarization_schema.py --all

# Benchmark
python scripts/benchmark_context_reduction.py
```

**Expected:** All 3 schemas pass validation, 100% schema compliance.