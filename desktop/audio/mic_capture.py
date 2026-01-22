"""Microphone audio capture using sounddevice."""
from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional
import numpy as np
import sounddevice as sd

from .resampler import to_mono_float32, resample_to_16k, float32_to_pcm16_bytes, calculate_rms

logger = logging.getLogger("anuvad.desktop.mic")


class MicrophoneCapture:
    """
    Captures live audio from a microphone device and converts it to 16kHz mono PCM16 bytes.
    """

    def __init__(
        self,
        on_audio_chunk: Optional[Callable[[bytes, float], None]] = None,
        device_index: Optional[int] = None,
        target_sample_rate: int = 16000,
        chunk_duration_ms: int = 50,
    ):
        self.on_audio_chunk = on_audio_chunk
        self.device_index = device_index
        self.target_sample_rate = target_sample_rate
        self.chunk_duration_ms = chunk_duration_ms

        self._stream: Optional[sd.InputStream] = None
        self._is_recording = False
        self._capture_sample_rate = target_sample_rate

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @staticmethod
    def list_input_devices() -> List[Dict[str, any]]:
        """List all available microphone/input devices on the system."""
        devices = []
        try:
            device_list = sd.query_devices()
            default_input = sd.default.device[0]
            for idx, dev in enumerate(device_list):
                if dev.get("max_input_channels", 0) > 0:
                    devices.append({
                        "index": idx,
                        "name": dev.get("name", f"Device {idx}"),
                        "hostapi": dev.get("hostapi"),
                        "channels": dev.get("max_input_channels"),
                        "default_samplerate": dev.get("default_samplerate", 16000),
                        "is_default": (idx == default_input),
                    })
        except Exception as e:
            logger.error(f"Error querying input devices: {e}")
        return devices

    def start(self, device_index: Optional[int] = None) -> None:
        """Start capturing microphone audio."""
        if self._is_recording:
            return

        if device_index is not None:
            self.device_index = device_index

        # Determine optimal sample rate for the selected device
        try:
            dev_info = sd.query_devices(self.device_index, "input") if self.device_index is not None else sd.query_devices(kind="input")
            native_rate = int(dev_info.get("default_samplerate", 44100))
        except Exception:
            native_rate = 44100

        # Try opening at 16000Hz directly; if unsupported, fall back to native device rate
        rates_to_try = [self.target_sample_rate, native_rate, 48000, 44100]
        opened = False
        last_err = None

        for rate in rates_to_try:
            try:
                blocksize = int(rate * (self.chunk_duration_ms / 1000.0))
                self._stream = sd.InputStream(
                    device=self.device_index,
                    channels=1,
                    samplerate=rate,
                    dtype="float32",
                    blocksize=blocksize,
                    callback=self._audio_callback,
                )
                self._stream.start()
                self._capture_sample_rate = rate
                opened = True
                logger.info(f"Microphone stream started on device {self.device_index} at {rate}Hz (blocksize={blocksize})")
                break
            except Exception as e:
                last_err = e
                continue

        if not opened:
            self._is_recording = False
            raise RuntimeError(f"Failed to open microphone input stream: {last_err}")

        self._is_recording = True

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """Callback invoked by sounddevice for each new audio buffer."""
        if status:
            logger.debug(f"sounddevice status: {status}")

        if not self._is_recording or self.on_audio_chunk is None:
            return

        try:
            mono_f32 = to_mono_float32(indata)
            if self._capture_sample_rate != self.target_sample_rate:
                mono_f32 = resample_to_16k(mono_f32, self._capture_sample_rate, self.target_sample_rate)

            rms = calculate_rms(mono_f32)
            pcm_bytes = float32_to_pcm16_bytes(mono_f32)

            self.on_audio_chunk(pcm_bytes, rms)
        except Exception as e:
            logger.error(f"Error in microphone callback: {e}")

    def stop(self) -> None:
        """Stop capturing microphone audio."""
        self._is_recording = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                logger.warning(f"Error closing microphone stream: {e}")
            finally:
                self._stream = None
        logger.info("Microphone stream stopped.")
