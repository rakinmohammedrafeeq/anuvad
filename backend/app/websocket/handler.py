"""WebSocket client connection handler with decoupled streaming pipeline."""
from __future__ import annotations

import json
import logging
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

from ..config import config, SUPPORTED_LANGUAGES
from ..audio.processor import pcm16_to_float32
from ..speech.model import get_model_manager
from ..speech.streaming import StreamingASRProcessor
from ..translation.translator import get_translator

logger = logging.getLogger("anuvad.websocket")


async def handle_websocket_client(websocket: WebSocket) -> None:
    """Handle a WebSocket client connection for low-latency speech streaming."""
    await websocket.accept()
    client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
    logger.info(f"Client connected: {client_info}")

    model_manager = get_model_manager()
    translator = get_translator()

    processor = StreamingASRProcessor(
        model_manager=model_manager,
        source_language=config.default_source_language,
        target_language=config.default_target_language,
        sampling_rate=config.sampling_rate,
        min_chunk_seconds=config.min_chunk_size,
        enable_vad=config.enable_vad,
    )

    # Send welcome status
    await websocket.send_json({
        "type": "status",
        "message": (
            f"Connected to Anuvad server (Model: {config.whisper_model}, "
            f"Translation: {'Enabled' if config.enable_translation else 'Disabled'})"
        ),
    })

    is_active = True
    is_recording = True
    is_processing = [False]  # Mutable flag for cooperative inference locking

    async def async_translate_and_send(
        text: str,
        src: str,
        dest: str,
        start_ms: int,
        end_ms: int,
        is_final: bool = True,
    ) -> None:
        """Asynchronously translate text in the background without blocking ASR."""
        if not is_active or not text:
            return
        try:
            loop = asyncio.get_running_loop()
            translation = await loop.run_in_executor(
                None,
                translator.translate,
                text,
                src,
                dest,
            )
            if translation and is_active:
                await websocket.send_json({
                    "type": "translation",
                    "text": translation,
                    "sourceText": text,
                    "start": start_ms,
                    "end": end_ms,
                    "isFinal": is_final,
                    "sourceLanguage": src,
                    "targetLanguage": dest,
                })
        except Exception as e:
            logger.debug(f"Background translation error: {e}")

    async def process_and_emit() -> None:
        """Trigger an inference iteration if worker is not busy."""
        if not is_active or is_processing[0]:
            return
        is_processing[0] = True
        try:
            loop = asyncio.get_running_loop()
            if is_recording and processor.has_enough_audio():
                result = await loop.run_in_executor(None, processor.process_iter)
                if result and is_active:
                    await websocket.send_json(result)

                    # Trigger instant translation as soon as text appears
                    if config.enable_translation and result.get("text"):
                        is_final = result.get("isFinal", False)
                        asyncio.create_task(
                            async_translate_and_send(
                                result["text"],
                                processor.source_language,
                                processor.target_language,
                                result.get("start", 0),
                                result.get("end", 0),
                                is_final=is_final,
                            )
                        )
        except Exception as e:
            logger.debug(f"Error during process_and_emit: {e}")
        finally:
            is_processing[0] = False

    async def streaming_worker() -> None:
        """Heartbeat worker that triggers inference whenever audio is ready."""
        while is_active:
            try:
                if is_recording and processor.has_enough_audio() and not is_processing[0]:
                    await process_and_emit()
                await asyncio.sleep(0.02)  # 20ms check interval
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Streaming worker error: {e}")
                await asyncio.sleep(0.05)

    worker_task = asyncio.create_task(streaming_worker())

    try:
        while True:
            message = await websocket.receive()

            # Check for disconnect
            if message.get("type") == "websocket.disconnect":
                break

            # Handle Binary Audio (PCM16) - Instant non-blocking ingestion
            if "bytes" in message and message["bytes"] is not None:
                audio_bytes = message["bytes"]
                if len(audio_bytes) > 0 and is_recording:
                    float_chunk = pcm16_to_float32(audio_bytes)
                    processor.insert_audio_chunk(float_chunk)

                    # Trigger inference without awaiting (non-blocking)
                    if processor.has_enough_audio() and not is_processing[0]:
                        asyncio.create_task(process_and_emit())

            # Handle Text JSON Messages
            elif "text" in message and message["text"] is not None:
                try:
                    data = json.loads(message["text"])
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format received",
                    })
                    continue

                msg_type = data.get("type")

                if msg_type == "start":
                    is_recording = True
                    processor.reset()
                    await websocket.send_json({
                        "type": "status",
                        "message": (
                            f"Started transcription (Source: {processor.source_language}, "
                            f"Target: {processor.target_language})"
                        ),
                    })

                elif msg_type == "stop":
                    is_recording = False
                    # Wait briefly for in-flight inference to settle
                    for _ in range(10):
                        if not is_processing[0]:
                            break
                        await asyncio.sleep(0.05)

                    loop = asyncio.get_running_loop()
                    final_result = await loop.run_in_executor(None, processor.finish)
                    if final_result:
                        await websocket.send_json(final_result)

                        if config.enable_translation and final_result.get("text"):
                            asyncio.create_task(
                                async_translate_and_send(
                                    final_result["text"],
                                    processor.source_language,
                                    processor.target_language,
                                    final_result.get("start", 0),
                                    final_result.get("end", 0),
                                )
                            )

                    await websocket.send_json({
                        "type": "status",
                        "message": "Stopped transcription",
                    })

                elif msg_type == "setLanguages":
                    src = data.get("sourceLanguage", config.default_source_language)
                    target = data.get("targetLanguage", config.default_target_language)

                    if src not in SUPPORTED_LANGUAGES and src != "auto":
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unsupported source language: '{src}'",
                        })
                        continue

                    change_type = processor.update_languages(src, target)

                    if change_type == "source_changed":
                        await websocket.send_json({
                            "type": "languageChangeRestart",
                            "message": f"Source language changed to {src}.",
                            "sourceLanguage": src,
                            "targetLanguage": target,
                        })
                    elif change_type == "target_changed":
                        await websocket.send_json({
                            "type": "targetLanguageChanged",
                            "message": f"Translation target changed to {target}.",
                            "targetLanguage": target,
                        })
                    else:
                        await websocket.send_json({
                            "type": "status",
                            "message": f"Languages configured: {src} -> {target}",
                        })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected normally: {client_info}")
    except Exception as e:
        logger.error(f"Error handling WebSocket client {client_info}: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        is_active = False
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
