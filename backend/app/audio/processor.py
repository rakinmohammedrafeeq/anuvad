"""Audio format conversion and buffer management."""
from __future__ import annotations

import logging
import numpy as np

logger = logging.getLogger("anuvad.audio.processor")


def pcm16_to_float32(pcm_bytes: bytes) -> np.ndarray:
    """
    Convert raw PCM16 (signed 16-bit little-endian) bytes to normalized float32 numpy array.
    
    Args:
        pcm_bytes: Raw PCM audio bytes.
        
    Returns:
        np.ndarray: 1D array of float32 samples in range [-1.0, 1.0].
    """
    if not pcm_bytes:
        return np.array([], dtype=np.float32)

    # Ensure even number of bytes for 16-bit integers
    length = len(pcm_bytes) - (len(pcm_bytes) % 2)
    if length <= 0:
        return np.array([], dtype=np.float32)

    try:
        audio_int16 = np.frombuffer(pcm_bytes[:length], dtype=np.int16)
        # Normalize to [-1.0, 1.0]
        return audio_int16.astype(np.float32) / 32768.0
    except Exception as e:
        logger.error(f"Error converting PCM16 to float32: {e}")
        return np.array([], dtype=np.float32)


def float32_to_pcm16(float_array: np.ndarray) -> bytes:
    """
    Convert normalized float32 numpy array to raw PCM16 bytes.
    
    Args:
        float_array: 1D array of float32 samples in range [-1.0, 1.0].
        
    Returns:
        bytes: Raw PCM16 audio bytes.
    """
    if float_array is None or len(float_array) == 0:
        return b""

    # Clip to valid range and scale
    clipped = np.clip(float_array, -1.0, 1.0)
    int16_samples = (clipped * 32767.0).astype(np.int16)
    return int16_samples.tobytes()


class AudioBuffer:
    """Accumulates audio bytes and produces float32 chunks when minimum size is reached."""

    def __init__(self, sampling_rate: int = 16000, min_chunk_seconds: float = 0.3):
        self.sampling_rate = sampling_rate
        self.min_chunk_seconds = min_chunk_seconds
        # 2 bytes per sample (PCM16)
        self.min_bytes = int(min_chunk_seconds * sampling_rate * 2)
        self._buffer: list[bytes] = []
        self._total_bytes: int = 0

    def append(self, data: bytes) -> None:
        """Append raw PCM16 audio bytes to buffer."""
        if data:
            self._buffer.append(data)
            self._total_bytes += len(data)

    def has_enough_data(self) -> bool:
        """Check if buffer has reached the minimum chunk size."""
        return self._total_bytes >= self.min_bytes

    def pop_all(self) -> np.ndarray:
        """Pop all accumulated bytes and return as float32 array."""
        if not self._buffer:
            return np.array([], dtype=np.float32)

        combined = b"".join(self._buffer)
        self.clear()
        return pcm16_to_float32(combined)

    def duration_seconds(self) -> float:
        """Current duration of buffered audio in seconds."""
        # 2 bytes per sample at sampling_rate
        return self._total_bytes / (self.sampling_rate * 2)

    def clear(self) -> None:
        """Reset the buffer."""
        self._buffer.clear()
        self._total_bytes = 0
