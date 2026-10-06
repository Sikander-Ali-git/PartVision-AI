"""
scripts/benchmark_m9.py
Milestone 9: Full System Performance Benchmark & Local M3 Concurrency Smoke Test.
Measures warm latency breakdown (decode, inference, DB lookup, serialization, full API)
and concurrent request scaling across 1, 2, 4, and 8 concurrent requests.
"""

import sys
import time
import json
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np
from fastapi.testclient import TestClient

from src.api.app import app
from src.database.connection import DEFAULT_DB_PATH
from src.database.repository import PartVisionRepository
from src.inference.engine import PartVisionInferenceEngine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_IMAGE = PROJECT_ROOT / "data" / "processed" / "partvision-v3" / "images" / "test" / "hitl_Car_damages_1033.png"
OUTPUT_REPORT = PROJECT_ROOT / "reports" / "m9_performance.json"


def percentile(data, p):
    """Calculates percentile from sorted data."""
    if not data:
        return 0.0
    k = (len(data) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(data) - 1)
    d = k - f
    return data[f] + (data[c] - data[f]) * d


def run_benchmark():
    assert TEST_IMAGE.exists(), f"Missing test image: {TEST_IMAGE}"
    with open(TEST_IMAGE, "rb") as f:
        img_bytes = f.read()

    print("======================================================================")
    print("PartVision AI — Milestone 9: Performance & Concurrency Audit")
    print("Device: Apple Silicon M3 (MPS) · Model: Frozen YOLO11n-seg (V3)")
    print(f"Target Image: {TEST_IMAGE.name} ({len(img_bytes) / 1024:.1f} KB)")
    print("======================================================================")

    repo = PartVisionRepository(db_path=DEFAULT_DB_PATH)
    engine = PartVisionInferenceEngine(
        model_path=PROJECT_ROOT / "models" / "partvision_v3_yolo11n_seg_best.pt",
        device="auto",
        verbose=False,
    )

    # 1. Warm-up (2 passes)
    print("\nWarming up model and cache (2 iterations)...")
    for _ in range(2):
        _ = engine.predict(TEST_IMAGE, conf=0.25, imgsz=512)

    # 2. Decomposed Latency Benchmark (20 warm iterations)
    NUM_WARM_RUNS = 20
    print(f"\nRunning decomposed latency benchmark ({NUM_WARM_RUNS} iterations)...")

    decode_times = []
    inference_times = []
    db_times = []
    serialization_times = []
    full_api_times = []

    with TestClient(app) as client:
        # Client warm up
        client.post("/api/analyze", files={"file": (TEST_IMAGE.name, img_bytes, "image/png")})

        for i in range(NUM_WARM_RUNS):
            # A. Full API Request
            t_api_start = time.perf_counter()
            resp = client.post(
                "/api/analyze",
                files={"file": (TEST_IMAGE.name, img_bytes, "image/png")},
            )
            t_api_end = time.perf_counter()
            assert resp.status_code == 200
            full_api_times.append((t_api_end - t_api_start) * 1000.0)

            # B. Component: Image Decode
            t_dec_start = time.perf_counter()
            img_np = np.frombuffer(img_bytes, np.uint8)
            decoded = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            t_dec_end = time.perf_counter()
            decode_times.append((t_dec_end - t_dec_start) * 1000.0)

            # C. Component: Model Inference
            t_inf_start = time.perf_counter()
            inf_res = engine.predict(TEST_IMAGE, conf=0.25, imgsz=512)
            t_inf_end = time.perf_counter()
            inference_times.append((t_inf_end - t_inf_start) * 1000.0)

            # D. Component: Database Lookup for all detections
            t_db_start = time.perf_counter()
            for det in inf_res.detections:
                _ = repo.get_compatible_vehicles(det.class_name)
            t_db_end = time.perf_counter()
            db_times.append((t_db_end - t_db_start) * 1000.0)

            # E. Component: Serialization
            t_ser_start = time.perf_counter()
            _ = resp.json()
            t_ser_end = time.perf_counter()
            serialization_times.append((t_ser_end - t_ser_start) * 1000.0)

            if (i + 1) % 5 == 0:
                print(f"  Completed {i + 1}/{NUM_WARM_RUNS} runs...")

        def summarize(latencies):
            s = sorted(latencies)
            return {
                "min_ms": round(min(s), 2),
                "mean_ms": round(statistics.mean(s), 2),
                "median_ms": round(statistics.median(s), 2),
                "p50_ms": round(percentile(s, 50), 2),
                "p95_ms": round(percentile(s, 95), 2),
                "p99_ms": round(percentile(s, 99), 2),
                "max_ms": round(max(s), 2),
            }

        breakdown = {
            "image_decode": summarize(decode_times),
            "model_inference": summarize(inference_times),
            "database_lookup": summarize(db_times),
            "serialization": summarize(serialization_times),
            "full_api_request": summarize(full_api_times),
        }

        print("\n--- Decomposed Warm Latency Summary (ms) ---")
        for stage, metrics in breakdown.items():
            print(f"  {stage.replace('_', ' ').title():<20}: Mean={metrics['mean_ms']}ms, P50={metrics['p50_ms']}ms, P95={metrics['p95_ms']}ms")

        # 3. Concurrency Smoke Test (1, 2, 4, 8 concurrent requests)
        print("\n--- Local M3 Concurrency Smoke Test ---")
        concurrency_levels = [1, 2, 4, 8]
        concurrency_results = {}

        for c in concurrency_levels:
            num_reqs = max(8, c * 2)
            latencies = []
            failures = 0

            def send_req(_):
                nonlocal failures
                t0 = time.perf_counter()
                try:
                    r = client.post(
                        "/api/analyze",
                        files={"file": (TEST_IMAGE.name, img_bytes, "image/png")},
                    )
                    t_dur = (time.perf_counter() - t0) * 1000.0
                    if r.status_code == 200:
                        return t_dur
                    else:
                        failures += 1
                        return None
                except Exception:
                    failures += 1
                    return None

            with ThreadPoolExecutor(max_workers=c) as executor:
                results = list(executor.map(send_req, range(num_reqs)))

            valid_latencies = sorted([r for r in results if r is not None])
            successful = len(valid_latencies)

            res_entry = {
                "concurrency": c,
                "total_requests": num_reqs,
                "successful_requests": successful,
                "failures": failures,
                "avg_latency_ms": round(statistics.mean(valid_latencies), 2) if valid_latencies else 0.0,
                "p50_ms": round(percentile(valid_latencies, 50), 2) if valid_latencies else 0.0,
                "p95_ms": round(percentile(valid_latencies, 95), 2) if valid_latencies else 0.0,
                "max_latency_ms": round(max(valid_latencies), 2) if valid_latencies else 0.0,
            }
            concurrency_results[f"concurrency_{c}"] = res_entry
            print(
                f"  Concurrency {c}: {successful}/{num_reqs} success, "
                f"Avg={res_entry['avg_latency_ms']}ms, P95={res_entry['p95_ms']}ms, Max={res_entry['max_latency_ms']}ms"
            )

    # 4. Save Final Report
    report_data = {
        "benchmark_label": "Local M3 development benchmark",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hardware": {
            "device": engine.device,
            "architecture": "Apple Silicon M3",
            "os": "macOS",
        },
        "test_image": {
            "name": TEST_IMAGE.name,
            "size_bytes": len(img_bytes),
        },
        "decomposed_latency": breakdown,
        "concurrency_smoke_test": concurrency_results,
    }

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REPORT, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\nBenchmark report successfully saved to: {OUTPUT_REPORT}")
    print("======================================================================")


if __name__ == "__main__":
    run_benchmark()
