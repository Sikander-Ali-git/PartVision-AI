"""
scripts/run_server.py
CLI entrypoint to launch the PartVision AI FastAPI server using Uvicorn.
"""

import sys
import argparse
from pathlib import Path
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description="Run the PartVision AI FastAPI server.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable automatic code reloading for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")

    args = parser.parse_args()

    print("=" * 70)
    print("PartVision AI — Production FastAPI Server")
    print(f"Listening on: http://{args.host}:{args.port}")
    print(f"Swagger Documentation: http://{args.host}:{args.port}/docs")
    print(f"ReDoc Documentation:   http://{args.host}:{args.port}/redoc")
    print("=" * 70)

    uvicorn.run(
        "src.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info",
    )


if __name__ == "__main__":
    main()
