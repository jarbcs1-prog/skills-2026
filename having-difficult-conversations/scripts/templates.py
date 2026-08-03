"""Conversation templates for difficult conversations."""
from dataclasses import dataclass
from typing import List


@dataclass
class ConversationTemplate:
    name: str
    type: str
    framework: str
    preparation: List[str]
    flow: List[str]
    common_reactions: dict
    follow_up: List[str]


FEEDBACK_TEMPLATE = ConversationTemplate(
    name="Performance Improvement",
    type="feedback",
    framework="SBI + Crystal Clear Warning",
    preparation=[
        "Identify specific behavior",
        "Document impact on team/project/client",
        "Define desired outcome with measurable change + timeframe",
        "Prepare warning script with clear consequences",
    ],
    flow=[
        "Opening (Radical Candor): 'I care about your growth AND I need to address something directly.'",
        "SBI: Situation → Behavior → Impact",
        "Pause: Let them respond. 'What did you hear me say?'",
        "Expectation: Clear, measurable, timebound",
        "Support: 'Here's how I'll help: [resources, check-ins]'",
        "Warning (if needed): Crystal clear consequences",
        "Close: 'What did you hear me say?' + Next steps",
    ],
    common_reactions={
        "Defensiveness": '"I hear you. Not attacking - want us to work better together."',
        "Denial": '"What did you hear me say?"',
        "Emotional": '"This is hard. Let\'s take a moment."',
        "Agreement": '"Great. Let\'s document the plan and check in [date]."',
    },
    follow_up=[
        "Email summary within 24 hours",
        "Check-in scheduled: [date]",
        "Support resources provided: [list]",
        "My debrief: [15 min reflection]",
    ],
)

TERMINATION_TEMPLATE = ConversationTemplate(
    name="Termination",
    type="termination",
    framework="SBI + Clear Decision",
    preparation=[
        "Review performance documentation",
        "Confirm legal/HR compliance",
        "Prepare separation package details",
        "Schedule private meeting with HR present if needed",
    ],
    flow=[
        "Opening: 'I want to discuss something difficult about your role.'",
        "SBI: Situation → Behavior → Impact",
        "Decision: 'After careful consideration, we have decided to end your employment.'",
        "Details: Final date, separation package, benefits continuation",
        "Support: Outplacement resources, reference policy",
        "Close: 'Is there anything you need from us today?'",
    ],
    common_reactions={
        "Shock": '"I understand this is unexpected. Let me walk you through the details."',
        "Anger": '"I hear your frustration. Let\'s discuss the next steps calmly."',
        "Sadness": '"This is a difficult moment. I appreciate your contributions."',
    },
    follow_up=[
        "Exit interview scheduled",
        "Benefits continuation details provided",
        "Outplacement contact given",
        "Final paycheck and documentation",
    ],
)

CONFLICT_TEMPLATE = ConversationTemplate(
    name="Conflict Resolution",
    type="conflict",
    framework="NVC (Nonviolent Communication)",
    preparation=[
        "Identify the core issue",
        "Gather perspectives from all parties",
        "Define shared goals",
        "Prepare for emotional regulation",
    ],
    flow=[
        "Opening: 'I want to understand your perspective and find a resolution.'",
        "Observation: State facts without judgment",
        "Feeling: Acknowledge emotions",
        "Need: Identify underlying needs",
        "Request: Make a clear, actionable request",
        "Close: Agree on next steps and follow-up",
    ],
    common_reactions={
        "Defensiveness": '"I understand this feels defensive. Let\'s focus on the issue."',
        "Dismissal": '"I hear that this seems unimportant to you. Can we explore why?"',
        "Escalation": '"Let\'s take a step back and revisit this calmly."',
    },
    follow_up=[
        "Document resolution agreement",
        "Schedule follow-up check-in",
        "Monitor for recurrence",
    ],
)

NEGOTIATION_TEMPLATE = ConversationTemplate(
    name="Negotiation",
    type="negotiation",
    framework="Interest-Based Negotiation",
    preparation=[
        "Define your BATNA (Best Alternative to a Negotiated Agreement)",
        "Identify your interests (not positions)",
        "Research the other party's interests",
        "Prepare concession options",
    ],
    flow=[
        "Opening: Establish rapport and agenda",
        "Interests: Share and explore each party's interests",
        "Options: Generate options for mutual gain",
        "Criteria: Agree on objective criteria",
        "Commitment: Document the agreement",
    ],
    common_reactions={
        "Aggressive": '"I understand the urgency. Let\'s find a solution that works for both."',
        "Passive": '"I want to make sure we address your concerns. Can you share more?"',
    },
    follow_up=[
        "Document agreement in writing",
        "Set implementation timeline",
        "Schedule review meeting",
    ],
)