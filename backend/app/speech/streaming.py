"""Streaming ASR processor with low-latency local agreement and dynamic trimming."""
from __future__ import annotations

import time
import logging
from typing import Any
import numpy as np

from .model import WhisperModelManager, get_model_manager
from ..audio.vad import SileroVAD
from ..config import config

logger = logging.getLogger("anuvad.speech.streaming")


def deduplicate_text(text: str) -> str:
    """
    Suppress repetitive hallucination loops from ASR decoders.
    Handles:
      - Single words repeated 2+ consecutive times ("going going going")
      - Multi-word phrases repeated 2+ consecutive times ("than I was going than I was going")
      - Long phrases that appear only twice but are the entire output
    """
    if not text or not text.strip():
        return text

    import re

    # Phase 1: Token-level sliding window deduplication.
    # Works left to right; for each window size n, collapse runs of n repeated tokens.
    words = text.split()
    n_words = len(words)

    # Try every possible phrase length from longest to shortest so we catch big loops first
    changed = True
    while changed:
        changed = False
        new_words = words[:]
        n_words = len(new_words)
        for n in range(min(n_words // 2, 20), 0, -1):
            i = 0
            result = []
            while i < len(new_words):
                # Check if there's a run of at least 2 identical n-grams starting here
                chunk = [w.lower() for w in new_words[i: i + n]]
                if len(chunk) < n:
                    result.extend(new_words[i:])
                    break
                run = 1
                j = i + n
                while j + n <= len(new_words):
                    next_chunk = [w.lower() for w in new_words[j: j + n]]
                    if next_chunk == chunk:
                        run += 1
                        j += n
                    else:
                        break
                if run >= 2:
                    # Emit only the first occurrence
                    result.extend(new_words[i: i + n])
                    i = j  # Skip all repetitions
                    changed = True
                else:
                    result.append(new_words[i])
                    i += 1
            if changed:
                words = result
                break  # restart outer loop with updated words

    cleaned = " ".join(words)

    # Phase 2: Regex cleanup for any leftover single-character repeated punctuation artifacts
    import re
    cleaned = re.sub(r'([.!?])\1{2,}', r'\1', cleaned)

    return cleaned


class StreamingASRProcessor:
    """Processes streaming audio chunks with sub-second latency and zero backlog."""

    def __init__(
        self,
        model_manager: WhisperModelManager | None = None,
        source_language: str = "en",
        target_language: str = "es",
        sampling_rate: int = 16000,
        min_chunk_seconds: float = 0.15,
        enable_vad: bool = True,
    ):
        self.model_manager = model_manager or get_model_manager()
        self.source_language = source_language
        self.target_language = target_language
        self.sampling_rate = sampling_rate
        self.min_chunk_seconds = min_chunk_seconds
        self.min_chunk_samples = int(min_chunk_seconds * sampling_rate)
        self.enable_vad = enable_vad

        self.vad = SileroVAD(sampling_rate=sampling_rate, threshold=config.vad_threshold) if enable_vad else None

        self.audio_buffer: np.ndarray = np.array([], dtype=np.float32)
        self.last_processed_samples: int = 0
        self.last_hypothesis_words: list[tuple[float, float, str]] = []
        self.total_time_offset: float = 0.0
        self.last_committed_text: str = ""
        self.last_committed_time: float = 0.0

    def insert_audio_chunk(self, chunk: np.ndarray) -> None:
        """Append float32 audio chunk to internal buffer with strict backlog ceiling."""
        if chunk is not None and len(chunk) > 0:
            self.audio_buffer = np.concatenate((self.audio_buffer, chunk))
            # Strict backlog cap: prevent memory & inference delay runaway (max 2.5s)
            max_samples = int(2.5 * self.sampling_rate)
            if len(self.audio_buffer) > max_samples:
                drop = len(self.audio_buffer) - max_samples
                self.audio_buffer = self.audio_buffer[drop:]
                self.last_processed_samples = max(0, self.last_processed_samples - drop)
                self.total_time_offset += (drop / self.sampling_rate)

    def has_enough_audio(self) -> bool:
        """Check if sufficient fresh audio has accumulated for an inference pass."""
        if len(self.audio_buffer) < self.min_chunk_samples:
            return False
        return (len(self.audio_buffer) - self.last_processed_samples) >= self.min_chunk_samples

    def process_iter(self) -> dict[str, Any] | None:
        """
        Process current audio buffer if sufficient audio is accumulated.
        
        Returns:
            dict with transcription details or None if no update.
        """
        if not self.has_enough_audio():
            return None

        self.last_processed_samples = len(self.audio_buffer)
        buffer_duration = len(self.audio_buffer) / self.sampling_rate

        # Quick VAD check across entire active buffer
        has_speech = True
        tail_speaking = True
        if self.enable_vad and self.vad is not None:
            has_speech = self.vad.is_speech(self.audio_buffer)
            # If completely silent and no in-flight hypothesis, discard excess silence
            if not has_speech and len(self.last_hypothesis_words) == 0:
                if buffer_duration > 1.0:
                    keep = int(self.sampling_rate * 0.25)
                    self.audio_buffer = self.audio_buffer[-keep:]
                    self.last_processed_samples = len(self.audio_buffer)
                return None
            tail_speaking = self.vad.is_tail_speech(self.audio_buffer, tail_duration_s=0.20)

        try:
            # Transcribe active buffer without prompt feedback loop to prevent autoregressive hallucinations
            segments, _ = self.model_manager.transcribe(
                self.audio_buffer,
                language=self.source_language,
                beam_size=1,
                word_timestamps=True,
                initial_prompt=None,
                condition_on_previous_text=False,
                temperature=0.0,
            )

            words: list[tuple[float, float, str]] = []
            for segment in segments:
                if getattr(segment, "no_speech_prob", 0.0) > 0.8:
                    continue
                if hasattr(segment, "words") and segment.words:
                    for w in segment.words:
                        if w.word and w.word.strip():
                            words.append((w.start, w.end, w.word))
                elif segment.text and segment.text.strip():
                    words.append((segment.start, segment.end, segment.text))

            # Handle case where no speech was transcribed
            if not words:
                # If speech stopped and we had an uncommitted hypothesis, finalize it
                if (not has_speech or not tail_speaking) and self.last_hypothesis_words:
                    final_text = deduplicate_text("".join(w[2] for w in self.last_hypothesis_words).strip())
                    start_ms = int((self.total_time_offset + self.last_hypothesis_words[0][0]) * 1000)
                    end_ms = int((self.total_time_offset + self.last_hypothesis_words[-1][1]) * 1000)
                    self.total_time_offset += buffer_duration
                    self.audio_buffer = np.array([], dtype=np.float32)
                    self.last_processed_samples = 0
                    self.last_hypothesis_words = []
                    if final_text:
                        return {
                            "type": "transcription",
                            "text": final_text,
                            "start": start_ms,
                            "end": end_ms,
                            "isFinal": True,
                        }
                return None

            # Local Agreement: Find agreed prefix with previous hypothesis
            agreed_count = 0
            min_len = min(len(self.last_hypothesis_words), len(words))
            for i in range(min_len):
                w1 = self.last_hypothesis_words[i][2].strip().lower()
                w2 = words[i][2].strip().lower()
                if w1 == w2 and w1 != "":
                    agreed_count += 1
                else:
                    break

            # If user paused speaking (tail silence detected) or buffer reached 2.0s ceiling, commit all words in buffer
            if ((not tail_speaking or not has_speech) and len(words) > 0 and buffer_duration >= 0.20) or (buffer_duration >= 2.0 and len(words) > 0):
                agreed_count = len(words)

            if agreed_count > 0:
                # Commit agreed words
                committed = words[:agreed_count]
                raw_committed = "".join(w[2] for w in committed).strip()
                committed_text = deduplicate_text(raw_committed)
                start_ms = int((self.total_time_offset + committed[0][0]) * 1000)
                end_ms = int((self.total_time_offset + committed[-1][1]) * 1000)

                cut_time = committed[-1][1]
                cut_samples = int(cut_time * self.sampling_rate)

                # If all words in buffer are committed, purge entire buffer to prevent re-transcription & hallucination loops
                if agreed_count == len(words):
                    self.total_time_offset += buffer_duration
                    self.audio_buffer = np.array([], dtype=np.float32)
                    self.last_processed_samples = 0
                    self.last_hypothesis_words.clear()
                elif 0 < cut_samples < len(self.audio_buffer):
                    self.audio_buffer = self.audio_buffer[cut_samples:]
                    self.last_processed_samples = max(0, self.last_processed_samples - cut_samples)
                    self.total_time_offset += cut_time
                    self.last_hypothesis_words = [
                        (max(0.0, w[0] - cut_time), max(0.0, w[1] - cut_time), w[2])
                        for w in words[agreed_count:]
                    ]
                else:
                    self.total_time_offset += buffer_duration
                    self.audio_buffer = np.array([], dtype=np.float32)
                    self.last_processed_samples = 0
                    self.last_hypothesis_words.clear()

                # Deduplicate rapid duplicate commits
                now_ts = time.time()
                if committed_text and (committed_text.lower() != self.last_committed_text.lower() or (now_ts - self.last_committed_time) > 1.2):
                    self.last_committed_text = committed_text
                    self.last_committed_time = now_ts
                    return {
                        "type": "transcription",
                        "text": committed_text,
                        "start": start_ms,
                        "end": end_ms,
                        "isFinal": True,
                    }

            # Emit interim partial hypothesis
            self.last_hypothesis_words = words
            raw_partial = "".join(w[2] for w in words).strip()
            partial_text = deduplicate_text(raw_partial)
            start_ms = int((self.total_time_offset + words[0][0]) * 1000)
            end_ms = int((self.total_time_offset + words[-1][1]) * 1000)
            return {
                "type": "transcription",
                "text": partial_text,
                "start": start_ms,
                "end": end_ms,
                "isFinal": False,
            }

        except Exception as e:
            logger.error(f"Error during streaming ASR processing: {e}")
            return None

    def finish(self) -> dict[str, Any] | None:
        """Flush final remaining speech when session stops."""
        # If we have an existing hypothesis waiting to be committed, commit it
        if self.last_hypothesis_words:
            raw_text = "".join(w[2] for w in self.last_hypothesis_words).strip()
            text = deduplicate_text(raw_text)
            start_ms = int((self.total_time_offset + self.last_hypothesis_words[0][0]) * 1000)
            end_ms = int((self.total_time_offset + self.last_hypothesis_words[-1][1]) * 1000)
            self.last_hypothesis_words = []
            self.audio_buffer = np.array([], dtype=np.float32)
            self.last_processed_samples = 0
            if text:
                return {
                    "type": "transcription",
                    "text": text,
                    "start": start_ms,
                    "end": end_ms,
                    "isFinal": True,
                }

        # Otherwise, if uncommitted audio is left in the buffer, transcribe it
        if len(self.audio_buffer) >= int(0.25 * self.sampling_rate):
            try:
                segments, _ = self.model_manager.transcribe(
                    self.audio_buffer,
                    language=self.source_language,
                    beam_size=1,
                    initial_prompt=None,
                    condition_on_previous_text=False,
                    temperature=0.0,
                )
                final_parts = []
                for segment in segments:
                    if getattr(segment, "no_speech_prob", 0.0) > 0.8:
                        continue
                    if segment.text and segment.text.strip():
                        final_parts.append(segment.text.strip())
                text = deduplicate_text(" ".join(final_parts).strip())
                self.audio_buffer = np.array([], dtype=np.float32)
                self.last_processed_samples = 0
                if text:
                    return {
                        "type": "transcription",
                        "text": text,
                        "start": int(self.total_time_offset * 1000),
                        "end": int((self.total_time_offset + 0.5) * 1000),
                        "isFinal": True,
                    }
            except Exception as e:
                logger.debug(f"Finish transcribe error: {e}")

        return None

    def reset(self) -> None:
        """Reset internal buffers for a fresh recording session."""
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_processed_samples = 0
        self.last_hypothesis_words.clear()
        self.total_time_offset = 0.0
        if self.vad is not None:
            self.vad.reset_states()

    def update_languages(self, source_language: str, target_language: str) -> str:
        """Update active languages for this stream."""
        old_source = self.source_language
        old_target = self.target_language
        self.source_language = source_language
        self.target_language = target_language

        if old_source != source_language:
            self.last_hypothesis_words.clear()
            logger.info(f"Source language updated: {old_source} -> {source_language}")
            return "source_changed"
        elif old_target != target_language:
            logger.info(f"Target language updated: {old_target} -> {target_language}")
            return "target_changed"
        return "no_change"
