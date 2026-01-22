"""Async WebSocket client running inside a PySide6 QThread."""
from __future__ import annotations

import asyncio
import json
import logging
import queue
from typing import Optional

from PySide6.QtCore import QThread, Signal
import websockets

logger = logging.getLogger("anuvad.desktop.client")


class WebSocketClientThread(QThread):
    """
    Dedicated QThread that manages the WebSocket connection to the Anuvad backend.
    Streams binary PCM audio chunks and dispatches parsed JSON events to the GUI via signals.
    """

    # Signals dispatched to the GUI thread
    connection_changed = Signal(bool, str)     # (is_connected, status_text)
    transcription_received = Signal(str, bool) # (text, is_final)
    translation_received = Signal(str, str, str, bool) # (translated_text, source_text, target_lang, is_final)
    status_received = Signal(str, str)         # (status_type, message)
    error_received = Signal(str)               # (error_message)
    audio_level_received = Signal(float)       # (rms_level 0.0 - 1.0)

    def __init__(self, server_url: str = "ws://127.0.0.1:8000/ws", parent=None):
        super().__init__(parent)
        self.server_url = server_url
        self.source_language = "auto"
        self.target_language = "en"

        self._audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=100)
        self._command_queue: queue.Queue[dict] = queue.Queue()
        self._is_running = True
        self._is_session_active = False
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Return True if WebSocket is actively connected to backend."""
        return self._is_connected

    def set_languages(self, source_lang: str, target_lang: str) -> None:
        """Update source and target languages on the fly."""
        self.source_language = source_lang
        self.target_language = target_lang
        self._command_queue.put({
            "type": "setLanguages",
            "sourceLanguage": source_lang,
            "targetLanguage": target_lang,
        })

    def start_session(self, source_lang: Optional[str] = None, target_lang: Optional[str] = None) -> None:
        """Signal the backend to start a live speech captioning session."""
        if source_lang:
            self.source_language = source_lang
        if target_lang:
            self.target_language = target_lang

        self._is_session_active = True
        # Clear any stale audio
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break

        self._command_queue.put({
            "type": "start",
            "sourceLanguage": self.source_language,
            "targetLanguage": self.target_language,
        })

    def stop_session(self) -> None:
        """Signal the backend to stop the current captioning session and flush."""
        self._is_session_active = False
        self._command_queue.put({"type": "stop"})

    def queue_audio_chunk(self, pcm_bytes: bytes, rms_level: float = 0.0) -> None:
        """Queue raw PCM16 audio bytes to be sent over WebSocket."""
        if not self._is_session_active:
            return

        self.audio_level_received.emit(rms_level)
        try:
            self._audio_queue.put_nowait(pcm_bytes)
        except queue.Full:
            # Drop oldest frame if queue full to prevent lag accumulation
            try:
                self._audio_queue.get_nowait()
                self._audio_queue.put_nowait(pcm_bytes)
            except Exception:
                pass

    def stop_client(self) -> None:
        """Stop the entire client thread."""
        self._is_running = False
        self._is_session_active = False
        self._command_queue.put({"type": "_shutdown"})

    def run(self) -> None:
        """Run the asyncio event loop inside this dedicated QThread."""
        logger.info("WebSocketClientThread starting asyncio event loop...")
        asyncio.run(self._main_async_loop())
        logger.info("WebSocketClientThread event loop finished.")

    async def _main_async_loop(self) -> None:
        """Continuous reconnection and event-handling loop."""
        while self._is_running:
            try:
                self.connection_changed.emit(False, "Connecting...")
                async with websockets.connect(
                    self.server_url,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                    max_size=10 * 1024 * 1024,
                ) as websocket:
                    self._is_connected = True
                    self.connection_changed.emit(True, "Connected")
                    logger.info(f"Connected to Anuvad backend at {self.server_url}")

                    # Run send and receive loops concurrently
                    sender_task = asyncio.create_task(self._send_loop(websocket))
                    receiver_task = asyncio.create_task(self._receive_loop(websocket))

                    done, pending = await asyncio.wait(
                        [sender_task, receiver_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for task in pending:
                        task.cancel()

            except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError) as e:
                self._is_connected = False
                if self._is_running:
                    self.connection_changed.emit(False, "Disconnected (Server Offline)")
                    logger.debug(f"WebSocket disconnected: {e}. Retrying in 2 seconds...")
                    await asyncio.sleep(2.0)
            except Exception as e:
                self._is_connected = False
                if self._is_running:
                    self.error_received.emit(f"Connection error: {e}")
                    logger.error(f"Unexpected WebSocket error: {e}", exc_info=True)
                    await asyncio.sleep(2.0)

        self._is_connected = False
        self.connection_changed.emit(False, "Stopped")

    async def _send_loop(self, websocket) -> None:
        """Pulls audio and commands from queues and sends them over WebSocket."""
        while self._is_running:
            sent_something = False

            # 1. Process control commands
            while not self._command_queue.empty():
                try:
                    cmd = self._command_queue.get_nowait()
                    if cmd.get("type") == "_shutdown":
                        return
                    await websocket.send(json.dumps(cmd))
                    sent_something = True
                except queue.Empty:
                    break

            # 2. Process audio chunks if session is active
            if self._is_session_active:
                while not self._audio_queue.empty():
                    try:
                        chunk = self._audio_queue.get_nowait()
                        await websocket.send(chunk)
                        sent_something = True
                    except queue.Empty:
                        break

            if not sent_something:
                await asyncio.sleep(0.001)

    async def _receive_loop(self, websocket) -> None:
        """Receives messages from backend and dispatches to Qt signals."""
        async for raw_message in websocket:
            if not self._is_running:
                break

            try:
                if isinstance(raw_message, str):
                    data = json.loads(raw_message)
                    msg_type = data.get("type")

                    if msg_type == "transcription":
                        text = data.get("text", "")
                        is_final = data.get("isFinal", False)
                        self.transcription_received.emit(text, is_final)

                    elif msg_type == "translation":
                        text = data.get("text", "")
                        source_text = data.get("sourceText", "")
                        target_lang = data.get("targetLanguage", "")
                        is_final = data.get("isFinal", True)
                        self.translation_received.emit(text, source_text, target_lang, is_final)

                    elif msg_type == "status":
                        msg = data.get("message", "")
                        self.status_received.emit("status", msg)

                    elif msg_type == "error":
                        err_msg = data.get("message", "Unknown error")
                        self.error_received.emit(err_msg)

            except Exception as e:
                logger.error(f"Error parsing backend message: {e}")
