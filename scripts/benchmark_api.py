"""
scripts/benchmark_api.py
Performance benchmark script for PartVision AI FastAPI Backend (Milestone 7).
Executes at least 5 real analysis requests to benchmark startup time, model initialization,
model inference latency, and full API pipeline latency on Apple Silicon M3.
"""

import sys
import json
import time
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.app import app

TEST_IMAGE_PATH = PROJECT_ROOT / "data" / "processed" / "partvision-v3" / "images" / "test" / "hitl_Car_damages_1033.png"
OUTPUT_JSON = PROJECT_ROOT / "reports" / "api_performance.json"


def run_benchmark():
    print("=" * 70)
    print("PartVision AI — Milestone 7: API Performance Benchmark")
    print("Platform: Local M3 development-server benchmark")
    print("=" * 70)

    if not TEST_IMAGE_PATH.exists():
        print(f"[-] Error: Benchmark image not found at {TEST_IMAGE_PATH}")
        sys.exit(1)

    with open(TEST_IMAGE_PATH, "rb") as f:
        img_bytes = f.read()

    # 1. Measure Application Startup & Lifespan
    print("\n[*] Measuring Application Startup & Model Initialization...")
    t_start = time.perf_counter()
    with TestClient(app) as client:
        startup_duration_ms = (time.perf_counter() - t_start) * 1000.0
        model_init_ms = getattr(app.state, "model_load_duration_ms", 0.0)

        print(f"  • Full Application Startup: {startup_duration_ms:.2f} ms")
        print(f"  • Model Weights Load Time:  {model_init_ms:.2f} ms")

        # Warmup pass (initial MPS shader compilation)
        print("\n[*] Executing Warmup Request...")
        files = {"file": ("hitl_Car_damages_1033.png", img_bytes, "image/png")}
        warmup_resp = client.post("/api/analyze", files=files)
        assert warmup_resp.status_code == 200, f"Warmup failed: {warmup_resp.text}"
        warmup_data = warmup_resp.json()
        print(f"  Warmup Model Latency: {warmup_data['inference']['latency_ms']:.2f} ms")

        # 2. Run 5 Benchmarked Analysis Requests
        num_runs = 5
        print(f"\n[*] Executing {num_runs} consecutive real analysis requests...")
        model_latencies = []
        api_latencies = []

        for i in range(1, num_runs + 1):
            files = {"file": (f"test_run_{i}.png", img_bytes, "image/png")}
            t0 = time.perf_counter()
            resp = client.post("/api/analyze", files=files)
            wall_ms = (time.perf_counter() - t0) * 1000.0

            assert resp.status_code == 200
            data = resp.json()
            model_ms = data["inference"]["latency_ms"]

            model_latencies.append(model_ms)
            api_latencies.append(wall_ms)
            print(f"  Run {i}: Model = {model_ms:7.2f} ms | Full API = {wall_ms:7.2f} ms")

    # 3. Compute Summary Statistics
    benchmarks = {
        "benchmark_label": "Local M3 development-server benchmark",
        "system": {
            "device": warmup_data["inference"]["device"],
            "image": "hitl_Car_damages_1033.png",
            "resolution": f"{warmup_data['image']['width']}x{warmup_data['image']['height']}",
            "iterations": num_runs,
        },
        "startup": {
            "application_startup_ms": round(startup_duration_ms, 2),
            "model_initialization_ms": round(model_init_ms, 2),
        },
        "model_inference_latency_ms": {
            "min": round(min(model_latencies), 2),
            "avg": round(sum(model_latencies) / len(model_latencies), 2),
            "max": round(max(model_latencies), 2),
            "runs": [round(x, 2) for x in model_latencies],
        },
        "full_api_request_latency_ms": {
            "min": round(min(api_latencies), 2),
            "avg": round(sum(api_latencies) / len(api_latencies), 2),
            "max": round(max(api_latencies), 2),
            "runs": [round(x, 2) for x in api_latencies],
        },
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(benchmarks, f, indent=2)

    print("\n----------------------------------------------------------------------")
    print(f"BENCHMARK SUMMARY ({benchmarks['benchmark_label']})")
    print("----------------------------------------------------------------------")
    print(f"Model Inference Latency (ms):")
    print(f"  Min: {benchmarks['model_inference_latency_ms']['min']} ms")
    print(f"  Avg: {benchmarks['model_inference_latency_ms']['avg']} ms")
    print(f"  Max: {benchmarks['model_inference_latency_ms']['max']} ms")
    print(f"\nFull API Request Latency (ms):")
    print(f"  Min: {benchmarks['full_api_request_latency_ms']['min']} ms")
    print(f"  Avg: {benchmarks['full_api_request_latency_ms']['avg']} ms")
    print(f"  Max: {benchmarks['full_api_request_latency_ms']['max']} ms")
    print(f"\nSaved metrics to: {OUTPUT_JSON}")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
