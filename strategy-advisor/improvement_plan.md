# Improvement Plan: strategy-advisor

## Current State Assessment

**Tier:** 🟠 Functional but Thin (Needs Substantial Expansion)
**Lines:** 84 | **Version:** 1.0 (implied)

### Strengths
- Clear 4-step strategic thinking framework
- Structured output format with all key sections
- Covers situational analysis, option generation, decision criteria, recommendation
- Includes implementation roadmap and success metrics

### Gaps Identified
1. **No analytical tools** - Framework only, no models/calculators
2. **No strategic frameworks library** - Only generic 4-step process
3. **No data integration** - Can't pull market/competitive data
4. **No scenario planning** - Single recommendation only
5. **No decision matrices** - No weighted scoring
6. **No risk quantification** - Qualitative only
7. **No stakeholder analysis** - Mentioned but no framework
8. **No templates** - No pre-built for common decisions
9. **No CLI tooling** - Manual only
10. **No integration with other skills** - Standalone

---

## Improvement Roadmap

### Phase 1: Frameworks & Tools (Week 1)
- [ ] Add strategic frameworks library (Porter's 5 Forces, SWOT, PESTLE, BCG Matrix, Ansoff, Blue Ocean)
- [ ] Build decision matrix calculator
- [ ] Add scenario planning (best/base/worst case)
- [ ] Create risk quantification (Monte Carlo for strategic risks)

### Phase 2: Data & Analysis (Week 2)
- [ ] Integrate market data APIs (Crunchbase, PitchBook, public financials)
- [ ] Add competitive intelligence framework
- [ ] Implement stakeholder analysis (power/interest matrix)
- [ ] Build option generation with creative techniques

### Phase 3: Automation & Templates (Week 3)
- [ ] Create CLI for strategic analysis
- [ ] Build template library (market entry, product launch, M&A, pivot, resource allocation)
- [ ] Add decision documentation with audit trail
- [ ] Implement strategic review cycle

### Phase 4: Integration (Week 4)
- [ ] Connect with `project-planner` (strategy → execution)
- [ ] Connect with `brainstorming` (option generation)
- [ ] Add `systematic-debugging` for strategic assumption validation
- [ ] Create strategy dashboard

---

## Specific Technical Tasks

### Strategic Frameworks Library
```python
# frameworks.py
FRAMEWORKS = {
    "porters_five_forces": {
        "name": "Porter's Five Forces",
        "dimensions": [
            "threat_of_new_entrants",
            "bargaining_power_suppliers",
            "bargaining_power_buyers",
            "threat_of_substitutes",
            "competitive_rivalry"
        ],
        "scoring": "1-5 scale per force",
        "output": "Industry attractiveness score + strategic implications"
    },
    "swot": {
        "name": "SWOT Analysis",
        "dimensions": ["strengths", "weaknesses", "opportunities", "threats"],
        "scoring": "Impact x Likelihood matrix",
        "output": "Strategic options per quadrant (SO, WO, ST, WT strategies)"
    },
    "pestle": {
        "name": "PESTLE Analysis",
        "dimensions": ["political", "economic", "social", "technological", "legal", "environmental"],
        "scoring": "Trend direction + impact assessment",
        "output": "Macro drivers + strategic response priorities"
    },
    "bcg_matrix": {
        "name": "BCG Growth-Share Matrix",
        "dimensions": ["market_growth_rate", "relative_market_share"],
        "quadrants": ["stars", "cash_cows", "question_marks", "dogs"],
        "output": "Portfolio strategy per business unit"
    },
    "ansoff_matrix": {
        "name": "Ansoff Matrix",
        "dimensions": ["products", "markets"],
        "quadrants": ["market_penetration", "market_development", "product_development", "diversification"],
        "output": "Growth strategy options with risk levels"
    },
    "blue_ocean": {
        "name": "Blue Ocean Strategy",
        "tools": ["strategy_canvas", "four_actions_framework", "eliminate_reduce_raise_create"],
        "output": "Value innovation map + uncontested market space"
    }
}
```

### Decision Matrix
```python
# decision_matrix.py
class DecisionMatrix:
    def evaluate(self, options: List[Option], criteria: List[Criterion]) -> DecisionResult:
        # 1. Normalize scores (0-1)
        # 2. Apply weights
        # 3. Calculate weighted scores
        # 4. Sensitivity analysis (vary weights ±20%)
        # 5. Return ranking with confidence intervals
        pass
    
    def format_output(self, result: DecisionResult) -> str:
        # Markdown table with scores, rankings, sensitivity
        pass
```

### Scenario Planning
```python
# scenarios.py
class ScenarioPlanner:
    def generate_scenarios(self, base_case: Case, 
                           variables: List[Variable]) -> List[Scenario]:
        # Best case: all variables favorable
        # Base case: expected values
        # Worst case: all variables adverse
        # Custom scenarios: specific combinations
        pass
    
    def evaluate_strategy(self, strategy: Strategy, 
                          scenarios: List[Scenario]) -> StrategyRobustness:
        # Expected value across scenarios
        # Downside protection (worst case)
        # Upside potential (best case)
        # Regret minimization
        pass
```

### CLI Design
```bash
# strategy-advisor analyze --framework swot --topic "enterprise AI market entry"
# strategy-advisor decide --options "build,buy,partner" --criteria "cost,time,risk,control" --weights "0.3,0.3,0.2,0.2"
# strategy-advisor scenario --strategy "acquire startup" --variables "integration_cost,market_growth,retention"
# strategy-advisor template --type "market_entry" --output strategy.md
# strategy-advisor monitor --strategy "product_launch" --kpis "adoption,revenue,churn"
```

---

## Acceptance Criteria
- [ ] 6+ strategic frameworks with scoring
- [ ] Decision matrix handles 10 options × 10 criteria
- [ ] Scenario planning generates 4+ scenarios with evaluation
- [ ] CLI completes analysis in <30s
- [ ] Templates cover 10+ common strategic decisions
- [ ] Integration with project-planner generates valid plans
- [ ] Risk quantification uses Monte Carlo (1000+ iterations)

---

## Dependencies
- `project-planner` (strategy → execution)
- `brainstorming` (option generation)
- `systematic-debugging` (assumption validation)
- `code-quality` (CLI code)
- `verification-before-completion` (analysis claims)
- `writing-skills` (documentation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Framework misuse | Medium | High | Guided workflow, framework selection aid |
| Data quality | Medium | High | Source validation, confidence scoring |
| Analysis paralysis | High | Medium | Time-boxing, decision deadlines |

---

## Success Metrics
- Decision quality (retrospective): >80% rated good/excellent
- Analysis time: <1 hour for standard decisions
- Framework usage: >3 frameworks per analysis
- Template adoption: >70% of analyses use templates
- Integration success: >90% strategy→plan transitions