"""Strategic frameworks library for the strategy-advisor skill."""
from __future__ import annotations


def _dim(name: str, question: str, prompts: list[str]) -> dict:
    return {"name": name, "question": question, "prompts": prompts}


def _build_template(name: str, dimensions: list[dict]) -> str:
    lines = ["# {framework}", "", "**Topic:** {topic}", "", "## Summary", "{summary}", ""]
    for dim in dimensions:
        lines.append(f"## {dim['name']}")
        lines.append(f"**Question:** {dim['question']}")
        lines.append(f"{{dimension:{dim['name']}}}")
        lines.append("")
    return "\n".join(lines)


_PORTERS = [
    _dim(
        "Threat of New Entrants",
        "How easy is it for new competitors to enter the market?",
        [
            "What are the capital requirements to enter?",
            "How strong are existing brand loyalties and switching costs?",
            "What regulatory or licensing barriers exist?",
            "How quickly could incumbents retaliate?",
        ],
    ),
    _dim(
        "Bargaining Power of Suppliers",
        "How much leverage do suppliers have over prices and terms?",
        [
            "How concentrated is the supplier base?",
            "How costly would it be to switch suppliers?",
            "How differentiated are supplier inputs?",
            "How much would forward integration threaten us?",
        ],
    ),
    _dim(
        "Bargaining Power of Buyers",
        "How much leverage do buyers hold over prices and terms?",
        [
            "How concentrated are buyers?",
            "How price-sensitive is demand?",
            "How low are buyer switching costs?",
            "Can buyers easily backward integrate?",
        ],
    ),
    _dim(
        "Threat of Substitutes",
        "How likely are customers to switch to alternative solutions?",
        [
            "What substitutes exist and how do they compare on price?",
            "How does substitute performance differ?",
            "What is the relative price-performance tradeoff?",
            "How quickly could substitutes improve?",
        ],
    ),
    _dim(
        "Industry Rivalry",
        "How intense is competition among existing players?",
        [
            "How many competitors are there and how similar are they?",
            "How fast is the market growing?",
            "How high are exit barriers?",
            "How often do competitors engage in price wars?",
        ],
    ),
]

_SWOT = [
    _dim(
        "Strengths",
        "What internal advantages give us an edge?",
        [
            "What do we do better than competitors?",
            "What unique resources or assets do we hold?",
            "What are our most valuable capabilities?",
        ],
    ),
    _dim(
        "Weaknesses",
        "What internal disadvantages hold us back?",
        [
            "Where do competitors outperform us?",
            "What resources are we missing?",
            "What are our operational bottlenecks?",
        ],
    ),
    _dim(
        "Opportunities",
        "What external conditions could we exploit?",
        [
            "What market trends create openings?",
            "What gaps exist in competitor offerings?",
            "What unmet customer needs could we serve?",
        ],
    ),
    _dim(
        "Threats",
        "What external conditions could hurt us?",
        [
            "What trends threaten our position?",
            "Who could disrupt our market?",
            "What regulatory or economic risks loom?",
        ],
    ),
]

_PESTLE = [
    _dim(
        "Political",
        "What political forces shape the market?",
        [
            "How stable is the political environment?",
            "What regulations or policies affect us?",
            "What is the tax or trade policy outlook?",
        ],
    ),
    _dim(
        "Economic",
        "What economic conditions affect the market?",
        [
            "What is the macroeconomic growth outlook?",
            "How do interest rates and inflation affect us?",
            "What are the employment and income trends?",
        ],
    ),
    _dim(
        "Social",
        "What social and cultural forces are at play?",
        [
            "How are demographics shifting?",
            "What lifestyle or attitude trends matter?",
            "How is public opinion evolving?",
        ],
    ),
    _dim(
        "Technological",
        "What technological changes affect the market?",
        [
            "What technologies are disrupting the market?",
            "How is technology adoption evolving?",
            "What R&D investments are emerging?",
        ],
    ),
    _dim(
        "Legal",
        "What legal forces constrain or enable us?",
        [
            "What laws regulate our activities?",
            "What is the compliance burden?",
            "What legal risks do we face?",
        ],
    ),
    _dim(
        "Environmental",
        "What environmental forces matter?",
        [
            "What sustainability regulations apply?",
            "How do climate concerns affect demand?",
            "What resource or emissions constraints exist?",
        ],
    ),
]

_BCG = [
    _dim(
        "Relative Market Share",
        "How large is our market share relative to the largest competitor?",
        [
            "What is our share versus the market leader?",
            "Is our share growing or eroding?",
            "What share does the strongest competitor hold?",
        ],
    ),
    _dim(
        "Market Growth Rate",
        "How fast is the market growing?",
        [
            "What is the annual market growth rate?",
            "Is growth accelerating or slowing?",
            "What growth do forecasters expect?",
        ],
    ),
]

_ANSOFF = [
    _dim(
        "Market Penetration",
        "How can we grow by selling existing products to existing markets?",
        [
            "What is our current market share?",
            "How can we increase usage among existing customers?",
            "What pricing or promotion levers exist?",
        ],
    ),
    _dim(
        "Product Development",
        "How can we grow by introducing new products to existing markets?",
        [
            "What new products would existing customers value?",
            "What capabilities do we need to build?",
            "How fast can we innovate?",
        ],
    ),
    _dim(
        "Market Development",
        "How can we grow by entering new markets with existing products?",
        [
            "Which new geographies or segments fit?",
            "What adaptation does each new market require?",
            "What distribution channels are available?",
        ],
    ),
    _dim(
        "Diversification",
        "How can we grow by entering new markets with new products?",
        [
            "What related adjacencies make sense?",
            "What unrelated markets could we enter?",
            "What risks does diversification introduce?",
        ],
    ),
]

