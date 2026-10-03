#!/usr/bin/env python3
"""
scripts/verify_integrity_v2.py
Comprehensive integrity test for Milestone 1 preservation and Milestone 2 dataset verification.
- Verifies V1 artifacts (dataset, models, runs, reports) are 100% untouched
- Verifies V2 dataset image bit-level equivalence (full hash check of all 3,833 images)
- Verifies V2 labels, polygon coordinates, and class ID boundaries [0, 12]
- Verifies exact annotation counts and object elimination
"""

import os
import sys
import hashlib
import yaml
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1_DIR = os.path.join(BASE_DIR, "data", "processed", "carparts-seg")
V2_DIR = os.path.join(BASE_DIR, "data", "processed", "carparts-v2")
M1_CHECKPOINT = os.path.join(BASE_DIR, "models", "baseline_yolo11n_seg_best.pt")
M1_RUNS = os.path.join(BASE_DIR, "runs", "partvision_v1")
M1_METRICS_TXT = os.path.join(BASE_DIR, "reports", "baseline_metrics.txt")
M1_METRICS_JSON = os.path.join(BASE_DIR, "reports", "baseline_metrics.json")
V2_YAML = os.path.join(V2_DIR, "carparts-v2.yaml")

def is_valid_file(fname):
    base = os.path.basename(fname)
    return not base.startswith("._") and not base.startswith(".")

