#!/usr/bin/env python3
"""
scripts/analyze_v3_results.py
Generates:
1. reports/v3_source_contribution.csv (Dataset Coverage Analysis)
2. reports/v1_v2_v3_model_comparison.csv (Model Comparison across V1, V2, and V3)
"""

import os
import sys
import json
import csv
from pathlib import Path

BASE_DIR = Path("/Volumes/Toshiba 1TB/PartVision")
REPORTS_DIR = BASE_DIR / "reports"

def generate_source_contribution():
    print("[*] Generating reports/v3_source_contribution.csv...")
    v3_dist_csv = REPORTS_DIR / "v3_class_distribution.csv"
    if not v3_dist_csv.exists():
        print(f"Error: {v3_dist_csv} not found.")
        return

    rows = []
    total_v2 = 0
    total_hitl = 0
    total_all = 0

    with open(v3_dist_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cid = int(r["class_id"])
            cname = r["class_name"]
            v2_cnt = int(r["carparts_v2_count"])
            hitl_cnt = int(r["hitl_count"])
            tot = int(r["total_count"])

            total_v2 += v2_cnt
            total_hitl += hitl_cnt
            total_all += tot

            v2_pct = (v2_cnt / tot * 100.0) if tot > 0 else 0.0
            hitl_pct = (hitl_cnt / tot * 100.0) if tot > 0 else 0.0
            depends_hitl = "YES (100% HITL)" if v2_cnt == 0 else "NO"
            underrepresented = "SEVERELY UNDERREPRESENTED" if tot < 200 else ("MODERATE (<1000)" if tot < 1000 else "WELL REPRESENTED")

            notes = ""
            if v2_cnt == 0:
                notes = "Newly introduced class from HITL"
            elif hitl_cnt == 0:
                notes = "Retained solely from Carparts-V2"
            elif cname in ("trunk", "wheel", "mirror", "back_glass"):
                notes = f"Significantly bolstered by HITL (+{hitl_cnt} instances)"
            else:
                notes = "Joint coverage from both datasets"

            rows.append({
                "class_id": cid,
                "class_name": cname,
                "carparts_v2_count": v2_cnt,
                "hitl_count": hitl_cnt,
                "v3_total_count": tot,
                "v2_percentage": f"{v2_pct:.2f}%",
                "hitl_percentage": f"{hitl_pct:.2f}%",
                "depends_entirely_on_hitl": depends_hitl,
                "representation_status": underrepresented,
                "notes": notes
            })

    out_csv = REPORTS_DIR / "v3_source_contribution.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "class_id", "class_name", "carparts_v2_count", "hitl_count",
            "v3_total_count", "v2_percentage", "hitl_percentage",
            "depends_entirely_on_hitl", "representation_status", "notes"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"[*] Saved {out_csv}")
    print(f"    Total Annotations: {total_all:,}")
    print(f"    Carparts-V2 Contribution: {total_v2:,} ({total_v2/total_all*100:.2f}%)")
    print(f"    HITL Contribution:        {total_hitl:,} ({total_hitl/total_all*100:.2f}%)")

