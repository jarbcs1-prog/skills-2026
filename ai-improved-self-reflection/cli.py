"""
AI Self-Reflection Engine v2

Command-line interface.

The CLI coordinates the reflection system.

It does not contain learning logic.

Commands:

initialize
    Create memory structure.

record
    Store reflection experience.

distill
    Convert experiences into candidates.

promote
    Evaluate candidate capabilities.

validate
    Record capability performance.

report
    Display system state.
"""

import argparse
import json

from storage import (
    initialize_storage,
)

from reflection import (
    create_reflection,
)

from distillation import (
    run_distillation,
)

from capability import (
    promote_candidates,
)

from validation import (
    record_validation,
)

from analysis import (
    generate_system_report,
)


def command_initialize(
    _: argparse.Namespace,
) -> None:
    """
    Initialize memory.
    """

    initialize_storage()

    print(
        "Reflection memory initialized."
    )


def command_record(
    args: argparse.Namespace,
) -> None:
    """
    Create reflection event.
    """

    event = create_reflection(
        task=args.task,
        category=args.category,
        observation=args.observation,
        friction=args.friction,
        root_cause=args.root_cause,
        lesson=args.lesson,
        scope=args.scope,
        confidence=args.confidence,
        evidence=args.evidence,
        action=args.action,
        audience_assumptions=(
            args.audience
            if args.audience is not None
            else []
        ),
        hidden_criteria=(
            args.criteria
            if args.criteria is not None
            else []
        ),
        corrections=args.corrections,
        clarifications=args.clarifications,
        re_prompts=args.reprompts,
    )

    print(
        "Reflection recorded:"
    )

    print(
        event.lesson
    )


def command_distill(
    _: argparse.Namespace,
) -> None:
    """
    Generate candidate lessons.
    """

    candidates = run_distillation()

    print(
        f"Generated {len(candidates)} candidates."
    )


def command_promote(
    _: argparse.Namespace,
) -> None:
    """
    Promote candidate lessons.
    """

    capabilities = promote_candidates()

    print(
        f"Evaluated {len(capabilities)} capabilities."
    )


def command_validate(
    args: argparse.Namespace,
) -> None:
    """
    Store validation result.
    """

    validation = record_validation(
        capability_name=args.capability,
        task=args.task,
        outcome=args.outcome,
        improvement_observed=(
            args.success
        ),
        confidence_delta=args.delta,
    )

    print(
        "Validation recorded:"
    )

    print(
        validation.capability_name
    )


def command_report(
    _: argparse.Namespace,
) -> None:
    """
    Display system report.
    """

    report = generate_system_report()

    print(
        json.dumps(
            report,
            indent=2,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    """
    Construct CLI parser.
    """

    parser = argparse.ArgumentParser(
        description=(
            "AI Self-Reflection Engine"
        )
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )


    initialize = commands.add_parser(
        "initialize",
        help="Initialize memory storage",
    )

    initialize.set_defaults(
        function=command_initialize,
    )


    record = commands.add_parser(
        "record",
        help="Record reflection event",
    )

    record.add_argument(
        "--task",
        required=True,
    )

    record.add_argument(
        "--category",
        required=True,
    )

    record.add_argument(
        "--observation",
        required=True,
    )

    record.add_argument(
        "--friction",
        required=True,
    )

    record.add_argument(
        "--root-cause",
        dest="root_cause",
        required=True,
    )

    record.add_argument(
        "--lesson",
        required=True,
    )

    record.add_argument(
        "--scope",
        required=True,
    )

    record.add_argument(
        "--confidence",
        type=float,
        required=True,
    )

    record.add_argument(
        "--evidence",
        type=int,
        default=1,
    )

    record.add_argument(
        "--action",
        required=True,
    )

    record.add_argument(
        "--audience",
        nargs="*",
    )

    record.add_argument(
        "--criteria",
        nargs="*",
    )

    record.add_argument(
        "--corrections",
        type=int,
        default=0,
    )

    record.add_argument(
        "--clarifications",
        type=int,
        default=0,
    )

    record.add_argument(
        "--reprompts",
        type=int,
        default=0,
    )

    record.set_defaults(
        function=command_record,
    )


    distill = commands.add_parser(
        "distill",
        help="Generate candidate lessons",
    )

    distill.set_defaults(
        function=command_distill,
    )


    promote = commands.add_parser(
        "promote",
        help="Promote capabilities",
    )

    promote.set_defaults(
        function=command_promote,
    )


    validate = commands.add_parser(
        "validate",
        help="Validate capability",
    )

    validate.add_argument(
        "--capability",
        required=True,
    )

    validate.add_argument(
        "--task",
        required=True,
    )

    validate.add_argument(
        "--outcome",
        required=True,
    )

    validate.add_argument(
        "--success",
        action="store_true",
    )

    validate.add_argument(
        "--delta",
        type=float,
        default=0.05,
    )

    validate.set_defaults(
        function=command_validate,
    )


    report = commands.add_parser(
        "report",
        help="Generate system report",
    )

    report.set_defaults(
        function=command_report,
    )


    return parser


def main():
    """
    CLI entry point.
    """

    parser = build_parser()

    args = parser.parse_args()

    args.function(
        args
    )


if __name__ == "__main__":
    main()
