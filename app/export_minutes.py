
from pathlib import Path
import re


# XML 1.0 does not allow these characters in DOCX text.
# Valid tabs, newlines, carriage returns, and Unicode are preserved.
_INVALID_XML_10_CHARS = re.compile(
    r"[\x00-\x08\x0B\x0C\x0E-\x1F\uD800-\uDFFF\uFFFE\uFFFF]"
)


def _sanitize_docx_text(value):
    """Remove characters that XML 1.0 does not allow in DOCX text."""
    return _INVALID_XML_10_CHARS.sub("", str(value))


def export_minutes(minutes, output_path, file_format=None):
    """
    Export structured meeting minutes to TXT or DOCX.

    Missing values are displayed as "Not specified".
    Supports TXT and DOCX formats.
    """

    output_path = Path(output_path)
    fmt = (file_format or output_path.suffix.lstrip(".")).lower()

    if fmt not in ("txt", "docx"):
        raise ValueError("Supported formats are TXT and DOCX.")

    title = minutes.get("title")

    topics = minutes.get("topics", [])
    decisions = minutes.get("decisions", [])
    action_items = minutes.get("action_items", [])

    # Build TXT content. TXT export remains unchanged.
    lines = [
        str(title) if title else "MEETING MINUTES",
        ""
    ]

    # Discussion Topics
    lines.append("DISCUSSION TOPICS")

    if topics:
        lines.extend(f"- {item}" for item in topics)
    else:
        lines.append("None recorded.")

    lines.append("")

    # Decisions
    lines.append("DECISIONS")

    if decisions:
        lines.extend(f"- {item}" for item in decisions)
    else:
        lines.append("None recorded.")

    lines.append("")

    # Action Items
    lines.append("ACTION ITEMS")

    if action_items:
        for item in action_items:
            task = item.get("task") or "Not specified"
            owner = item.get("owner") or "Not specified"
            deadline = item.get("deadline") or "Not specified"

            lines.append(f"- Task: {task}")
            lines.append(f"  Owner: {owner}")
            lines.append(f"  Deadline: {deadline}")
    else:
        lines.append("None recorded.")

    # Export as TXT
    if fmt == "txt":
        output_path.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

    # Export as DOCX
    else:
        try:
            from docx import Document
        except ImportError as exc:
            raise ImportError(
                "Install python-docx using: "
                "python3 -m pip install python-docx"
            ) from exc

        document = Document()

        # Meeting title
        document.add_heading(
            _sanitize_docx_text(title) if title else "Meeting Minutes",
            level=0
        )

        # Discussion Topics
        document.add_heading("Discussion Topics", level=1)

        if topics:
            for item in topics:
                clean_item = _sanitize_docx_text(item)
                document.add_paragraph(f"• {clean_item}")
        else:
            document.add_paragraph("None recorded.")

        # Decisions
        document.add_heading("Decisions", level=1)

        if decisions:
            for item in decisions:
                clean_item = _sanitize_docx_text(item)
                document.add_paragraph(f"• {clean_item}")
        else:
            document.add_paragraph("None recorded.")

        # Action Items
        document.add_heading("Action Items", level=1)

        if action_items:
            for item in action_items:
                task = item.get("task") or "Not specified"
                owner = item.get("owner") or "Not specified"
                deadline = item.get("deadline") or "Not specified"

                document.add_paragraph(
                    f"Task: {_sanitize_docx_text(task)}"
                )
                document.add_paragraph(
                    f"Owner: {_sanitize_docx_text(owner)}"
                )
                document.add_paragraph(
                    f"Deadline: {_sanitize_docx_text(deadline)}"
                )
        else:
            document.add_paragraph("None recorded.")

        document.save(str(output_path))

    return str(output_path)
