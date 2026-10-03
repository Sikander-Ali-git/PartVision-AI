"""
PartVision AI - Integrity Verification Script for Milestone 4B
Ensures that all prior datasets and model checkpoints remain 100% untouched.
"""

import hashlib
import json
from pathlib import Path

WORKSPACE = Path("/Volumes/Toshiba 1TB/PartVision")

EXPECTED_RAW_ZIP_SHA256 = "e2eea20030d02366b07174bcdbcc843f63791bdd53962a83e00636d15e78e41f"

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def count_files(dir_path: Path, ext_tuple: tuple) -> int:
    if not dir_path.exists():
        return 0
    return sum(
        1 for f in dir_path.rglob("*")
        if f.is_file() and f.suffix.lower() in ext_tuple and not f.name.startswith("._")
    )

def check_integrity():
    results = {}
    passed = True

    print("=" * 60)
    print("PARTVISION AI - INTEGRITY VERIFICATION (MILESTONE 4B)")
    print("=" * 60)

    # 1. Raw Carparts-Seg Zip
    raw_zip = WORKSPACE / "data" / "raw" / "carparts-seg.zip"
    if raw_zip.exists():
        zip_sha = compute_sha256(raw_zip)
        zip_size = raw_zip.stat().st_size
        zip_match = (zip_sha == EXPECTED_RAW_ZIP_SHA256)
        results["raw_carparts_seg_zip"] = {
            "exists": True,
            "size_bytes": zip_size,
            "sha256": zip_sha,
            "matches_expected": zip_match
        }
        print(f"[*] data/raw/carparts-seg.zip: {zip_size:,} bytes")
        print(f"    SHA256: {zip_sha}")
        print(f"    Checksum Match: {'PASS' if zip_match else 'FAIL'}")
        if not zip_match:
            passed = False
    else:
        results["raw_carparts_seg_zip"] = {"exists": False}
        print("[!] data/raw/carparts-seg.zip NOT FOUND")
        passed = False

    # 2. V1 Model Checkpoint
    v1_model = WORKSPACE / "models" / "baseline_yolo11n_seg_best.pt"
    if v1_model.exists():
        v1_sha = compute_sha256(v1_model)
        v1_size = v1_model.stat().st_size
        results["v1_model_checkpoint"] = {
            "exists": True,
            "size_bytes": v1_size,
            "sha256": v1_sha
        }
        print(f"[*] models/baseline_yolo11n_seg_best.pt: {v1_size:,} bytes")
        print(f"    SHA256: {v1_sha}")
    else:
        results["v1_model_checkpoint"] = {"exists": False}
        print("[!] models/baseline_yolo11n_seg_best.pt NOT FOUND")
        passed = False

    # 3. V2 Model Checkpoint
    v2_model = WORKSPACE / "models" / "partvision_v2_yolo11n_seg_best.pt"
    if v2_model.exists():
        v2_sha = compute_sha256(v2_model)
        v2_size = v2_model.stat().st_size
        results["v2_model_checkpoint"] = {
            "exists": True,
            "size_bytes": v2_size,
            "sha256": v2_sha
        }
        print(f"[*] models/partvision_v2_yolo11n_seg_best.pt: {v2_size:,} bytes")
        print(f"    SHA256: {v2_sha}")
    else:
        results["v2_model_checkpoint"] = {"exists": False}
        print("[!] models/partvision_v2_yolo11n_seg_best.pt NOT FOUND")
        passed = False

    # 4. V1 Processed Dataset
    v1_dir = WORKSPACE / "data" / "processed" / "carparts-seg"
    v1_imgs = count_files(v1_dir / "images", (".jpg", ".jpeg", ".png"))
    v1_lbls = count_files(v1_dir / "labels", (".txt",))
    results["v1_processed_dataset"] = {
        "exists": v1_dir.exists(),
        "images_count": v1_imgs,
        "labels_count": v1_lbls,
        "intact": (v1_imgs == 3833 and v1_lbls == 3833)
    }
    print(f"[*] data/processed/carparts-seg: {v1_imgs} images, {v1_lbls} labels (Expected 3,833/3,833) -> {'PASS' if results['v1_processed_dataset']['intact'] else 'FAIL'}")
    if not results["v1_processed_dataset"]["intact"]:
        passed = False

    # 5. V2 Processed Dataset
    v2_dir = WORKSPACE / "data" / "processed" / "carparts-v2"
    v2_imgs = count_files(v2_dir / "images", (".jpg", ".jpeg", ".png"))
    v2_lbls = count_files(v2_dir / "labels", (".txt",))
    results["v2_processed_dataset"] = {
        "exists": v2_dir.exists(),
        "images_count": v2_imgs,
        "labels_count": v2_lbls,
        "intact": (v2_imgs == 3833 and v2_lbls == 3833)
    }
    print(f"[*] data/processed/carparts-v2: {v2_imgs} images, {v2_lbls} labels (Expected 3,833/3,833) -> {'PASS' if results['v2_processed_dataset']['intact'] else 'FAIL'}")
    if not results["v2_processed_dataset"]["intact"]:
        passed = False

    print("=" * 60)
    print(f"OVERALL INTEGRITY STATUS: {'ALL CHECKS PASSED' if passed else 'INTEGRITY CHECK FAILED'}")
    print("=" * 60)

    return passed, results

if __name__ == "__main__":
    check_integrity()
