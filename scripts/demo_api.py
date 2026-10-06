"""
scripts/demo_api.py
End-to-end demonstration of the PartVision AI FastAPI backend (Milestone 7).
Sends an automotive test image to POST /api/analyze, displays detected parts,
confidence scores, vehicle compatibility matches, and execution metadata.
"""

import sys
import json
import time
from pathlib import Path
import httpx
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.app import app

DEFAULT_DEMO_IMAGE = (
    PROJECT_ROOT / "data" / "processed" / "partvision-v3" / "images" / "test" / "hitl_Car_damages_1033.png"
)


def run_demo(image_path: Path = DEFAULT_DEMO_IMAGE, server_url: str = "http://127.0.0.1:8000"):
    print("=" * 70)
    print(" PartVision AI API — End-to-End Analysis Demonstration")
    print("=" * 70)

    if not image_path.exists():
        print(f"[-] Error: Demo image not found at {image_path}")
        return

    # Check if a live server is running, otherwise use in-process TestClient
    use_live_server = False
    try:
        r = httpx.get(f"{server_url}/health", timeout=1.0)
        if r.status_code == 200:
            use_live_server = True
            print(f"[*] Connected to active server at {server_url}")
    except Exception:
        pass

    if not use_live_server:
        print("[*] Running in-process demonstration via FastAPI TestClient...")

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    files = {"file": (image_path.name, img_bytes, "image/png")}

    start_wall_t = time.perf_counter()
    if use_live_server:
        response = httpx.post(f"{server_url}/api/analyze", files=files, timeout=30.0)
    else:
        with TestClient(app) as client:
            response = client.post("/api/analyze", files=files)
    total_wall_ms = (time.perf_counter() - start_wall_t) * 1000.0

    if response.status_code != 200:
        print(f"[-] API Error ({response.status_code}): {response.text}")
        return

    data = response.json()

    print("\n----------------------------------------------------------------------")
    print(f"Image: {image_path.name} ({data['image']['width']}x{data['image']['height']} px)")
    print(f"Request ID: {data['request_id']}")
    print(f"Compute Device: {data['inference']['device']}")
    print(f"Model Latency:  {data['inference']['latency_ms']:.2f} ms")
    print(f"Total API Time: {total_wall_ms:.2f} ms")
    print("----------------------------------------------------------------------")

    print(f"\nDetected {data['summary']['detection_count']} automotive parts:")
    for det in data["detections"]:
        pct = det["confidence"] * 100
        bbox = det["bbox"]
        print(f"  • {det['display_name']:<18} — {pct:5.1f}% conf | BBox: [{bbox['x1']:.0f}, {bbox['y1']:.0f}, {bbox['x2']:.0f}, {bbox['y2']:.0f}]")

    print("\n----------------------------------------------------------------------")
    print("Compatibility Lookup Highlights:")
    print("----------------------------------------------------------------------")
    # Show compatibility for detected parts
    seen_parts = set()
    for det in data["detections"]:
        part_name = det["part_name"]
        if part_name in seen_parts:
            continue
        seen_parts.add(part_name)

        compat = det["compatibility"]
        verified = compat["verified_vehicles"]
        unverified = compat["unverified_vehicles"]
        print(f"\n► Part: {det['display_name']} ({part_name})")
        print(f"  Verified OEM Matches:   {len(verified)}")
        print(f"  Unverified/Demo Matches: {len(unverified)}")

        if verified:
            print("  Example Verified Vehicles:")
            for v in verified[:3]:
                gen = f" ({v['generation']})" if v.get("generation") else ""
                ystart = v.get("year_start", "")
                yend = v.get("year_end") or "Present"
                print(f"    - {v['make']} {v['model']}{gen} [{ystart}–{yend}]: {v['compatibility_status']} (Source: {v['source']})")

    print("\n" + "=" * 70)
    print(" Demonstration Finished Successfully")
    print("=" * 70)


if __name__ == "__main__":
    img_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DEMO_IMAGE
    run_demo(img_arg)
