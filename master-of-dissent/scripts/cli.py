"""CLI for master-of-dissent skill."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.frameworks import FRAMEWORKS, get_framework
from scripts.safety import DissentSafety


def cmd_rebut(args: argparse.Namespace) -> int:
    framework = get_framework(args.framework)
    safety = DissentSafety()

    if not safety.is_allowed_target("ideas_arguments"):
        print(json.dumps({"error": "Target not allowed"}, indent=2))
        return 1

    result = {
        "mode": "rebut",
        "framework": args.framework,
        "input": args.text,
        "framework_description": framework["description"] if framework else None,
        "template": framework["template"] if framework else None,
        "response": _generate_rebut(args.text, framework),
    }
    print(json.dumps(result, indent=2))
    return 0


def cmd_roast(args: argparse.Namespace) -> int:
    safety = DissentSafety()

    result = {
        "mode": "roast",
        "intensity": args.intensity,
        "input": args.text,
        "response": _generate_roast(args.text, args.intensity),
    }
    print(json.dumps(result, indent=2))
    return 0


def cmd_debate(args: argparse.Namespace) -> int:
    result = {
        "mode": "debate",
        "topic": args.topic,
        "rounds": args.rounds,
        "positions": _generate_debate_rounds(args.topic, args.rounds),
    }
    print(json.dumps(result, indent=2))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    result = {
        "mode": "analyze",
        "input": args.text,
        "fallacies_detected": _detect_fallacies(args.text),
        "argument_strength": _assess_argument_strength(args.text),
    }
    print(json.dumps(result, indent=2))
    return 0


def cmd_practice(args: argparse.Namespace) -> int:
    safety = DissentSafety()

    result = {
        "mode": "practice",
        "practice_mode": args.mode,
        "feedback": _generate_practice_feedback(args.mode, args.feedback),
    }
    print(json.dumps(result, indent=2))
    return 0


def _generate_rebut(text: str, framework: dict | None) -> str:
    if framework is None:
        return f"Interesting claim: {text}"
    template = framework["template"]
    return template.format(
        premise=text,
        absurd_conclusion="the opposite must also be true",
        witty_closer="But that's clearly not the case, is it?",
        strong_form="the strongest version of this argument",
        flaw="it doesn't hold up under scrutiny",
        analogy="comparing apples to oranges",
        punchline="the comparison breaks down immediately",
        negative_frame="a flawed perspective",
        positive_frame="a more accurate view",
        insight="context matters more than the label",
        counter_example="the exception proves the rule wrong",
        implication="so the generalization is false",
        alternative="the evidence points elsewhere",
        assumption="the premise is unproven",
        consequence="the conclusion doesn't follow",
        authority="domain experts",
        quote="this approach doesn't work",
        evidence="the results speak for themselves",
    )


def _generate_roast(text: str, intensity: str) -> str:
    intensity_map = {
        "playful": f"Nice try, but {text} doesn't quite land.",
        "sharp": f"Let me be direct: {text} is wrong, and here's why.",
        "devastating": f"{text}. Truly. That's the whole argument?",
    }
    return intensity_map.get(intensity, f"Interesting: {text}")


def _generate_debate_rounds(topic: str, rounds: int) -> list[dict]:
    rounds_data = []
    for i in range(1, rounds + 1):
        rounds_data.append({
            "round": i,
            "position": f"Argument for round {i} on {topic}",
            "rebuttal": f"Counter-argument for round {i}",
        })
    return rounds_data


def _detect_fallacies(text: str) -> list[dict]:
    fallacies = []
    text_lower = text.lower()
    if "everyone" in text_lower or "all" in text_lower:
        fallacies.append({"type": "hasty_generalization", "confidence": 0.7})
    if "always" in text_lower or "never" in text_lower:
        fallacies.append({"type": "absolute_claim", "confidence": 0.8})
    if "because" in text_lower and "therefore" in text_lower:
        fallacies.append({"type": "circular_reasoning", "confidence": 0.5})
    return fallacies


def _assess_argument_strength(text: str) -> dict:
    evidence_markers = ["data", "study", "research", "evidence", "example", "case"]
    strength = sum(1 for m in evidence_markers if m in text.lower())
    return {
        "score": min(1.0, strength / 3),
        "has_evidence": strength > 0,
        "weaknesses": ["no citations"] if strength == 0 else [],
    }


def _generate_practice_feedback(mode: str, feedback: bool) -> str:
    if not feedback:
        return "Practice mode active. Submit your argument for review."
    return f"Constructive {mode} feedback: focus on the argument structure, not the person."


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="master-of-dissent",
        description="Professional debate expert with structured frameworks, safety guards, and CLI tooling",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    rebut_p = subparsers.add_parser("rebut", help="Rebut an argument using a specific framework")
    rebut_p.add_argument("text", help="The argument to rebut")
    rebut_p.add_argument("--framework", default="steel_man", choices=list(FRAMEWORKS.keys()))

    roast_p = subparsers.add_parser("roast", help="Deliver a witty roast")
    roast_p.add_argument("text", help="The claim to roast")
    roast_p.add_argument("--intensity", default="playful", choices=["playful", "sharp", "devastating"])

    debate_p = subparsers.add_parser("debate", help="Run a structured debate")
    debate_p.add_argument("--topic", required=True, help="Debate topic")
    debate_p.add_argument("--rounds", type=int, default=3, help="Number of rounds")

    analyze_p = subparsers.add_parser("analyze", help="Analyze an argument for fallacies")
    analyze_p.add_argument("text", help="Text to analyze")

    practice_p = subparsers.add_parser("practice", help="Practice debate skills")
    practice_p.add_argument("--mode", default="constructive", choices=["roast", "constructive", "steel_man", "devils_advocate"])
    practice_p.add_argument("--feedback", action="store_true", help="Include feedback")

    args = parser.parse_args()
    handlers = {
        "rebut": cmd_rebut,
        "roast": cmd_roast,
        "debate": cmd_debate,
        "analyze": cmd_analyze,
        "practice": cmd_practice,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())