_FOUR_ACTIONS = [
    _dim(
        "Eliminate",
        "Which factors the industry takes for granted should be eliminated?",
        [
            "What value factors do customers no longer need?",
            "What factors can we stop offering?",
            "What assumptions are obsolete?",
        ],
    ),
    _dim(
        "Reduce",
        "Which factors should be reduced well below industry standard?",
        [
            "What factors are over-delivered relative to value?",
            "Where can we reduce without hurting value?",
            "What simplifications increase speed?",
        ],
    ),
    _dim(
        "Raise",
        "Which factors should be raised well above industry standard?",
        [
            "What factors does the market under-serve?",
            "Where can we outperform on value?",
            "What do customers wish were better?",
        ],
    ),
    _dim(
        "Create",
        "Which factors that the industry has never offered should we create?",
        [
            "What unmet needs remain unaddressed?",
            "What entirely new value can we create?",
            "What jobs do customers struggle to get done?",
        ],
    ),
]

_BLUE_OCEAN = [
    _dim(
        "Value Innovation",
        "Where can we deliver a leap in value while lowering cost?",
        [
            "How can we raise buyer value dramatically?",
            "How can we lower cost simultaneously?",
            "What competing factors can we ignore?",
        ],
    ),
    _dim(
        "Cost Innovation",
        "How can we structure costs to support differentiation?",
        [
            "What cost drivers can we eliminate?",
            "What fixed costs can become variable?",
            "Where can we simplify to save?",
        ],
    ),
    _dim(
        "Differentiation",
        "How can we make our offering stand apart?",
        [
            "What factors can we offer that no one else does?",
            "What non-price value can we create?",
            "How can we sharpen our value curve?",
        ],
    ),
    *_FOUR_ACTIONS,
]

_MOAT = [
    _dim(
        "Network Effects",
        "How much does each additional user increase value for others?",
        [
            "How does value grow with user count?",
            "How defensible is the network?",
            "What are the risks of network saturation?",
        ],
    ),
    _dim(
        "Switching Costs",
        "How costly is it for customers to leave?",
        [
            "What costs do customers incur to switch?",
            "How deep is product integration in their workflow?",
            "How sticky is our data lock-in?",
        ],
    ),
    _dim(
        "Cost Advantage",
        "Do we have a structurally lower cost position?",
        [
            "Where do our unit costs beat competitors?",
            "What scale or learning-curve benefits exist?",
            "How durable is the cost edge?",
        ],
    ),
    _dim(
        "Intangible Assets",
        "What hard-to-replicate intangibles do we hold?",
        [
            "What patents, brands, or licenses protect us?",
            "What proprietary data or software do we own?",
            "How valuable are our customer relationships?",
        ],
    ),
    _dim(
        "Scale",
        "How do our scale advantages protect the business?",
        [
            "Where does scale reduce cost per unit?",
            "What scale-based bargaining power do we have?",
            "How quickly could competitors reach scale?",
        ],
    ),
]

FRAMEWORKS: dict[str, dict] = {
    "porters_five_forces": {
        "id": "porters_five_forces",
        "name": "Porter's Five Forces",
        "dimensions": _PORTERS,
        "template": _build_template("Porter's Five Forces", _PORTERS),
    },
    "swot": {
        "id": "swot",
        "name": "SWOT Analysis",
        "dimensions": _SWOT,
        "template": _build_template("SWOT Analysis", _SWOT),
    },
    "pestle": {
        "id": "pestle",
        "name": "PESTLE Analysis",
        "dimensions": _PESTLE,
        "template": _build_template("PESTLE Analysis", _PESTLE),
    },
    "bcg_matrix": {
        "id": "bcg_matrix",
        "name": "BCG Growth-Share Matrix",
        "dimensions": _BCG,
        "template": _build_template("BCG Growth-Share Matrix", _BCG),
    },
    "ansoff_matrix": {
        "id": "ansoff_matrix",
        "name": "Ansoff Matrix",
        "dimensions": _ANSOFF,
        "template": _build_template("Ansoff Matrix", _ANSOFF),
    },
    "blue_ocean": {
        "id": "blue_ocean",
        "name": "Blue Ocean Strategy",
        "dimensions": _BLUE_OCEAN,
        "four_actions": ["Eliminate", "Reduce", "Raise", "Create"],
        "template": _build_template("Blue Ocean Strategy", _BLUE_OCEAN),
    },
    "competitive_moat": {
        "id": "competitive_moat",
        "name": "Competitive Moat",
        "dimensions": _MOAT,
        "template": _build_template("Competitive Moat", _MOAT),
    },
}


def get_framework(framework_id: str) -> dict:
    if framework_id not in FRAMEWORKS:
        raise KeyError(f"Unknown framework: {framework_id}")
    return FRAMEWORKS[framework_id]


def analyze(framework_id: str, topic: str, inputs: dict[str, str] | None = None) -> dict:
    framework = get_framework(framework_id)
    inputs = inputs or {}
    dimensions = [
        {
            "name": dim["name"],
            "question": dim["question"],
            "prompts": dim["prompts"],
            "analysis": inputs.get(dim["name"], ""),
        }
        for dim in framework["dimensions"]
    ]
    return {"framework": framework_id, "topic": topic, "dimensions": dimensions, "summary": ""}


def render_markdown(framework_id: str, topic: str, analysis: dict) -> str:
    framework = get_framework(framework_id)
    text = framework["template"]
    text = text.replace("{framework}", framework["name"])
    text = text.replace("{topic}", topic)
    text = text.replace("{summary}", analysis.get("summary", ""))
    for dim in analysis["dimensions"]:
        text = text.replace(f"{{dimension:{dim['name']}}}", dim["analysis"])
    return text
