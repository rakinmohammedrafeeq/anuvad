"""Unit and integration tests for FastAPI routes and WebSocket protocol."""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app


def test_health_endpoint():
    """Verify GET /health returns operational status."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "model" in data
        assert "device" in data


def test_languages_endpoint():
    """Verify GET /api/languages returns supported languages map."""
    with TestClient(app) as client:
        response = client.get("/api/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "en" in data["languages"]
        assert "es" in data["languages"]


def test_root_serves_html():
    """Verify GET / serves the web frontend index.html."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "ANUVAD" in response.text


def test_favicon_and_assets():
    """Verify GET /favicon.ico and /assets/logo.png are served with 200 OK."""
    with TestClient(app) as client:
        fav_resp = client.get("/favicon.ico")
        assert fav_resp.status_code == 200
        assert "image" in fav_resp.headers.get("content-type", "")

        logo_resp = client.get("/assets/logo.png")
        assert logo_resp.status_code == 200
        assert "image/png" in logo_resp.headers.get("content-type", "")



def test_websocket_lifecycle_and_messages():
    """Verify WebSocket handshake, language switching, start, stop, and error handling."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            # Welcome message
            welcome = ws.receive_json()
            assert welcome["type"] == "status"
            assert "Connected to Anuvad" in welcome["message"]

            # Valid language update
            ws.send_json({"type": "setLanguages", "sourceLanguage": "fr", "targetLanguage": "de"})
            resp = ws.receive_json()
            assert resp["type"] == "languageChangeRestart"
            assert resp["sourceLanguage"] == "fr"
            assert resp["targetLanguage"] == "de"

            # Invalid source language
            ws.send_json({"type": "setLanguages", "sourceLanguage": "invalid_lang", "targetLanguage": "es"})
            err_resp = ws.receive_json()
            assert err_resp["type"] == "error"
            assert "Unsupported" in err_resp["message"]

            # Start recording session
            ws.send_json({"type": "start"})
            start_resp = ws.receive_json()
            assert start_resp["type"] == "status"
            assert "Started transcription" in start_resp["message"]

            # Stop recording session
            ws.send_json({"type": "stop"})
            stop_resp = ws.receive_json()
            assert stop_resp["type"] == "status"
            assert "Stopped transcription" in stop_resp["message"]

            # Malformed JSON
            ws.send_text("not a valid json")
            json_err = ws.receive_json()
            assert json_err["type"] == "error"
