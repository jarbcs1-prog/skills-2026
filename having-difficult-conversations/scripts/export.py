"""Export conversation plans and results to various formats."""
from pathlib import Path


def export_markdown(conversation_data: dict, output_path: str) -> str:
    """Export conversation template or result to Markdown."""
    lines = []

    if "template" in conversation_data:
        lines.append(f"# {conversation_data.get('type', 'Conversation').title()} Template")
        lines.append(f"**Framework:** {conversation_data.get('framework', 'N/A')}")
        lines.append("")

        if "preparation" in conversation_data:
            lines.append("## Preparation")
            for item in conversation_data["preparation"]:
                lines.append(f"- [ ] {item}")
            lines.append("")

        if "flow" in conversation_data:
            lines.append("## Conversation Flow")
            for i, step in enumerate(conversation_data["flow"], 1):
                lines.append(f"{i}. {step}")
            lines.append("")

        if "common_reactions" in conversation_data:
            lines.append("## Common Reactions & Responses")
            for reaction, response in conversation_data["common_reactions"].items():
                lines.append(f"| {reaction} | {response} |")
            lines.append("")

        if "follow_up" in conversation_data:
            lines.append("## Follow-up")
            for item in conversation_data["follow_up"]:
                lines.append(f"- [ ] {item}")
            lines.append("")

    content = "\n".join(lines)
    Path(output_path).write_text(content)
    return content


def export_pdf(conversation_data: dict, output_path: str) -> str:
    """Export conversation template to PDF-ready format."""
    markdown = export_markdown(conversation_data, output_path.replace(".pdf", ".md"))
    Path(output_path).write_text(markdown)
    return markdown