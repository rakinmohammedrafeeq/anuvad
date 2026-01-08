"""Speech recognition package."""
from .model import WhisperModelManager, get_model_manager
from .streaming import StreamingASRProcessor

__all__ = ["WhisperModelManager", "get_model_manager", "StreamingASRProcessor"]
