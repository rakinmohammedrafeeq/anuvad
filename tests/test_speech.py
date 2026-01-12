"""Unit tests for speech streaming processor and hallucination deduplication."""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.speech.streaming import deduplicate_text, StreamingASRProcessor


def test_deduplicate_text_normal():
    """Verify standard sentences without repetition are untouched."""
    text = "Hello, can you hear me? The meeting is starting now."
    assert deduplicate_text(text) == text


def test_deduplicate_single_word_loop():
    """Verify single word repetitions (3+ repeats) are collapsed."""
    text = "going going going going to the store"
    assert deduplicate_text(text) == "going to the store"


def test_deduplicate_multiword_phrase_loop():
    """Verify multi-word phrases repeating consecutively are collapsed."""
    text = "than I was going than I was going than I was going"
    assert deduplicate_text(text) == "than I was going"


def test_deduplicate_user_hallucination_loop():
    """Verify long phrase repetitions (Whisper-style output) are collapsed."""
    # Whisper hallucinates by DIRECTLY repeating phrases without separator words
    text = "I was going to be a little bit more nervous I was going to be a little bit more nervous"
    cleaned = deduplicate_text(text)
    assert cleaned.count("I was going to be a little bit more nervous") == 1


def test_streaming_processor_initialization_and_reset():
    """Verify StreamingASRProcessor lifecycle and reset."""
    processor = StreamingASRProcessor(
        model_manager=None,
        source_language="en",
        target_language="es",
        enable_vad=False,
    )
    assert processor.source_language == "en"
    assert processor.target_language == "es"
    assert len(processor.audio_buffer) == 0

    processor.reset()
    assert len(processor.audio_buffer) == 0
    assert len(processor.last_hypothesis_words) == 0
