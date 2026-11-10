from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from minutes_extractor import ActionItem, MinutesDraft


class FakeUploadedAudio(BytesIO):
    """Minimal uploaded-file stand-in; transcription is not invoked in this test."""

    name = "test-meeting.wav"
    size = 44

    def __init__(self):
        super().__init__(b"RIFF" + b"\x00" * 40)


def test_editable_minutes_save_and_docx_download_workflow():
    """Exercise the real Streamlit editor without requiring an audio recording."""
    draft = MinutesDraft(
        topics=["Initial topic"],
        decisions=["Initial decision"],
        action_items=[
            ActionItem(
                task="Prepare initial report",
                owner="Alex",
                deadline="Nov 12",
            )
        ],
        review_flags=[],
    )

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(app_path)
    at.session_state["minutes_draft"] = draft
    at.session_state["minutes_review_flags"] = []

    # Keep the upload branch active without invoking audio validation/transcription.
    with patch("streamlit.file_uploader", return_value=FakeUploadedAudio()):
        at.run()

        assert not at.exception
        assert len(at.form_submit_button) == 1
        assert len(at.text_input) == 1
        assert len(at.text_area) == 3

        at.text_input[0].set_value("Sprint 2 Review – Q&A")
        at.text_area[0].set_value("Updated topic\nCafé discussion")
        at.text_area[1].set_value("Approve the revised plan")
        at.text_area[2].set_value(
            "Prepare final report | Owner: Priya | Deadline: Nov 13\n"
            "Review transcript | Owner: | Deadline:"
        )
        at.form_submit_button[0].click().run()

    assert not at.exception

    saved = at.session_state["validated_minutes"]
    assert saved.title == "Sprint 2 Review – Q&A"
    assert saved.topics == ["Updated topic", "Café discussion"]
    assert saved.decisions == ["Approve the revised plan"]
    assert [
        (item.task, item.owner, item.deadline)
        for item in saved.action_items
    ] == [
        ("Prepare final report", "Priya", "Nov 13"),
        ("Review transcript", "Not specified", "Not specified"),
    ]

    # The editor must show the saved values after the Streamlit rerun.
    assert at.text_area[0].value == "Updated topic\nCafé discussion"
    assert at.text_area[1].value == "Approve the revised plan"
    assert "Prepare final report" in at.text_area[2].value
    assert "Review transcript" in at.text_area[2].value

    # A successful save must expose the Word download control.
    assert len(at.get("download_button")) == 1
