"""Audio format conversion, channel downmixing, and resampling utilities."""
from __future__ import annotations

import math
from typing import Tuple
import numpy as np

try:
    from scipy import signal
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


def to_mono_float32(audio_data: np.ndarray) -> np.ndarray:
    """
    Convert multi-channel or single-channel audio array to 1D float32 normalized in [-1.0, 1.0].
    """
    if audio_data.ndim > 1:
        # Multi-channel (e.g. shape [samples, channels]): average across channels
        audio_data = np.mean(audio_data, axis=1)

    if np.issubdtype(audio_data.dtype, np.floating):
        return audio_data.astype(np.float32)
    elif audio_data.dtype == np.int16:
        return (audio_data / 32768.0).astype(np.float32)
    elif audio_data.dtype == np.int32:
        return (audio_data / 2147483648.0).astype(np.float32)
    elif audio_data.dtype == np.uint8:
        return ((audio_data.astype(np.float32) - 128.0) / 128.0).astype(np.float32)
    else:
        return audio_data.astype(np.float32)


def resample_to_16k(audio_data: np.ndarray, orig_sr: int, target_sr: int = 16000) -> np.ndarray:
    """
    Resample a 1D float32 audio array from orig_sr to target_sr (default 16000 Hz).
    """
    if orig_sr == target_sr or len(audio_data) == 0:
        return audio_data.astype(np.float32)

    if _HAS_SCIPY:
        # Compute GCD for efficient polyphase resampling
        gcd = math.gcd(orig_sr, target_sr)
        up = target_sr // gcd
        down = orig_sr // gcd
        resampled = signal.resample_poly(audio_data, up, down)
        return resampled.astype(np.float32)
    else:
        # Fallback linear interpolation
        new_len = int(round(len(audio_data) * target_sr / orig_sr))
        x_orig = np.linspace(0, 1, len(audio_data), endpoint=False)
        x_target = np.linspace(0, 1, new_len, endpoint=False)
        return np.interp(x_target, x_orig, audio_data).astype(np.float32)


def float32_to_pcm16_bytes(audio_float32: np.ndarray) -> bytes:
    """Convert normalized 1D float32 numpy array to 16-bit signed PCM little-endian bytes."""
    clipped = np.clip(audio_float32, -1.0, 1.0)
    int16_arr = (clipped * 32767.0).astype(np.int16)
    return int16_arr.tobytes()


def calculate_rms(audio_float32: np.ndarray) -> float:
    """Calculate Root Mean Square (RMS) energy level in [0.0, 1.0]."""
    if len(audio_float32) == 0:
        return 0.0
    return float(np.sqrt(np.mean(audio_float32 ** 2)))
