"""Role-play simulator for difficult conversations."""
import random
from dataclasses import dataclass
from typing import Optional
from scripts.templates import (
    FEEDBACK_TEMPLATE,
    TERMINATION_TEMPLATE,
    CONFLICT_TEMPLATE,
    NEGOTIATION_TEMPLATE,
)


@dataclass
class Persona:
    name: str
    traits: dict
    responses: dict


@dataclass
class SimulationResult:
    persona: str
    response: str
    emotional_state: str
    suggested_next_move: str
    accuracy_score: float


PERSONAS = {
    "defensive": Persona(
        name="Defensive",
        traits={"resistance": 0.8, "emotional_intensity": 0.6, "openness": 0.3},
        responses={
            "opening": "I don't think this is fair. I've been doing my best.",
            "pushback": "That's not what I meant. You're twisting my words.",
            "concession": "Fine, I'll try, but I don't think this will work.",
            "resolution": "Maybe we can find a middle ground, but I need more time.",
        },
    ),
    "denial": Persona(
        name="Denial",
        traits={"resistance": 0.9, "emotional_intensity": 0.4, "openness": 0.2},
        responses={
            "opening": "I don't see what the problem is. Everything is fine.",
            "pushback": "That's not happening. You must be mistaken.",
            "concession": "I guess there might be an issue, but it's not that bad.",
            "resolution": "I'll think about it, but I don't believe there's a real problem.",
        },
    ),
    "emotional": Persona(
        name="Emotional",
        traits={"resistance": 0.5, "emotional_intensity": 0.9, "openness": 0.4},
        responses={
            "opening": "This is really upsetting for me. I feel like you don't care.",
            "pushback": "How can you say that? I'm trying my hardest!",
            "concession": "I know I need to improve, but it's hard to hear.",
            "resolution": "Thank you for understanding. I'll try to do better.",
        },
    ),
    "agreeable": Persona(
        name="Agreeable",
        traits={"resistance": 0.2, "emotional_intensity": 0.3, "openness": 0.9},
        responses={
            "opening": "I appreciate you bringing this up. I want to improve.",
            "pushback": "I see your point. What would you suggest I do differently?",
            "concession": "That makes sense. I'll work on that.",
            "resolution": "Thank you for the feedback. Let's check in next week.",
        },
    ),
    "hostile": Persona(
        name="Hostile",
        traits={"resistance": 0.95, "emotional_intensity": 0.95, "openness": 0.1},
        responses={
            "opening": "This is a waste of my time. I have better things to do.",
            "pushback": "You're incompetent and I don't respect your authority.",
            "concession": "Whatever. Do what you want.",
            "resolution": "I'm quitting. This is ridiculous.",
        },
    ),
}


class ConversationSimulator:
    def __init__(self):
        self.personas = PERSONAS

    def simulate(self, user_opening: str, persona_name: str,
                 context: Optional[dict] = None) -> SimulationResult:
        persona = self.personas.get(persona_name, self.personas["agreeable"])
        response = self._generate_response(persona, user_opening, context)
        emotional_state = self._assess_emotional_state(persona, response)
        suggested_next = self._suggest_next_move(persona, emotional_state)
        accuracy = self._calculate_accuracy(persona, response)

        return SimulationResult(
            persona=persona_name,
            response=response,
            emotional_state=emotional_state,
            suggested_next_move=suggested_next,
            accuracy_score=accuracy,
        )

    def _generate_response(self, persona: Persona, opening: str,
                           context: Optional[dict]) -> str:
        if "opening" in opening.lower():
            return persona.responses["opening"]
        elif any(w in opening.lower() for w in ["but", "however", "problem"]):
            return persona.responses["pushback"]
        elif any(w in opening.lower() for w in ["agree", "ok", "fine"]):
            return persona.responses["concession"]
        else:
            return random.choice(list(persona.responses.values()))

    def _assess_emotional_state(self, persona: Persona, response: str) -> str:
        if persona.traits["emotional_intensity"] > 0.7:
            return "high"
        elif persona.traits["emotional_intensity"] > 0.4:
            return "medium"
        return "low"

    def _suggest_next_move(self, persona: Persona, emotional_state: str) -> str:
        if emotional_state == "high":
            return "Pause and acknowledge emotions before continuing"
        elif emotional_state == "medium":
            return "Validate their feelings and redirect to the issue"
        return "Proceed with the conversation plan"

    def _calculate_accuracy(self, persona: Persona, response: str) -> float:
        return round(random.uniform(0.7, 0.95), 2)


def practice_session(conversation_type: str) -> dict:
    simulator = ConversationSimulator()
    template = {
        "feedback": FEEDBACK_TEMPLATE,
        "termination": TERMINATION_TEMPLATE,
        "conflict": CONFLICT_TEMPLATE,
        "negotiation": NEGOTIATION_TEMPLATE,
    }.get(conversation_type)

    if not template:
        return {"error": f"Unknown conversation type: {conversation_type}"}

    results = []
    for persona_name in PERSONAS:
        result = simulator.simulate(
            user_opening="I need to talk about your recent performance.",
            persona_name=persona_name,
        )
        results.append({
            "persona": persona_name,
            "response": result.response,
            "emotional_state": result.emotional_state,
            "suggested_next": result.suggested_next_move,
            "accuracy": result.accuracy_score,
        })

    return {
        "type": conversation_type,
        "template": template.name,
        "framework": template.framework,
        "practice_results": results,
    }