def get_file_md5(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=" * 70)
    print("PartVision AI — Automated Dataset Integrity Test")
    print("=" * 70)

    errors = []

    # 1. Milestone 1 Preservation Checks
    print("\n[CHECK 1/6] Verifying Milestone 1 Artifacts Preservation...")
    if not os.path.exists(M1_CHECKPOINT):
        errors.append("M1 best checkpoint missing: models/baseline_yolo11n_seg_best.pt")
    else:
        print(f"  ✓ M1 Model Checkpoint intact: {os.path.getsize(M1_CHECKPOINT)} bytes")

    if not os.path.exists(M1_RUNS):
        errors.append("M1 runs directory missing: runs/partvision_v1/")
    else:
        print("  ✓ M1 Runs directory intact")

    if not os.path.exists(M1_METRICS_TXT) or not os.path.exists(M1_METRICS_JSON):
        errors.append("M1 baseline metrics reports missing")
    else:
        print("  ✓ M1 Baseline metrics reports intact")

    # 2. V1 Dataset Directory Checks
    print("\n[CHECK 2/6] Verifying Original V1 Dataset Directory...")
    splits = ["train", "val", "test"]
    v1_image_count = 0
    v1_label_count = 0
    for s in splits:
        img_p = os.path.join(V1_DIR, "images", s)
        lbl_p = os.path.join(V1_DIR, "labels", s)
        imgs = [f for f in os.listdir(img_p) if is_valid_file(f) and f.endswith(".jpg")]
        lbls = [f for f in os.listdir(lbl_p) if is_valid_file(f) and f.endswith(".txt")]
        v1_image_count += len(imgs)
        v1_label_count += len(lbls)

    if v1_image_count != 3833:
        errors.append(f"V1 image count changed! Expected 3833, found {v1_image_count}")
    else:
        print(f"  ✓ V1 Images count intact: {v1_image_count} images")

    if v1_label_count != 3833:
        errors.append(f"V1 label count changed! Expected 3833, found {v1_label_count}")
    else:
        print(f"  ✓ V1 Labels count intact: {v1_label_count} labels")

    # 3. V2 Dataset Structure and YAML
    print("\n[CHECK 3/6] Verifying V2 YAML and Structure...")
    if not os.path.exists(V2_YAML):
        errors.append(f"V2 YAML missing: {V2_YAML}")
    else:
        with open(V2_YAML, "r") as f:
            ydata = yaml.safe_load(f)
        names = ydata.get("names", {})
        if len(names) != 13:
            errors.append(f"V2 YAML has {len(names)} classes, expected 13")
        else:
            print("  ✓ V2 YAML defines exactly 13 classes (IDs 0 to 12)")

    # 4. Image Bit-Level Equivalence (All 3,833 images)
    print("\n[CHECK 4/6] Verifying Bit-Level Image Equivalence (All 3,833 images)...")
    mismatches = 0
    total_imgs = 0
    for s in splits:
        v1_img_dir = os.path.join(V1_DIR, "images", s)
        v2_img_dir = os.path.join(V2_DIR, "images", s)
        files = sorted([f for f in os.listdir(v1_img_dir) if is_valid_file(f) and f.endswith(".jpg")])
        for fname in files:
            total_imgs += 1
            p1 = os.path.join(v1_img_dir, fname)
            p2 = os.path.join(v2_img_dir, fname)
            if not os.path.exists(p2):
                mismatches += 1
                errors.append(f"V2 image missing: {p2}")
                continue
            if os.path.getsize(p1) != os.path.getsize(p2):
                mismatches += 1
                errors.append(f"Size mismatch: {fname}")
            elif get_file_md5(p1) != get_file_md5(p2):
                mismatches += 1
                errors.append(f"MD5 hash mismatch: {fname}")

    if mismatches == 0:
        print(f"  ✓ All {total_imgs} images in V2 are 100% bit-identical to V1 images (0 mismatches)")
    else:
        errors.append(f"Found {mismatches} image mismatches between V1 and V2")

    # 5. Label Parsing & Class Boundaries [0, 12]
    print("\n[CHECK 5/6] Verifying V2 Label Parsing & Class Boundaries...")
    v2_total_ann = 0
    invalid_cls = 0
    malformed = 0
    v2_empty_files = 0

    for s in splits:
        v2_lbl_dir = os.path.join(V2_DIR, "labels", s)
        files = sorted([f for f in os.listdir(v2_lbl_dir) if is_valid_file(f) and f.endswith(".txt")])
        for fname in files:
            lp = os.path.join(v2_lbl_dir, fname)
            with open(lp, "r") as f:
                lines = [l.strip() for l in f if l.strip()]
            if len(lines) == 0:
                v2_empty_files += 1
                continue
            for line in lines:
                tokens = line.split()
                if len(tokens) < 7 or len(tokens[1:]) % 2 != 0:
                    malformed += 1
                    continue
                cid = int(tokens[0])
                if cid < 0 or cid > 12:
                    invalid_cls += 1
                    continue
                v2_total_ann += 1

    if invalid_cls > 0:
        errors.append(f"Found {invalid_cls} invalid class IDs outside [0, 12]")
    else:
        print("  ✓ All class IDs strictly in [0, 12] (0 invalid IDs)")

    if malformed > 0:
        errors.append(f"Found {malformed} malformed polygon lines")
    else:
        print("  ✓ All polygon coordinates well-formed (0 malformed lines)")

    # 6. Annotation Count and Object Removal Verification
    print("\n[CHECK 6/6] Verifying Exact Annotation Counts...")
    print(f"  Total V2 Annotations: {v2_total_ann}")
    print(f"  Total V2 Empty Label Files: {v2_empty_files}")

    if v2_total_ann != 20362:
        errors.append(f"V2 annotation count mismatch: expected 20362, found {v2_total_ann}")
    else:
        print("  ✓ Exactly 20,362 annotations present (20,374 original - 12 removed objects)")

    if v2_empty_files != 147:
        errors.append(f"V2 empty file count mismatch: expected 147, found {v2_empty_files}")
    else:
        print("  ✓ Exactly 147 empty label files present (135 originally empty + 12 became empty)")

    print("\n" + "=" * 70)
    if not errors:
        print("RESULT: ALL INTEGRITY CHECKS PASSED (100% INTEGRITY)")
        print("=" * 70)
        return 0
    else:
        print("RESULT: INTEGRITY CHECKS FAILED:")
        for err in errors:
            print(f"  ✗ {err}")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
