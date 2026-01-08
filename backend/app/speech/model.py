"""Whisper model lifecycle and inference management."""
from __future__ import annotations

import logging
import time
from typing import Any
import numpy as np

from ..config import config

logger = logging.getLogger("anuvad.speech.model")


class WhisperModelManager:
    """Manages the Faster-Whisper model lifecycle to avoid reloading on each connection."""

    _instance: WhisperModelManager | None = None

    def __init__(
        self,
        model_size_or_path: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
        download_root: str | None = None,
    ):
        self.model_size_or_path = model_size_or_path or config.whisper_model
        self.device = device or config.device
        self.compute_type = compute_type or config.compute_type
        self.download_root = download_root or config.cache_dir
        self.model = None
        self.is_loaded = False

    @classmethod
    def get_instance(cls) -> WhisperModelManager:
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self) -> None:
        """Load the Faster-Whisper model into memory."""
        if self.is_loaded and self.model is not None:
            logger.info("Model already loaded.")
            return

        from faster_whisper import WhisperModel

        import os
        cpu_threads = min(6, os.cpu_count() or 4) if self.device == "cpu" else 4
        logger.info(
            f"Loading Faster-Whisper model '{self.model_size_or_path}' on "
            f"device='{self.device}', compute_type='{self.compute_type}', cpu_threads={cpu_threads}..."
        )
        start_time = time.time()
        self.model = WhisperModel(
            self.model_size_or_path,
            device=self.device,
            compute_type=self.compute_type,
            download_root=self.download_root,
            cpu_threads=cpu_threads,
        )
        elapsed = time.time() - start_time
        self.is_loaded = True
        logger.info(f"Model successfully loaded in {elapsed:.2f} seconds.")

    def transcribe(
        self,
        audio: np.ndarray,
        language: str | None = "en",
        task: str = "transcribe",
        initial_prompt: str | None = None,
        beam_size: int = 1,
        condition_on_previous_text: bool = False,
        word_timestamps: bool = True,
        temperature: float = 0.0,
        compression_ratio_threshold: float = 2.2,
        repetition_penalty: float = 1.25,
        no_repeat_ngram_size: int = 3,
        hallucination_silence_threshold: float = 0.4,
        no_speech_threshold: float = 0.6,
        **kwargs: Any,
    ) -> tuple[list[Any], Any]:
        """
        Transcribe or translate an audio array with strict repetition and hallucination suppression.
        """
        if not self.is_loaded or self.model is None:
            self.load_model()

        # Handle 'auto' language
        lang_arg = None if (language == "auto" or not language) else language

        segments_iter, info = self.model.transcribe(
            audio,
            language=lang_arg,
            task=task,
            initial_prompt=initial_prompt,
            beam_size=beam_size,
            condition_on_previous_text=condition_on_previous_text,
            word_timestamps=word_timestamps,
            temperature=temperature,
            compression_ratio_threshold=compression_ratio_threshold,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            hallucination_silence_threshold=hallucination_silence_threshold,
            no_speech_threshold=no_speech_threshold,
            **kwargs,
        )
        return list(segments_iter), info


def get_model_manager() -> WhisperModelManager:
    """Convenience helper to get the singleton WhisperModelManager."""
    return WhisperModelManager.get_instance()
