"""Debate frameworks for master-of-dissent skill."""
from __future__ import annotations

FRAMEWORKS: dict[str, dict] = {
    "reductio_ad_absurdum": {
        "description": "Take premise to logical extreme to show absurdity",
        "template": "If {premise}, then {absurd_conclusion}. {witty_closer}",
        "example": "If we optimize for zero bugs, we'd write zero code. Perfect bug-free software: empty repository.",
    },
    "steel_manning": {
        "description": "Strengthen opponent's argument before dismantling",
        "template": "The strongest version of your argument is {strong_form}. But even that fails because {flaw}.",
        "example": "You're saying 'move fast and break things'. Strong form: 'iterate rapidly with user feedback'. Still fails: breaks trust when things break for users.",
    },
    "analogy": {
        "description": "Map to familiar domain to expose flaw",
        "template": "That's like {analogy}. {punchline}",
        "example": "Rewriting in Rust for safety is like wearing a helmet to eat soup. Technically protective, practically absurd.",
    },
    "reframing": {
        "description": "Change the frame to shift perspective",
        "template": "You call it {negative_frame}. I call it {positive_frame}. The difference? {insight}",
        "example": "You call it 'technical debt'. I call it 'interest-free loan from your past self'. The difference? You got value then, pay later.",
    },
    "counter_example": {
        "description": "Single case that breaks generalization",
        "template": "Except {counter_example}. {implication}",
        "example": "'All dynamic languages are slow.' Except LuaJIT. The implication? Implementation matters more than paradigm.",
    },
    "socratic_questioning": {
        "description": "Ask probing questions to expose assumptions",
        "template": "But have you considered {alternative}? If {assumption} is false, then {consequence}.",
        "example": "But have you considered that faster delivery might mean more bugs? If quality is sacrificed, then support costs rise.",
    },
    "appeal_to_authority": {
        "description": "Counter by citing credible opposition or evidence",
        "template": "Even {authority} disagrees: {quote}. The data shows {evidence}.",
        "example": "Even industry veterans argue against this. The data shows teams with stricter review processes ship more reliably.",
    },
}


def get_framework(name: str) -> dict | None:
    """Retrieve a debate framework by name."""
    return FRAMEWORKS.get(name)


def list_frameworks() -> list[str]:
    """List all available debate frameworks."""
    return list(FRAMEWORKS.keys())
