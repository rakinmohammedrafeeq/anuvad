"""Application entry point for Anuvad Desktop Application."""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
import requests

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from desktop.ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("anuvad.desktop")


def is_backend_running(host: str = "127.0.0.1", port: int = 8000) -> bool:
    """Check if local Anuvad backend is currently active and healthy."""
    try:
        resp = requests.get(f"http://{host}:{port}/health", timeout=1.0)
        return resp.status_code == 200
    except Exception:
        return False


def start_background_backend(host: str = "127.0.0.1", port: int = 8000) -> Optional[subprocess.Popen]:
    """Auto-launch the local backend server process if not already running."""
    logger.info("Local Anuvad backend not detected. Auto-spawning backend server...")
    backend_script = root_dir / "run.py"
    if not backend_script.exists():
        logger.warning(f"Could not locate {backend_script}. User should start backend manually.")
        return None

    python_bin = sys.executable
    if getattr(sys, "frozen", False):
        import shutil
        python_bin = shutil.which("python") or shutil.which("python3") or "python"

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    log_path = root_dir / "backend.log"

    try:
        cmd = [python_bin, str(backend_script), "--host", host, "--port", str(port)]
        log_file = open(log_path, "a", encoding="utf-8")
        proc = subprocess.Popen(
            cmd,
            cwd=str(root_dir),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        # Wait up to 15 seconds for backend to become ready
        for _ in range(50):
            if is_backend_running(host, port):
                logger.info("Background backend server successfully initialized!")
                return proc
            if proc.poll() is not None:
                logger.error(f"Backend process terminated prematurely with code {proc.returncode}. See backend.log")
                return None
            time.sleep(0.3)

        logger.info("Backend spawned; proceeding with GUI launch while model finishes loading...")
        return proc
    except Exception as e:
        logger.warning(f"Failed to auto-spawn backend: {e}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Anuvad Desktop Speech Captioning Application")
    parser.add_argument("--host", default="127.0.0.1", help="Backend host")
    parser.add_argument("--port", type=int, default=8000, help="Backend port")
    parser.add_argument("--no-autospawn", action="store_true", help="Do not auto-start backend if offline")
    args = parser.parse_args()

    backend_proc = None
    if not is_backend_running(args.host, args.port) and not args.no_autospawn:
        backend_proc = start_background_backend(args.host, args.port)

    # Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Anuvad")
    app.setOrganizationName("Anuvad Speech Systems")

    # Set clean default font to prevent QFont::setPointSize warnings
    from PySide6.QtGui import QFont
    app_font = QFont("Segoe UI", 10)
    app.setFont(app_font)

    ws_url = f"ws://{args.host}:{args.port}/ws"
    window = MainWindow(backend_url=ws_url)
    window.show()

    exit_code = app.exec()

    # Clean up auto-spawned backend if we created one
    if backend_proc is not None:
        try:
            backend_proc.terminate()
        except Exception:
            pass

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