def generate_model_comparison():
    print("\n[*] Generating reports/v1_v2_v3_model_comparison.csv...")
    v3_json_path = REPORTS_DIR / "v3_baseline_metrics.json"
    if not v3_json_path.exists():
        print(f"Warning: {v3_json_path} does not exist yet. Please run training first.")
        return

    with open(v3_json_path, "r", encoding="utf-8") as f:
        v3_data = json.load(f)

    # V1 & V2 metrics
    v1_metrics = {
        "dataset": "Carparts-Seg (V1)",
        "classes": 23,
        "images": 3833,
        "annotations": 20362,
        "epochs": 3,
        "imgsz": 640,
        "batch_size": 16,
        "training_duration": "30m 20.5s (1,820.47s)",
        "parameters": 2839053,
        "model_file_size": "5.73 MB",
        "det_p": 0.653580,
        "det_r": 0.487569,
        "det_map50": 0.480307,
        "det_map50_95": 0.372119,
        "seg_p": 0.666332,
        "seg_r": 0.493758,
        "seg_map50": 0.493539,
        "seg_map50_95": 0.358084,
    }

    v2_metrics = {
        "dataset": "Carparts-V2",
        "classes": 13,
        "images": 3833,
        "annotations": 20362,
        "epochs": 10,
        "imgsz": 512,
        "batch_size": 8,
        "training_duration": "155m 20.2s (9,320.18s)",
        "parameters": 2836373,
        "model_file_size": "5.71 MB",
        "det_p": 0.761013,
        "det_r": 0.831860,
        "det_map50": 0.810123,
        "det_map50_95": 0.662986,
        "seg_p": 0.767269,
        "seg_r": 0.830701,
        "seg_map50": 0.818042,
        "seg_map50_95": 0.641409,
    }

    v3_det = v3_data.get("detection_box", {})
    v3_seg = v3_data.get("segmentation_mask", {})

    v3_metrics = {
        "dataset": "PartVision-V3",
        "classes": 19,
        "images": 4831,
        "annotations": 35759,
        "epochs": v3_data.get("epochs", 15),
        "imgsz": v3_data.get("imgsz", 512),
        "batch_size": v3_data.get("batch_size", 8),
        "training_duration": f"{v3_data.get('training_duration_formatted', '')} ({v3_data.get('training_duration_seconds', 0):.2f}s)",
        "parameters": v3_data.get("parameters", 2838568),
        "model_file_size": f"{v3_data.get('model_file_size_bytes', 0) / (1024*1024):.2f} MB",
        "det_p": v3_det.get("precision", 0.0),
        "det_r": v3_det.get("recall", 0.0),
        "det_map50": v3_det.get("map50", 0.0),
        "det_map50_95": v3_det.get("map50_95", 0.0),
        "seg_p": v3_seg.get("precision", 0.0),
        "seg_r": v3_seg.get("recall", 0.0),
        "seg_map50": v3_seg.get("map50", 0.0),
        "seg_map50_95": v3_seg.get("map50_95", 0.0),
    }

    comparison_fields = [
        ("Dataset", v1_metrics["dataset"], v2_metrics["dataset"], v3_metrics["dataset"], "Dataset version and source"),
        ("Classes", v1_metrics["classes"], v2_metrics["classes"], v3_metrics["classes"], "Taxonomy size (23 vs 13 vs 19 classes)"),
        ("Images", v1_metrics["images"], v2_metrics["images"], v3_metrics["images"], "Total dataset image count"),
        ("Annotations", v1_metrics["annotations"], v2_metrics["annotations"], v3_metrics["annotations"], "Total ground-truth polygon instances"),
        ("Epochs", v1_metrics["epochs"], v2_metrics["epochs"], v3_metrics["epochs"], "CONFOUNDING: V1=3, V2=10, V3=15 epochs"),
        ("Image Size", v1_metrics["imgsz"], v2_metrics["imgsz"], v3_metrics["imgsz"], "CONFOUNDING: V1=640, V2/V3=512"),
        ("Batch Size", v1_metrics["batch_size"], v2_metrics["batch_size"], v3_metrics["batch_size"], "CONFOUNDING: V1=16, V2/V3=8"),
        ("Training Duration", v1_metrics["training_duration"], v2_metrics["training_duration"], v3_metrics["training_duration"], "Elapsed training wall-clock time"),
        ("Parameters", f"{v1_metrics['parameters']:,}", f"{v2_metrics['parameters']:,}", f"{v3_metrics['parameters']:,}", "Model parameter count"),
        ("Model Size", v1_metrics["model_file_size"], v2_metrics["model_file_size"], v3_metrics["model_file_size"], "Best checkpoint file size on disk"),
        ("Detection Precision", f"{v1_metrics['det_p']:.4f}", f"{v2_metrics['det_p']:.4f}", f"{v3_metrics['det_p']:.4f}", "Detection box precision"),
        ("Detection Recall", f"{v1_metrics['det_r']:.4f}", f"{v2_metrics['det_r']:.4f}", f"{v3_metrics['det_r']:.4f}", "Detection box recall"),
        ("Detection mAP50", f"{v1_metrics['det_map50']:.4f}", f"{v2_metrics['det_map50']:.4f}", f"{v3_metrics['det_map50']:.4f}", "Detection box mAP @ 0.50 IoU"),
        ("Detection mAP50-95", f"{v1_metrics['det_map50_95']:.4f}", f"{v2_metrics['det_map50_95']:.4f}", f"{v3_metrics['det_map50_95']:.4f}", "Detection box mAP @ 0.50:0.95 IoU"),
        ("Segmentation Precision", f"{v1_metrics['seg_p']:.4f}", f"{v2_metrics['seg_p']:.4f}", f"{v3_metrics['seg_p']:.4f}", "Segmentation mask precision"),
        ("Segmentation Recall", f"{v1_metrics['seg_r']:.4f}", f"{v2_metrics['seg_r']:.4f}", f"{v3_metrics['seg_r']:.4f}", "Segmentation mask recall"),
        ("Segmentation mAP50", f"{v1_metrics['seg_map50']:.4f}", f"{v2_metrics['seg_map50']:.4f}", f"{v3_metrics['seg_map50']:.4f}", "Segmentation mask mAP @ 0.50 IoU"),
        ("Segmentation mAP50-95", f"{v1_metrics['seg_map50_95']:.4f}", f"{v2_metrics['seg_map50_95']:.4f}", f"{v3_metrics['seg_map50_95']:.4f}", "Segmentation mask mAP @ 0.50:0.95 IoU"),
    ]

    out_csv = REPORTS_DIR / "v1_v2_v3_model_comparison.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric_field", "v1_baseline", "v2_consolidated", "v3_unified", "experimental_notes_and_confounders"])
        for row in comparison_fields:
            writer.writerow(row)

    print(f"[*] Saved {out_csv}")

if __name__ == "__main__":
    generate_source_contribution()
    generate_model_comparison()
