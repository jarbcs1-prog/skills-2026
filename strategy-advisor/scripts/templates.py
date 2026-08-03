"""Markdown template library for common strategic decisions."""
from __future__ import annotations

TEMPLATE_TYPES: dict[str, str] = {
    "market_entry": """# {topic}

## Strategic Question
Should we enter the {topic} market, and how?

## Market Assessment
- Market size and expected growth
- Customer segments and unmet needs
- Key success factors

## Competitive Landscape
- Existing competitors and their share
- Barriers to entry and exit
- Substitute and complement offerings

## Entry Options
- Build from scratch
- Acquire an existing player
- Partner or license

## Entry Plan
- Timeline and phased approach
- Investment required
- Success metrics

## Risks and Mitigations
- Regulatory or compliance risks
- Execution and talent risks
- Contingency plans""",
    "product_launch": """# {topic}

## Strategic Question
How should we launch {topic}?

## Launch Objectives
- Revenue and adoption targets
- Positioning and differentiation
- Target customer segments

## Go-To-Market Plan
- Pricing and packaging
- Sales and distribution channels
- Marketing and messaging

## Launch Timeline
- Phase 1: Internal readiness
- Phase 2: Limited release
- Phase 3: Full rollout

## Launch Checklist
- Customer validation complete
- Support and training ready
- Metrics and monitoring in place

## Risks and Contingencies
- Adoption shortfall
- Technical issues
- Competitive response""",
    "competitive_response": """# {topic}

## Strategic Question
How should we respond to {topic}?

## Situation Summary
- What changed in the competitive landscape
- Implied threat or opportunity
- Urgency of response

## Competitive Assessment
- Competitor strengths and weaknesses
- Our relative position
- Customer reaction and switching risk

## Response Options
- Defend current position
- Counter with differentiation
- Attack weakest segment
- Partner or acquire

## Recommended Response
- Chosen option and rationale
- Resource requirements
- Timeline for execution

## Ongoing Monitoring
- Competitor signals to track
- Review cadence
- Exit or escalation criteria""",
    "pricing_strategy": """# {topic}

## Strategic Question
What pricing strategy should we adopt for {topic}?

## Pricing Objectives
- Revenue and margin targets
- Market share goals
- Value signaling intent

## Customer Value Analysis
- Perceived value by segment
- Price sensitivity and elasticity
- Willingness to pay evidence

## Pricing Options
- Cost-plus
- Value-based
- Penetration or skimming
- Freemium or tiered

## Cost and Margin Impact
- Unit cost structure
- Breakeven analysis
- Margin impact per option

## Rollout and Testing
- Pilot pricing experiments
- Measurement plan
- Adjustment triggers""",
    "partnership": """# {topic}

## Strategic Question
Should we pursue {topic}, and with whom?

## Partnership Rationale
- Strategic fit with our objectives
- Capabilities and assets gained
- Gaps we cannot fill alone

## Partner Options
- Candidate partners and strengths
- Compatibility and culture fit
- Exclusivity considerations

## Deal Structure
- Scope of collaboration
- Value sharing and economics
- Governance and decision rights

## Integration Plan
- Workstreams and owners
- Timeline and milestones
- Communication plan

## Risks and Exit
- Dependencies and lock-in
- Conflict resolution
- Exit and wind-down clauses""",
    "expansion": """# {topic}

## Strategic Question
Should we expand via {topic}?

## Expansion Rationale
- Strategic objectives served
- Expected value creation
- Fit with current portfolio

## Market Analysis
- Target market size and growth
- Customer access and distribution
- Local competitive dynamics

## Expansion Options
- Organic growth
- Acquisition
- Joint venture or franchise

## Financial Impact
- Capital required
- Return projections
- Payback and breakeven

## Execution Roadmap
- Phased rollout plan
- Resource allocation
- Success metrics and review points""",
    "digital_transformation": """# {topic}

## Strategic Question
How should we approach {topic}?

## Transformation Vision
- Desired future state
- Problems being solved
- Value expected from digitization

## Current State Assessment
- Existing systems and processes
- Digital maturity and gaps
- Change readiness

## Priority Initiatives
- Customer experience
- Operational efficiency
- Data and analytics
- New business models

## Investment Plan
- Budget and phasing
- Technology choices
- Talent and capability building

## Execution and Governance
- Program structure and owners
- Milestones and KPIs
- Risk management and change control""",
    "talent_strategy": """# {topic}

## Strategic Question
How should we shape {topic}?

## Talent Needs
- Critical roles and skills required
- Current capability gaps
- Future capability needs

## Sourcing Options
- Build: internal development
- Buy: external hiring
- Borrow: contractors and partners

## Retention and Development
- Compensation and incentives
- Career paths and growth
- Culture and engagement

## Organizational Impact
- Structure changes required
- Leadership implications
- Change management needs

## Measurement
- Hiring and retention metrics
- Capability progression
- Cost of the talent strategy""",
    "cost_optimization": """# {topic}

## Strategic Question
How should we approach {topic}?

## Cost Baseline
- Cost structure by category
- Benchmarking vs peers
- Trends and pressure points

## Optimization Levers
- Process efficiency
- Supplier renegotiation
- Technology and automation
- Portfolio and scope pruning

## Impact Assessment
- Savings potential per lever
- One-time costs vs recurring savings
- Risk of value erosion

## Implementation Plan
- Phasing and quick wins
- Ownership and accountability
- Tracking and reporting

## Safeguards
- Quality and service guardrails
- Change management
- Reverse decisions if targets missed""",
    "go_to_market": """# {topic}

## Strategic Question
How should we take {topic} to market?

## Target Market
- Segments and personas
- Geography and channels
- Buying journey and triggers

## Value Proposition
- Core message and differentiation
- Proof points and evidence
- Objection handling

## Channel Strategy
- Direct vs partner channels
- Pricing and packaging
- Sales enablement

## Marketing Plan
- Campaigns and content
- Demand generation
- Budget and allocation

## Launch Metrics
- Pipeline and conversion targets
- Revenue and adoption goals
- Review cadence and learning loops""",
    "roadmap": """# {topic}

## Strategic Question
What is the roadmap for {topic}?

## Vision and Goals
- Where we are heading
- Objectives and key results
- Success criteria

## Initiative Portfolio
- Near-term initiatives
- Mid-term initiatives
- Long-term bets

## Dependencies
- Technical dependencies
- Market dependencies
- Resource dependencies

## Timeline and Phasing
- Milestones by quarter
- Checkpoints and gates
- Capacity planning

## Governance
- Owners and decision cadence
- Prioritization process
- Measurement and review""",
    "risk_mitigation": """# {topic}

## Strategic Question
How should we manage risks around {topic}?

## Risk Register
- Key risks identified
- Likelihood and impact ratings
- Current exposure

## Mitigation Plan
- Preventive measures
- Detection and early warning
- Response and recovery actions

## Scenario Planning
- Best case
- Base case
- Worst case

## Ownership and Monitoring
- Risk owners
- Review cadence
- Escalation thresholds

## Residual Risk
- Acceptable remaining exposure
- Insurance or hedging
- Contingency reserves""",
}


def render_template(template_type: str, topic: str, params: dict | None = None) -> str:
    if template_type not in TEMPLATE_TYPES:
        raise KeyError(f"Unknown template type: {template_type}")
    return TEMPLATE_TYPES[template_type].format(topic=topic, **(params or {}))
