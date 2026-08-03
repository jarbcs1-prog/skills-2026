"""Tests for cheaper-reasoning convergence module."""
from scripts.convergence import detect_convergence, ConvergenceSignal


def test_empty_history_returns_continue():
    result = detect_convergence([])
    assert result == ConvergenceSignal.CONTINUE


def test_single_entry_returns_continue():
    result = detect_convergence(["Some thought"])
    assert result == ConvergenceSignal.CONTINUE


def test_repeating_themes_converged():
    history = [
        "The key insight is about scalability and performance",
        "Scalability and performance are the main concerns",
        "We need to focus on scalability and performance",
    ]
    result = detect_convergence(history)
    assert result == ConvergenceSignal.CONVERGED


def test_stabilizing_themes_converging():
    history = [
        "Starting with the basics of the problem",
        "Moving to the next aspect of the solution",
        "Now considering the final piece",
    ]
    result = detect_convergence(history)
    assert result in (ConvergenceSignal.CONVERGING, ConvergenceSignal.CONTINUE)


def test_stalled_history():
    history = [
        "Hmm.",
        "Wait.",
        "Let me think.",
        "Actually.",
    ]
    result = detect_convergence(history)
    assert result == ConvergenceSignal.STALLED


def test_continuing_diverse_themes():
    history = [
        "The market dynamics suggest a growth opportunity",
        "Technical constraints limit the implementation approach",
        "User feedback indicates a need for simplification",
        "Competitive analysis reveals a differentiation angle",
    ]
    result = detect_convergence(history)
    assert result == ConvergenceSignal.CONTINUE


def test_convergence_with_three_segments():
    history = [
        "First thoughts on the architecture: microservices",
        "Second thoughts: microservices with event sourcing",
        "Third thoughts: microservices, event sourcing, CQRS pattern",
    ]
    result = detect_convergence(history)
    assert result in (ConvergenceSignal.CONVERGING, ConvergenceSignal.CONVERGED)