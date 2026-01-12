"""Unit tests for audio processing and conversion routines."""
import sys
from pathlib import Path
import numpy as np

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.audio.processor import pcm16_to_float32, float32_to_pcm16, AudioBuffer


def test_pcm16_to_float32_conversion():
    """Verify conversion of raw bytes to normalized float32."""
    # 0 in int16 -> 0.0 in float32
    # 32767 in int16 -> ~1.0 in float32
    # -32768 in int16 -> -1.0 in float32
    raw = np.array([0, 16384, -16384, 32767, -32768], dtype=np.int16).tobytes()
    float_arr = pcm16_to_float32(raw)

    assert isinstance(float_arr, np.ndarray)
    assert float_arr.dtype == np.float32
    assert len(float_arr) == 5
    assert np.isclose(float_arr[0], 0.0, atol=1e-4)
    assert np.isclose(float_arr[1], 0.5, atol=1e-3)
    assert np.isclose(float_arr[2], -0.5, atol=1e-3)
    assert np.isclose(float_arr[3], 1.0, atol=1e-3)
    assert np.isclose(float_arr[4], -1.0, atol=1e-3)


def test_pcm16_empty_and_odd_bytes():
    """Verify handling of empty or malformed byte sequences."""
    empty_res = pcm16_to_float32(b"")
    assert len(empty_res) == 0

    # 3 bytes (1 sample + 1 trailing orphaned byte)
    odd_bytes = b"\x00\x00\xff"
    res = pcm16_to_float32(odd_bytes)
    assert len(res) == 1


def test_float32_to_pcm16_roundtrip():
    """Verify float32 to PCM16 roundtrip preserves values within precision."""
    original = np.array([-1.0, -0.5, 0.0, 0.5, 1.0], dtype=np.float32)
    pcm_bytes = float32_to_pcm16(original)
    recovered = pcm16_to_float32(pcm_bytes)

    assert len(recovered) == len(original)
    assert np.allclose(original, recovered, atol=1e-3)


def test_audio_buffer_lifecycle():
    """Verify AudioBuffer accumulation, thresholding, and clearing."""
    buffer = AudioBuffer(sampling_rate=16000, min_chunk_seconds=0.3)
    # 0.3s at 16000Hz * 2 bytes = 9600 bytes
    assert buffer.min_bytes == 9600
    assert not buffer.has_enough_data()

    # Append 4800 bytes (0.15s)
    half_chunk = b"\x00" * 4800
    buffer.append(half_chunk)
    assert not buffer.has_enough_data()
    assert np.isclose(buffer.duration_seconds(), 0.15, atol=1e-3)

    # Append another 4800 bytes (reaches 0.3s)
    buffer.append(half_chunk)
    assert buffer.has_enough_data()
    assert np.isclose(buffer.duration_seconds(), 0.30, atol=1e-3)

    # Pop all
    popped = buffer.pop_all()
    assert len(popped) == 4800  # 9600 bytes / 2 bytes per sample
    assert not buffer.has_enough_data()
    assert buffer.duration_seconds() == 0.0
