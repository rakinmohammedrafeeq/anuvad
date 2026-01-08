"""FastAPI application entry point for Anuvad."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import config, SUPPORTED_LANGUAGES
from .speech.model import get_model_manager
from .websocket.handler import handle_websocket_client

# Configure root logger
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("anuvad.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager: preloads Whisper model on startup."""
    logger.info("Initializing Anuvad backend...")
    logger.info(
        f"Configuration: Model={config.whisper_model}, Device={config.device}, "
        f"Compute={config.compute_type}, Translation={'ON' if config.enable_translation else 'OFF'}"
    )
    
    # Pre-load Whisper model once so first client connection is instant
    try:
        model_mgr = get_model_manager()
        model_mgr.load_model()
        logger.info("Anuvad speech engine is ready.")
    except Exception as e:
        logger.error(f"Failed to pre-load Whisper model: {e}", exc_info=True)

    yield

    logger.info("Shutting down Anuvad backend...")


app = FastAPI(
    title="Anuvad",
    description="Real-Time Multilingual Speech Captioning and Translation System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware to allow connections from local web app and Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health status and configuration info."""
    model_mgr = get_model_manager()
    return {
        "status": "ok",
        "model": config.whisper_model,
        "device": config.device,
        "compute_type": config.compute_type,
        "model_loaded": model_mgr.is_loaded,
        "vad_enabled": config.enable_vad,
        "translation_enabled": config.enable_translation,
    }


@app.get("/api/languages")
async def get_languages():
    """Supported languages for transcription and translation."""
    return {
        "languages": SUPPORTED_LANGUAGES,
        "default_source": config.default_source_language,
        "default_target": config.default_target_language,
    }


# WebSocket endpoints
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Primary WebSocket endpoint for real-time speech streaming."""
    await handle_websocket_client(websocket)


@app.websocket("/")
async def websocket_root_endpoint(websocket: WebSocket):
    """Root WebSocket fallback endpoint."""
    await handle_websocket_client(websocket)


# Mount Web Frontend if directory exists
static_dir = config.static_dir
if static_dir.exists():
    # Mount css, js, and assets subdirectories if they exist
    css_dir = static_dir / "css"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")

    js_dir = static_dir / "js"
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        favicon_path = static_dir / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(str(favicon_path), media_type="image/x-icon")
        return FileResponse(status_code=404)

    @app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
    async def chrome_devtools_probe():
        """Handle Chrome DevTools workspace probe silently."""
        return {}

    @app.get("/")
    async def serve_index():
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Anuvad backend running. Frontend not found."}
