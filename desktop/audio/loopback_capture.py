"""Windows WASAPI Loopback system audio capture using pyaudiowpatch."""
from __future__ import annotations

import logging
import threading
from typing import Callable, Dict, List, Optional
import numpy as np

try:
    import pyaudiowpatch as pyaudio
    _HAS_PYAUDIO = True
except ImportError:
    _HAS_PYAUDIO = False

from .resampler import to_mono_float32, resample_to_16k, float32_to_pcm16_bytes, calculate_rms

logger = logging.getLogger("anuvad.desktop.loopback")


class SystemAudioCapture:
    """
    Captures computer system playback audio (e.g. YouTube, meetings, lectures)
    via Windows WASAPI Loopback and resamples it to 16kHz mono PCM16 bytes.
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

        self._pa: Optional[pyaudio.PyAudio] = None
        self._stream = None
        self._is_recording = False
        self._capture_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @staticmethod
    def is_supported() -> bool:
        """Check if WASAPI loopback is supported in the current environment."""
        return _HAS_PYAUDIO

    @staticmethod
    def list_loopback_devices() -> List[Dict[str, any]]:
        """List all available WASAPI loopback (speaker output capture) devices."""
        if not _HAS_PYAUDIO:
            return []

        devices = []
        p = pyaudio.PyAudio()
        try:
            # Find default WASAPI output device for reference
            default_output_name = ""
            try:
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
                default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
                default_output_name = default_speakers.get("name", "")
            except Exception:
                pass

            for loopback in p.get_loopback_device_info_generator():
                name = loopback.get("name", "")
                idx = loopback.get("index")
                is_def = default_output_name and (default_output_name in name)
                devices.append({
                    "index": idx,
                    "name": name,
                    "channels": loopback.get("maxInputChannels", 2),
                    "samplerate": int(loopback.get("defaultSampleRate", 48000)),
                    "is_default": is_def,
                })
        except Exception as e:
            logger.error(f"Error enumerating WASAPI loopback devices: {e}")
        finally:
            p.terminate()

        return devices

    def start(self, device_index: Optional[int] = None) -> None:
        """Start capturing system playback audio."""
        if not _HAS_PYAUDIO:
            raise RuntimeError("System Audio Capture requires 'pyaudiowpatch' library on Windows.")

        if self._is_recording:
            return

        if device_index is not None:
            self.device_index = device_index

        self._pa = pyaudio.PyAudio()

        # Find target loopback device
        target_dev = None
        if self.device_index is not None:
            try:
                target_dev = self._pa.get_device_info_by_index(self.device_index)
            except Exception:
                pass

        if target_dev is None:
            # Default loopback device
            try:
                wasapi_info = self._pa.get_host_api_info_by_type(pyaudio.paWASAPI)
                default_speakers = self._pa.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
                if not default_speakers.get("isLoopbackDevice", False):
                    for loopback in self._pa.get_loopback_device_info_generator():
                        if default_speakers["name"] in loopback["name"]:
                            target_dev = loopback
                            break
                else:
                    target_dev = default_speakers
            except Exception as e:
                logger.warning(f"Could not automatically locate default loopback device: {e}")

        if target_dev is None:
            # Fallback: take the first available loopback device
            try:
                for loopback in self._pa.get_loopback_device_info_generator():
                    target_dev = loopback
                    break
            except Exception:
                pass

        if target_dev is None:
            self._pa.terminate()
            self._pa = None
            raise RuntimeError("No active Windows WASAPI audio playback device found for System Audio capture.")

        dev_index = target_dev["index"]
        channels = int(target_dev.get("maxInputChannels", 2))
        samplerate = int(target_dev.get("defaultSampleRate", 48000))
        # Block size for ~128ms packets
        blocksize = int(samplerate * (self.chunk_duration_ms / 1000.0))

        logger.info(f"Opening WASAPI Loopback on '{target_dev['name']}' (index={dev_index}, rate={samplerate}, ch={channels}, block={blocksize})")

        try:
            self._stream = self._pa.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=samplerate,
                input=True,
                input_device_index=dev_index,
                frames_per_buffer=blocksize,
            )
        except Exception as e:
            self._pa.terminate()
            self._pa = None
            raise RuntimeError(f"Failed to open WASAPI loopback stream on {target_dev['name']}: {e}")

        self._is_recording = True
        self._stop_event.clear()
        self._capture_thread = threading.Thread(
            target=self._capture_loop,
            args=(samplerate, channels, blocksize),
            daemon=True,
            name="Anuvad-LoopbackCapture",
        )
        self._capture_thread.start()

    def _capture_loop(self, samplerate: int, channels: int, blocksize: int) -> None:
        """Background thread continuously reading loopback audio frames."""
        logger.info("System audio capture thread started.")
        while self._is_recording and not self._stop_event.is_set():
            try:
                # Read raw float32 bytes from WASAPI loopback stream
                data = self._stream.read(blocksize, exception_on_overflow=False)
                if not data or not self._is_recording:
                    continue

                # Convert raw bytes to numpy float32 array
                audio_np = np.frombuffer(data, dtype=np.float32)
                if channels > 1:
                    audio_np = audio_np.reshape(-1, channels)

                # Downmix to mono float32
                mono_f32 = to_mono_float32(audio_np)

                # Resample to 16kHz
                if samplerate != self.target_sample_rate:
                    mono_f32 = resample_to_16k(mono_f32, samplerate, self.target_sample_rate)

                rms = calculate_rms(mono_f32)
                pcm_bytes = float32_to_pcm16_bytes(mono_f32)

                if self.on_audio_chunk and self._is_recording:
                    self.on_audio_chunk(pcm_bytes, rms)

            except Exception as e:
                if self._is_recording:
                    logger.debug(f"Loopback read error or stream interrupt: {e}")

        logger.info("System audio capture thread terminated.")

    def stop(self) -> None:
        """Stop capturing system playback audio."""
        self._is_recording = False
        self._stop_event.set()

        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception as e:
                logger.warning(f"Error closing loopback stream: {e}")
            finally:
                self._stream = None

        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=1.0)
            self._capture_thread = None

        if self._pa is not None:
            try:
                self._pa.terminate()
            except Exception:
                pass
            finally:
                self._pa = None

        logger.info("System audio capture stopped.")
