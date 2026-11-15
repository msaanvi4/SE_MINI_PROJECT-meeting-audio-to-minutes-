from pathlib import Path
from dataclasses import dataclass
import io

import av


MAX_FILE_SIZE = 100 * 1024 * 1024

SUPPORTED_FORMATS = {
    ".wav": "WAV",
    ".mp3": "MP3",
    ".m4a": "M4A",
}


@dataclass
class ValidationResult:
    valid: bool
    format: str
    size: int
    message: str


class AudioValidator:
    """Validate the extension, size, container signature, and decodability."""

    @staticmethod
    def validate(file):
        filename = getattr(file, "name", "")
        extension = Path(filename).suffix.lower()

        if extension not in SUPPORTED_FORMATS:
            return ValidationResult(
                False,
                "",
                0,
                "Unsupported file format. Upload WAV, MP3, or M4A.",
            )

        try:
            file.seek(0)
            audio_data = file.read()
            file.seek(0)
        except Exception:
            return ValidationResult(
                False,
                SUPPORTED_FORMATS[extension],
                0,
                "Unable to read the uploaded audio file.",
            )

        size = len(audio_data)

        if size == 0:
            return ValidationResult(
                False,
                SUPPORTED_FORMATS[extension],
                0,
                "The uploaded file is empty.",
            )

        if size > MAX_FILE_SIZE:
            return ValidationResult(
                False,
                SUPPORTED_FORMATS[extension],
                size,
                "File exceeds the 100 MB size limit.",
            )

        if not AudioValidator._has_valid_signature(extension, audio_data):
            return ValidationResult(
                False,
                SUPPORTED_FORMATS[extension],
                size,
                "The file appears corrupted or is not a valid audio file.",
            )

        if not AudioValidator._is_decodable_audio(extension, audio_data):
            return ValidationResult(
                False,
                SUPPORTED_FORMATS[extension],
                size,
                "The file has an audio-like header but contains no decodable "
                "audio. Upload a valid WAV, MP3, or M4A recording.",
            )

        return ValidationResult(
            True,
            SUPPORTED_FORMATS[extension],
            size,
            "Audio file validated successfully.",
        )

    @staticmethod
    def _has_valid_signature(extension, data):
        """Perform a quick container/header check before decoding."""
        if extension == ".wav":
            return (
                len(data) >= 12
                and data[:4] == b"RIFF"
                and data[8:12] == b"WAVE"
            )

        if extension == ".mp3":
            return (
                data.startswith(b"ID3")
                or (
                    len(data) >= 2
                    and data[0] == 0xFF
                    and (data[1] & 0xE0) == 0xE0
                )
            )

        if extension == ".m4a":
            return len(data) >= 12 and data[4:8] == b"ftyp"

        return False

    @staticmethod
    def _is_decodable_audio(extension, data):
        """
        Ask FFmpeg (through PyAV) to find an audio stream and decode at least
        one frame. A matching extension or header alone is not sufficient.
        """
        try:
            with av.open(io.BytesIO(data), mode="r") as container:
                audio_streams = container.streams.audio
                if not audio_streams:
                    return False

                stream = audio_streams[0]

                # Check that the detected container is compatible with the
                # extension, rather than accepting arbitrary renamed media.
                format_name = (container.format.name or "").lower()

                if extension == ".wav" and "wav" not in format_name:
                    return False

                if extension == ".mp3" and "mp3" not in format_name:
                    return False

                if extension == ".m4a" and not any(
                    name in format_name
                    for name in ("mov", "mp4", "m4a")
                ):
                    return False

                for _frame in container.decode(audio=stream.index):
                    return True

                return False

        except (av.error.FFmpegError, OSError, ValueError, EOFError):
            return False
        except Exception:
            # Invalid or truncated media can raise other decoder exceptions.
            return False
