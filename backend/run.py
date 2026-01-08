"""CLI launcher for Anuvad backend server."""
import argparse
import os
import sys
from pathlib import Path

# Add backend directory to sys.path to ensure modules resolve cleanly
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Anuvad Real-Time Multilingual Speech Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"), help="Server bind host")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")), help="Server port")
    parser.add_argument(
        "--model",
        default=os.getenv("WHISPER_MODEL", "tiny"),
        choices=["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large-v1", "large-v2", "large-v3", "large-v3-turbo"],
        help="Whisper model size",
    )
    parser.add_argument("--device", default=os.getenv("DEVICE", "auto"), choices=["auto", "cpu", "cuda"], help="Inference device")
    parser.add_argument("--compute-type", default=os.getenv("COMPUTE_TYPE", "auto"), help="Compute quantization type (e.g. int8, float16)")
    parser.add_argument("--no-translate", action="store_true", help="Disable translation feature")
    parser.add_argument("--no-vad", action="store_true", help="Disable Voice Activity Detection")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn auto-reload")
    return parser.parse_args()


def main():
    args = parse_args()

    # Pass command line arguments to environment so config.py picks them up
    os.environ["HOST"] = args.host
    os.environ["PORT"] = str(args.port)
    os.environ["WHISPER_MODEL"] = args.model
    os.environ["DEVICE"] = args.device
    os.environ["COMPUTE_TYPE"] = args.compute_type
    if args.no_translate:
        os.environ["ENABLE_TRANSLATION"] = "false"
    if args.no_vad:
        os.environ["ENABLE_VAD"] = "false"

    # Ensure stdout and stderr handle unicode safely on Windows
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("=" * 60)
    print("[*] Starting ANUVAD Speech Captioning & Translation Server")
    print("=" * 60)
    print(f"  - Address:            http://{args.host}:{args.port}")
    print(f"  - WebSocket Endpoint: ws://{args.host}:{args.port}/ws")
    print(f"  - Whisper Model:      {args.model}")
    print(f"  - Target Device:      {args.device}")
    print(f"  - Translation:        {'Disabled' if args.no_translate else 'Enabled'}")
    print(f"  - Voice Activity Det: {'Disabled' if args.no_vad else 'Enabled'}")
    print("=" * 60)
    print(f"  --> Open your browser at: http://{args.host}:{args.port}")
    print("=" * 60)

    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
