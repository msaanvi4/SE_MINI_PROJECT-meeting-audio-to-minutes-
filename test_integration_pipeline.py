import wave
import unittest
from io import BytesIO

from audio_validator import AudioValidator
from minutes_extractor import MinutesExtractor


class TestMeetingPipelineIntegration(unittest.TestCase):

    def test_validated_audio_to_structured_minutes(self):

        # Step 1: Create a valid, decodable WAV test file.
        wav_buffer = BytesIO()

        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(8000)
            wav_file.writeframes(b"\x00\x00" * 800)

        wav_data = wav_buffer.getvalue()

        uploaded_file = BytesIO(wav_data)
        uploaded_file.name = "sample.wav"
        # Step 2: Validate the uploaded audio.
        validation = AudioValidator.validate(uploaded_file)

        self.assertTrue(validation.valid)
        self.assertEqual(validation.format, "WAV")
        self.assertEqual(validation.size, len(wav_data))

        # Step 3: Simulate transcription output.
        fake_transcript = (
            "We discussed the project timeline. "
            "Ravi will submit the report by Friday. "
            "Priya will prepare the presentation by Monday. "
            "The team decided to use Python."
        )

        # Step 4: Extract structured meeting minutes.
        minutes = MinutesExtractor.extract(fake_transcript)

        # Step 5: Verify topic and decision extraction.
        self.assertTrue(len(minutes.topics) > 0)
        self.assertTrue(len(minutes.decisions) > 0)

        # Step 6: Verify both action items.
        self.assertEqual(len(minutes.action_items), 2)

        self.assertEqual(minutes.action_items[0].owner, "Ravi")
        self.assertEqual(minutes.action_items[0].deadline, "Friday")

        self.assertEqual(minutes.action_items[1].owner, "Priya")
        self.assertEqual(minutes.action_items[1].deadline, "Monday")


if __name__ == "__main__":
    unittest.main(verbosity=2)
