import io
import unittest
import wave
from pathlib import Path

from audio_validator import AudioValidator


def make_wav():
    """Create a small, genuinely decodable PCM WAV file."""
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        wav_file.writeframes(b"\x00\x00" * 800)
    return output.getvalue()


def make_file(data, name):
    file = io.BytesIO(data)
    file.name = name
    return file


class UploadedAudioFile:
    """File-like wrapper that exposes the filename expected by AudioValidator."""

    def __init__(self, path):
        self.name = path.name
        self._file = path.open("rb")

    def read(self, *args):
        return self._file.read(*args)

    def seek(self, *args):
        return self._file.seek(*args)

    def close(self):
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class TestAudioValidator(unittest.TestCase):

    def test_supported_wav_with_decodable_audio(self):
        result = AudioValidator.validate(
            make_file(make_wav(), "meeting.wav")
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.format, "WAV")
        self.assertIn("successfully", result.message.lower())

    def test_valid_mp3_audio(self):
        path = Path(__file__).parent / "tests" / "fixtures" / "audio" / "valid_sample.mp3"
        with UploadedAudioFile(path) as audio:
            result = AudioValidator.validate(audio)

        self.assertTrue(result.valid)
        self.assertEqual(result.format, "MP3")
        self.assertIn("successfully", result.message.lower())

    def test_valid_m4a_audio(self):
        path = Path(__file__).parent / "tests" / "fixtures" / "audio" / "valid_sample.m4a"
        with UploadedAudioFile(path) as audio:
            result = AudioValidator.validate(audio)

        self.assertTrue(result.valid)
        self.assertEqual(result.format, "M4A")
        self.assertIn("successfully", result.message.lower())

    def test_wav_header_without_audio_data_is_rejected(self):
        # A RIFF/WAVE-looking header is not enough: the data chunk is empty.
        fake_wav = (
            b"RIFF"
            + (36).to_bytes(4, "little")
            + b"WAVE"
            + b"fmt "
            + b"\x10\x00\x00\x00"
            + b"\x01\x00\x01\x00"
            + (8000).to_bytes(4, "little")
            + (16000).to_bytes(4, "little")
            + b"\x02\x00\x10\x00"
            + b"data"
            + b"\x00\x00\x00\x00"
        )

        result = AudioValidator.validate(
            make_file(fake_wav, "fake.wav")
        )

        self.assertFalse(result.valid)

    def test_mp3_id3_header_without_audio_is_rejected(self):
        result = AudioValidator.validate(
            make_file(b"ID3" + b"\x00" * 20, "fake.mp3")
        )

        self.assertFalse(result.valid)

    def test_m4a_ftyp_header_without_audio_is_rejected(self):
        fake_m4a = (
            b"\x00\x00\x00\x18"
            + b"ftyp"
            + b"M4A "
            + b"\x00\x00\x00\x00"
            + b"isom"
            + b"\x00\x00\x00\x00"
        )

        result = AudioValidator.validate(
            make_file(fake_m4a, "fake.m4a")
        )

        self.assertFalse(result.valid)

    def test_unsupported_format(self):
        result = AudioValidator.validate(
            make_file(b"some content", "meeting.txt")
        )

        self.assertFalse(result.valid)
        self.assertIn("Unsupported", result.message)

    def test_empty_file(self):
        result = AudioValidator.validate(make_file(b"", "meeting.wav"))

        self.assertFalse(result.valid)
        self.assertIn("empty", result.message.lower())

    def test_corrupted_audio(self):
        result = AudioValidator.validate(
            make_file(b"not an audio file", "meeting.wav")
        )

        self.assertFalse(result.valid)

    def test_file_over_100_mb(self):
        class LargeFile:
            name = "meeting.wav"

            def seek(self, position):
                pass

            def read(self):
                return b"x" * (100 * 1024 * 1024 + 1)

        result = AudioValidator.validate(LargeFile())

        self.assertFalse(result.valid)
        self.assertIn("100 MB", result.message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
