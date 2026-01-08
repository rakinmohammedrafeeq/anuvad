"""Voice Activity Detection using Silero VAD with fallback."""
from __future__ import annotations

import logging
import numpy as np

logger = logging.getLogger("anuvad.audio.vad")


class SileroVAD:
    """Silero VAD manager for detecting speech activity in audio chunks."""
    
    def __init__(self, sampling_rate: int = 16000, threshold: float = 0.5):
        self.sampling_rate = sampling_rate
        self.threshold = threshold
        self.model = None
        self.available = False
        self._load_model()

    def _load_model(self):
        try:
            import torch
            logger.info("Loading Silero VAD model...")
            # Use torch.hub with trust_repo=True to avoid interactive prompts
            model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                onnx=False,
                trust_repo=True
            )
            self.model = model
            self.available = True
            logger.info("Silero VAD model initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Silero VAD: {e}. Falling back to energy-based VAD.")
            self.available = False
            self.model = None

    def is_speech(self, audio: np.ndarray) -> bool:
        """
        Check if the given audio contains speech anywhere in its active window.
        
        Args:
            audio: 1D float32 numpy array with values in [-1.0, 1.0].
            
        Returns:
            bool: True if speech is detected, False otherwise.
        """
        if audio is None or len(audio) == 0:
            return False

        # Fast RMS pre-check: if digital silence / noise floor (< -60 dBFS), return False (<0.02ms)
        rms = float(np.sqrt(np.mean(np.square(audio))))
        if rms < 0.001:
            return False

        # If Silero model is available, evaluate recent frames (up to last 16000 samples ~ 1.0s)
        if self.available and self.model is not None:
            try:
                import torch
                # Focus on the most recent 1.0s where speech activity typically resides
                window = audio[-16000:] if len(audio) > 16000 else audio
                if len(window) < 512:
                    padded = np.pad(window, (0, 512 - len(window)))
                else:
                    padded = window

                # Evaluate 512-sample frames with step 1024 for sub-millisecond evaluation
                with torch.no_grad():
                    for i in range(0, len(padded) - 511, 1024):
                        chunk = padded[i : i + 512]
                        tensor_chunk = torch.from_numpy(chunk).float()
                        prob = self.model(tensor_chunk, self.sampling_rate).item()
                        if prob >= self.threshold:
                            return True
                return False
            except Exception as e:
                logger.debug(f"Silero VAD error: {e}, falling back to energy VAD")

        # Fallback: simple RMS energy detection
        return bool(rms > 0.003)

    def is_tail_speech(self, audio: np.ndarray, tail_duration_s: float = 0.25) -> bool:
        """
        Check if speech is actively occurring at the very tail of the buffer.
        Returns False if the speaker has paused or stopped speaking in the last tail_duration_s.
        """
        if audio is None or len(audio) == 0:
            return False

        tail_samples = int(tail_duration_s * self.sampling_rate)
        tail = audio[-tail_samples:] if len(audio) >= tail_samples else audio
        rms = float(np.sqrt(np.mean(np.square(tail))))
        if rms < 0.0015:
            return False

        if self.available and self.model is not None:
            try:
                import torch
                padded = np.pad(tail, (0, max(0, 512 - len(tail)))) if len(tail) < 512 else tail
                with torch.no_grad():
                    for i in range(0, len(padded) - 511, 512):
                        chunk = padded[i : i + 512]
                        tensor_chunk = torch.from_numpy(chunk).float()
                        prob = self.model(tensor_chunk, self.sampling_rate).item()
                        if prob >= self.threshold:
                            return True
                return False
            except Exception:
                pass

        return bool(rms > 0.003)

    def reset_states(self):
        """Reset internal recurrent states if model supports it."""
        if self.available and self.model is not None:
            try:
                self.model.reset_states()
            except Exception:
                pass
