
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from transcription import TranscriptResult


class FakeUploadedAudio(BytesIO):
    """Minimal uploaded-file stand-in for the Streamlit workflow test."""

    name = "test-meeting.wav"
    size = 44

    def __init__(self):
        super().__init__(b"RIFF" + b"\x00" * 40)


def click_button(at, label):
    """Find and click a Streamlit button by its displayed label."""
    matches = [button for button in at.button if button.label == label]

    assert len(matches) == 1, (
        f"Expected one button named {label!r}; "
        f"found {[button.label for button in at.button]}"
    )

    matches[0].click()
    at.run()


def test_editable_minutes_save_and_docx_download_workflow(tmp_path):
    """Exercise upload, transcription, extraction, editing and DOCX export."""

    # Create a real temporary file for the application's path check.
    audio_path = tmp_path / "test-meeting.wav"
    audio_path.write_bytes(b"RIFF" + b"\x00" * 40)

    # Mock transcription so the real Whisper model is not loaded.
    fake_adapter = SimpleNamespace(
        transcribe=lambda audio: TranscriptResult(
            text="We discussed the project plan and assigned tasks.",
            status="Transcription completed successfully.",
        )
    )

    # Mock extraction while keeping the real editor and exporter.
    extraction_result = {
        "topics": ["Initial topic"],
        "decisions": ["Initial decision"],
        "action_items": [
            {
                "task": "Prepare initial report",
                "owner": "Alex",
                "deadline": "Nov 12",
            }
        ],
        "review_flags": [],
    }

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(app_path)

    with (
        patch(
            "streamlit.file_uploader",
            return_value=FakeUploadedAudio(),
        ),
        patch(
            "validated_audio.validate_and_save",
            return_value=SimpleNamespace(
                valid=True,
                path=str(audio_path),
                message="Audio validated successfully.",
            ),
        ),
        patch(
            "transcription.TranscriptionAdapter",
            return_value=fake_adapter,
        ),
        patch(
            "app.extraction.extract_minutes",
            return_value=extraction_result,
        ),
    ):
        # Initial upload screen.
        at.run()
        assert not at.exception

        # Step 1: Validate the uploaded recording.
        click_button(at, "Validate Audio")
        assert not at.exception

        # Step 2: Transcribe the validated recording.
        click_button(at, "Transcribe Audio")
        assert not at.exception

        assert at.session_state["transcript"] == (
            "We discussed the project plan and assigned tasks."
        )

        # Step 3: Generate the initial meeting minutes.
        click_button(at, "Generate Meeting Minutes")
        assert not at.exception

        # One transcript text area and three minutes text areas.
        assert len(at.text_input) == 1
        assert len(at.text_area) == 4

        # Step 4: Edit the meeting title, topics and decisions.
        at.text_input[0].set_value("Sprint 2 Review \u2013 Q&A")

        # Index 0 is the transcript editor. Leave it unchanged.
        # Index 1 contains the topics.
        at.text_area[1].set_value(
            "Updated topic\nCaf\u00e9 discussion"
        )

        # Index 2 contains the decisions.
        at.text_area[2].set_value(
            "Approve the revised plan"
        )

        # Index 3 contains the action items.
        # Include literal pipes in task descriptions and metadata.
        at.text_area[3].set_value(
            "Prepare final | report | Owner: Priya | Deadline: Nov 13\n"
            "Review transcript | Owner: | Deadline:\n"
            "Review A | B transcript"
        )

        # Step 5: Save the edited minutes.
        click_button(at, "Save Edited Minutes")

        assert not at.exception

        saved = at.session_state["validated_minutes"]

        # Verify the saved minutes exist.
        assert saved is not None

        # Verify the title, topics and decisions.
        assert saved.title == "Sprint 2 Review \u2013 Q&A"

        assert saved.topics == [
            "Updated topic",
            "Caf\u00e9 discussion",
        ]

        assert saved.decisions == [
            "Approve the revised plan"
        ]

        # Verify task descriptions, owners and deadlines.
        assert [
            (item.task, item.owner, item.deadline)
            for item in saved.action_items
        ] == [
            ("Prepare final | report", "Priya", "Nov 13"),
            (
                "Review transcript",
                "Not specified",
                "Not specified",
            ),
            (
                "Review A | B transcript",
                "Not specified",
                "Not specified",
            ),
        ]

        # Step 6: Verify the editor retains the saved values.
        assert at.text_area[1].value == (
            "Updated topic\nCaf\u00e9 discussion"
        )

        assert at.text_area[2].value == (
            "Approve the revised plan"
        )

        assert "Prepare final | report" in at.text_area[3].value
        assert "Review transcript" in at.text_area[3].value
        assert "Review A | B transcript" in at.text_area[3].value

        # Step 7: Verify the Word download control is available.
        assert len(at.get("download_button")) == 1
