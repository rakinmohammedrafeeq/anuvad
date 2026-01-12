"""Unit tests for desktop audio capture, downmixing, resampling, and device enumeration."""
import math
import numpy as np
import pytest

from desktop.audio.resampler import (
    to_mono_float32,
    resample_to_16k,
    float32_to_pcm16_bytes,
    calculate_rms,
)
from desktop.audio.mic_capture import MicrophoneCapture
from desktop.audio.loopback_capture import SystemAudioCapture


def test_to_mono_stereo_downmix():
    """Verify stereo [samples, 2] audio downmixes to [samples] with channel averaging."""
    left = np.full((100, 1), 0.8, dtype=np.float32)
    right = np.full((100, 1), 0.2, dtype=np.float32)
    stereo = np.hstack([left, right])

    mono = to_mono_float32(stereo)
    assert mono.ndim == 1
    assert len(mono) == 100
    assert np.allclose(mono, 0.5, atol=1e-5)


def test_to_mono_int16_normalization():
    """Verify int16 audio is properly normalized to float32 [-1.0, 1.0]."""
    raw_int16 = np.array([-32768, 0, 16384, 32767], dtype=np.int16)
    mono = to_mono_float32(raw_int16)

    assert mono.dtype == np.float32
    assert mono.ndim == 1
    assert math.isclose(mono[0], -1.0, rel_tol=1e-3)
    assert math.isclose(mono[1], 0.0, abs_tol=1e-5)
    assert math.isclose(mono[2], 0.5, rel_tol=1e-3)
    assert math.isclose(mono[3], 1.0, rel_tol=1e-3)


def test_resample_48k_to_16k():
    """Verify 48kHz audio resamples to 16kHz with exact 3:1 ratio."""
    # 4800 samples at 48kHz = 100ms
    orig_samples = 4800
    audio_48k = np.sin(np.linspace(0, 100 * math.pi, orig_samples, dtype=np.float32))

    resampled = resample_to_16k(audio_48k, orig_sr=48000, target_sr=16000)
    # Expected output length is 1600 samples (100ms at 16kHz)
    assert len(resampled) == 1600
    assert resampled.dtype == np.float32


def test_resample_same_rate_noop():
    """Verify resampling with orig_sr == target_sr returns same length array."""
    audio = np.ones(500, dtype=np.float32)
    resampled = resample_to_16k(audio, orig_sr=16000, target_sr=16000)
    assert len(resampled) == 500
    assert np.array_equal(audio, resampled)


def test_resample_empty_array():
    """Verify empty array is safely handled."""
    empty = np.array([], dtype=np.float32)
    resampled = resample_to_16k(empty, orig_sr=48000, target_sr=16000)
    assert len(resampled) == 0


def test_float32_to_pcm16_bytes():
    """Verify float32 to signed 16-bit PCM little-endian conversion."""
    audio = np.array([-1.0, 0.0, 1.0], dtype=np.float32)
    pcm_bytes = float32_to_pcm16_bytes(audio)

    assert len(pcm_bytes) == 6  # 3 samples * 2 bytes
    unpacked = np.frombuffer(pcm_bytes, dtype=np.int16)
    assert unpacked[0] == -32767 or unpacked[0] == -32768
    assert unpacked[1] == 0
    assert unpacked[2] == 32767


def test_calculate_rms():
    """Verify RMS energy computation on silence and non-silent signals."""
    silence = np.zeros(500, dtype=np.float32)
    assert calculate_rms(silence) == 0.0

    constant = np.full(500, 0.5, dtype=np.float32)
    assert math.isclose(calculate_rms(constant), 0.5, rel_tol=1e-4)


def test_microphone_device_enumeration():
    """Verify list_input_devices runs without unhandled exceptions."""
    devices = MicrophoneCapture.list_input_devices()
    assert isinstance(devices, list)
    # If system has microphones, each should have standard fields
    for d in devices:
        assert "name" in d
        assert "index" in d
        assert "channels" in d


def test_loopback_device_enumeration():
    """Verify list_loopback_devices runs and discovers WASAPI loopback devices."""
    assert SystemAudioCapture.is_supported() is True
    devices = SystemAudioCapture.list_loopback_devices()
    assert isinstance(devices, list)
    for d in devices:
        assert "name" in d
        assert "index" in d
