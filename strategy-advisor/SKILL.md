---
name: strategy-advisor
description: Use when making strategic decisions, evaluating business options, setting direction, analyzing trade-offs, or when user mentions strategy, business planning, competitive analysis or long-term planning.
version: "2.0.0"
---

# Strategy Advisor

Strategic analysis, decision matrices, scenario planning, and templates for high-level business decisions.

## When to Use

- Evaluating strategic options
- Making high-impact business decisions
- Conducting competitive analysis
- Setting organizational direction
- Assessing market opportunities
- Planning long-term initiatives

## CLI Usage

```bash
# Run a strategic framework analysis
strategy-advisor analyze --framework swot --topic "enterprise AI market entry"

# Evaluate options with a weighted decision matrix
strategy-advisor decide --options "build,buy,partner" --criteria "cost,time,risk,control" --weights "0.3,0.3,0.2,0.2"

# Generate strategy scenarios (best/base/worst case + Monte Carlo)
strategy-advisor scenario --strategy "acquire startup" --variables "integration_cost,market_growth,retention" --monte-carlo --iterations 1000

# Render a strategy template
strategy-advisor template --type market_entry --topic "AI product launch" --output strategy.md

# Define strategy monitoring KPIs
strategy-advisor monitor --strategy "product_launch" --kpis "adoption,revenue,churn"
```

## Supported Frameworks

| Framework | Dimensions | Output |
|-----------|-----------|--------|
| Porter's Five Forces | 5 competitive forces | Industry attractiveness + strategic implications |
| SWOT | Strengths, Weaknesses, Opportunities, Threats | SO/WO/ST/WT strategic options |
| PESTLE | Political, Economic, Social, Technological, Legal, Environmental | Macro drivers + response priorities |
| BCG Growth-Share Matrix | Market growth, Relative market share | Stars/Cash Cows/Question Marks/Dogs |
| Ansoff Matrix | Products × Markets | Growth strategy with risk levels |
| Blue Ocean Strategy | 4 actions framework | Value innovation map |
| Competitive Moat | Network effects, Switching costs, Cost advantage, Intangibles, Scale | Moat assessment |

## CLI Commands

| Command | Description |
|---------|-------------|
| `analyze` | Run a strategic framework analysis |
| `decide` | Evaluate options with a weighted decision matrix |
| `scenario` | Generate best/base/worst scenarios with Monte Carlo |
| `template` | Render a pre-built strategy template |
| `monitor` | Define strategy monitoring KPIs |

## Output Format

```markdown
## Strategic Question
[What decision needs to be made?]

## Situation Analysis
- **Current State**: [Where are we now?]
- **Objective**: [Where do we want to go?]
- **Constraints**: [What limits our options?]

## Options Evaluation

### Option 1: [Name]
**Pros**: [Benefits]
**Cons**: [Drawbacks]
**Risk**: [High/Med/Low]

### Option 2: [Name]
[Continue for each option...]

## Recommendation
[Preferred path with clear rationale]

## Implementation Roadmap
[High-level steps to execute]

## Success Metrics
[How to measure if this was the right choice]
```

## Architecture

```
CLI (scripts/cli.py)
  ├── analyze → frameworks.py (7 frameworks)
  ├── decide → decision_matrix.py (weighted scoring + sensitivity)
  ├── scenario → scenario.py (best/base/worst + Monte Carlo)
  ├── template → templates.py (10+ pre-built templates)
  └── monitor → KPI tracking with thresholds
```

## Testing

```bash
pytest tests/ -v
```

36 tests covering frameworks, decision matrix, scenario planning, templates, and CLI.
