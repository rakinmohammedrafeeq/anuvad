"""Unit tests for the translation service and fallbacks."""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.translation.translator import BaseTranslator, ResilientTranslator


class MockWorkingTranslator(BaseTranslator):
    """Mock translator that reverses text as simulated translation."""

    def __init__(self, prefix="es_"):
        self.prefix = prefix
        self.call_count = 0

    def translate(self, text: str, src: str = "auto", dest: str = "es") -> str | None:
        self.call_count += 1
        return f"{self.prefix}{text}"


class MockFailingTranslator(BaseTranslator):
    """Mock translator that always fails (e.g. simulating HTTP 429)."""

    def __init__(self):
        self.call_count = 0

    def translate(self, text: str, src: str = "auto", dest: str = "es") -> str | None:
        self.call_count += 1
        return None


def test_same_language_bypass():
    """Verify that when source and destination are identical, text is returned unmodified."""
    translator = ResilientTranslator()
    result = translator.translate("Hello world", src="en", dest="en")
    assert result == "Hello world"


def test_empty_string_handling():
    """Verify handling of empty or blank input strings."""
    translator = ResilientTranslator()
    assert translator.translate("", src="en", dest="es") is None
    assert translator.translate("   ", src="en", dest="es") is None
    assert translator.translate(None, src="en", dest="es") is None


def test_translator_caching():
    """Verify caching prevents redundant translation calls."""
    translator = ResilientTranslator()
    mock = MockWorkingTranslator(prefix="es_")
    translator.engines = [mock]

    # First call
    res1 = translator.translate("Good morning", src="en", dest="es")
    assert res1 == "es_Good morning"
    assert mock.call_count == 1

    # Second call with same text and languages should hit cache
    res2 = translator.translate("Good morning", src="en", dest="es")
    assert res2 == "es_Good morning"
    assert mock.call_count == 1


def test_resilient_fallback():
    """Verify that a failing primary engine falls back to secondary engine."""
    translator = ResilientTranslator()
    failing_engine = MockFailingTranslator()
    working_fallback = MockWorkingTranslator(prefix="fallback_")

    translator.engines = [failing_engine, working_fallback]

    result = translator.translate("Welcome", src="en", dest="es")
    assert result == "fallback_Welcome"
    assert failing_engine.call_count == 1
    assert working_fallback.call_count == 1
