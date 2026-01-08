"""Configuration management for Anuvad."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from dataclasses import dataclass, field
import logging

try:
    from dotenv import load_dotenv
    # Load .env file from repository root or backend directory
    root_dir = Path(__file__).resolve().parent.parent.parent
    env_file = root_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("anuvad.config")


SUPPORTED_LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "ru": "Russian",
    "hi": "Hindi",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "sv": "Swedish",
    "da": "Danish",
    "no": "Norwegian",
    "fi": "Finnish",
    "cs": "Czech",
    "sk": "Slovak",
    "hu": "Hungarian",
    "ro": "Romanian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "sl": "Slovenian",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "uk": "Ukrainian",
}


@dataclass
class AppConfig:
    host: str = field(default_factory=lambda: os.getenv("HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    
    # Whisper Model settings
    whisper_model: str = field(default_factory=lambda: os.getenv("WHISPER_MODEL", "tiny"))
    device: str = field(default_factory=lambda: os.getenv("DEVICE", "auto"))
    compute_type: str = field(default_factory=lambda: os.getenv("COMPUTE_TYPE", "auto"))
    model_dir: str | None = field(default_factory=lambda: os.getenv("MODEL_DIR", None))
    cache_dir: str | None = field(default_factory=lambda: os.getenv("CACHE_DIR", None))
    
    # Audio processing settings
    sampling_rate: int = field(default_factory=lambda: int(os.getenv("SAMPLING_RATE", "16000")))
    min_chunk_size: float = field(default_factory=lambda: float(os.getenv("MIN_CHUNK_SIZE", "0.15")))
    enable_vad: bool = field(default_factory=lambda: os.getenv("ENABLE_VAD", "true").lower() in ("true", "1", "yes"))
    vad_threshold: float = field(default_factory=lambda: float(os.getenv("VAD_THRESHOLD", "0.5")))
    
    # Translation settings
    enable_translation: bool = field(default_factory=lambda: os.getenv("ENABLE_TRANSLATION", "true").lower() in ("true", "1", "yes"))
    translation_engine: str = field(default_factory=lambda: os.getenv("TRANSLATION_ENGINE", "auto"))
    google_translate_api_key: str | None = field(default_factory=lambda: os.getenv("GOOGLE_TRANSLATE_API_KEY", None))
    default_source_language: str = field(default_factory=lambda: os.getenv("DEFAULT_SOURCE_LANGUAGE", "en"))
    default_target_language: str = field(default_factory=lambda: os.getenv("DEFAULT_TARGET_LANGUAGE", "es"))
    
    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    # Web static directory
    static_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "web")

    def __post_init__(self):
        # Resolve device
        if self.device == "auto":
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"
                
        # Resolve compute type
        if self.compute_type == "auto":
            if self.device == "cuda":
                self.compute_type = "float16"
            else:
                self.compute_type = "int8"


# Global singleton instance
config = AppConfig()
