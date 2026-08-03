"""Tests for conversation simulator."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.simulator import ConversationSimulator, PERSONAS


def test_simulator_initializes():
    sim = ConversationSimulator()
    assert sim.personas == PERSONAS


def test_simulate_returns_result():
    sim = ConversationSimulator()
    result = sim.simulate(
        user_opening="I need to talk about your performance.",
        persona_name="defensive",
    )
    assert result.persona == "defensive"
    assert result.response
    assert result.emotional_state in ("high", "medium", "low")
    assert result.suggested_next_move
    assert 0.0 <= result.accuracy_score <= 1.0


def test_all_personas_produce_responses():
    sim = ConversationSimulator()
    for persona_name in PERSONAS:
        result = sim.simulate(
            user_opening="I need to talk about your performance.",
            persona_name=persona_name,
        )
        assert result.response, f"No response for persona {persona_name}"


def test_practice_session_returns_results():
    from scripts.simulator import practice_session
    result = practice_session("feedback")
    assert "type" in result
    assert "practice_results" in result
    assert len(result["practice_results"]) > 0


def test_practice_session_unknown_type():
    from scripts.simulator import practice_session
    result = practice_session("unknown_type")
    assert "error" in result


def test_simulator_accuracy_in_range():
    sim = ConversationSimulator()
    result = sim.simulate(
        user_opening="I need to talk about your performance.",
        persona_name="agreeable",
    )
    assert 0.7 <= result.accuracy_score <= 1.0