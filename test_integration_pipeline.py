
import unittest
from io import BytesIO

from audio_validator import AudioValidator
from minutes_extractor import MinutesExtractor


class TestMeetingPipelineIntegration(unittest.TestCase):

    def test_validated_audio_to_structured_minutes(self):

        # Step 1: Create a WAV-like test file.
        wav_data = (
            b"RIFF"
            + (36).to_bytes(4, "little")
            + b"WAVE"
            + b"fmt "
            + b"\x00" * 24
        )

        uploaded_file = BytesIO(wav_data)
        uploaded_file.name = "sample.wav"

        # Step 2: Validate the uploaded audio.
        validation = AudioValidator.validate(uploaded_file)

        self.assertTrue(validation.valid)
        self.assertEqual(validation.format, "WAV")

        # Step 3: Simulate the output from transcription.
        fake_transcript = (
            "The meeting is about the project timeline. "
            "Ravi will submit the report by Friday. "
            "Priya will prepare the presentation by Monday. "
            "The team decided to use Python."
        )

        # Step 4: Extract structured meeting minutes.
        minutes = MinutesExtractor.extract(fake_transcript)

        # Step 5: Verify extracted information.
        self.assertTrue(minutes.topics)
        self.assertTrue(minutes.decisions)
        self.assertEqual(len(minutes.action_items), 2)

        self.assertEqual(minutes.action_items[0].owner, "Ravi")
        self.assertEqual(minutes.action_items[1].owner, "Priya")


if __name__ == "__main__":
    unittest.main(verbosity=2)
