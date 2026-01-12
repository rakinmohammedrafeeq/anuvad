"""Unit tests for configuration loading and validation."""
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import AppConfig, SUPPORTED_LANGUAGES


def test_default_config():
    """Verify sensible default configuration values."""
    cfg = AppConfig()
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 8000
    assert cfg.whisper_model == "tiny"
    assert cfg.sampling_rate == 16000
    assert cfg.min_chunk_size == 0.3
    assert cfg.enable_vad is True
    assert cfg.enable_translation is True
    assert cfg.device in ("cpu", "cuda")
    assert cfg.compute_type in ("int8", "float16")


def test_supported_languages():
    """Verify supported languages structure and essential entries."""
    assert "en" in SUPPORTED_LANGUAGES
    assert "es" in SUPPORTED_LANGUAGES
    assert "fr" in SUPPORTED_LANGUAGES
    assert "hi" in SUPPORTED_LANGUAGES
    assert "auto" in SUPPORTED_LANGUAGES
    assert SUPPORTED_LANGUAGES["en"] == "English"
    assert SUPPORTED_LANGUAGES["es"] == "Spanish"


def test_env_override(monkeypatch):
    """Verify that environment variables properly override defaults."""
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("WHISPER_MODEL", "base")
    monkeypatch.setenv("ENABLE_VAD", "false")
    monkeypatch.setenv("ENABLE_TRANSLATION", "false")

    cfg = AppConfig()
    assert cfg.host == "0.0.0.0"
    assert cfg.port == 9000
    assert cfg.whisper_model == "base"
    assert cfg.enable_vad is False
    assert cfg.enable_translation is False
