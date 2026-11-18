
import statistics
import tempfile
import time
from pathlib import Path

from app.extraction import extract_minutes
from app.export_minutes import export_minutes


def benchmark(function, runs=5):
    """Run a function repeatedly and return its execution times."""
    timings = []

    for _ in range(runs):
        start = time.perf_counter()
        function()
        elapsed = time.perf_counter() - start
        timings.append(elapsed)

    return timings


def main():
    # Generate a repeatable synthetic meeting transcript.
    sentences = []

    for i in range(200):
        sentences.append(
            f"We discussed project topic number {i}."
        )
        sentences.append(
            f"The team approved implementation plan number {i}."
        )
        sentences.append(
            f"Alex will prepare report number {i} by Monday."
        )

    transcript = " ".join(sentences)

    word_count = len(transcript.split())
    sentence_count = len(sentences)

    print("MEETING MINUTES PERFORMANCE BENCHMARK")
    print("=" * 45)
    print(f"Transcript words: {word_count}")
    print(f"Transcript sentences: {sentence_count}")
    print("Runs per operation: 5")
    print()

    # Benchmark minutes extraction.
    extraction_times = benchmark(
        lambda: extract_minutes(transcript)
    )

    minutes = extract_minutes(transcript)

    print("1. MINUTES EXTRACTION")
    print(f"Average: {statistics.mean(extraction_times):.6f} seconds")
    print(f"Median:  {statistics.median(extraction_times):.6f} seconds")
    print(f"Minimum: {min(extraction_times):.6f} seconds")
    print(f"Topics extracted: {len(minutes['topics'])}")
    print(f"Decisions extracted: {len(minutes['decisions'])}")
    print(f"Action items extracted: {len(minutes['action_items'])}")
    print()

    # Prepare structured minutes for DOCX export.
    export_data = {
        "title": "Performance Benchmark Meeting",
        "topics": minutes["topics"],
        "decisions": minutes["decisions"],
        "action_items": minutes["action_items"],
    }

    # Benchmark DOCX generation in a temporary directory.
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "benchmark_minutes.docx"

        export_times = benchmark(
            lambda: export_minutes(export_data, output_path)
        )

        file_size = output_path.stat().st_size

    print("2. DOCX EXPORT")
    print(f"Average: {statistics.mean(export_times):.6f} seconds")
    print(f"Median:  {statistics.median(export_times):.6f} seconds")
    print(f"Minimum: {min(export_times):.6f} seconds")
    print(f"Generated DOCX size: {file_size / 1024:.2f} KB")
    print()

    print("=" * 45)
    print("BENCHMARK COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
