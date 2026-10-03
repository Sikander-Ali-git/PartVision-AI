#!/usr/bin/env python3
"""
scripts/download_dataset.py
Downloads the official Ultralytics Carparts-Seg dataset, calculates SHA256 checksum,
verifies archive integrity, and extracts it to data/processed/carparts-seg/.
"""

import os
import sys
import hashlib
import zipfile
import shutil
import json
import time
import requests

DATASET_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/carparts-seg.zip"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
RAW_ZIP = os.path.join(RAW_DIR, "carparts-seg.zip")
EXTRACT_DIR = os.path.join(BASE_DIR, "data", "processed", "carparts-seg")
META_FILE = os.path.join(BASE_DIR, "reports", "dataset_download_meta.json")

def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def get_disk_free(path):
    stat = shutil.disk_usage(path)
    return stat.free, format_size(stat.free)

def calculate_sha256(filepath):
    print(f"Calculating SHA256 checksum for {filepath}...")
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_file(url, target_path):
    print(f"Connecting to {url}...")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    start_time = time.time()
    headers = {"User-Agent": "PartVision-AI/1.0"}
    with requests.get(url, stream=True, headers=headers) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", -1))
        downloaded = 0
        chunk_size = 1024 * 256  # 256 KB
        
        last_log = 0
        with open(target_path, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    now = time.time()
                    if now - last_log > 2.0 or downloaded == total_size:
                        if total_size > 0:
                            pct = (downloaded / total_size) * 100
                            print(f"Progress: {format_size(downloaded)} / {format_size(total_size)} ({pct:.1f}%)")
                        else:
                            print(f"Downloaded: {format_size(downloaded)}")
                        last_log = now

    elapsed = time.time() - start_time
    print(f"Download complete in {elapsed:.1f}s.")

def extract_archive(zip_path, target_dir):
    print(f"Extracting {zip_path} into {target_dir}...")
    os.makedirs(target_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        total_files = len(zip_ref.infolist())
        print(f"Archive contains {total_files} entries.")
        zip_ref.extractall(target_dir)
    print("Extraction completed successfully.")

def main():
    print("=== PartVision AI: Dataset Download & Extraction ===")
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)
    
    free_bytes, free_str = get_disk_free(BASE_DIR)
    print(f"Disk space available: {free_str}")
    if free_bytes < 5 * 1024 * 1024 * 1024:
        print("WARNING: Less than 5 GB available on destination disk.")

    if os.path.exists(RAW_ZIP) and os.path.getsize(RAW_ZIP) > 1000:
        print(f"Raw archive already exists at: {RAW_ZIP}")
    else:
        if os.path.exists(RAW_ZIP):
            os.remove(RAW_ZIP)
        download_file(DATASET_URL, RAW_ZIP)

    archive_size = os.path.getsize(RAW_ZIP)
    print(f"Archive Size: {archive_size} bytes ({format_size(archive_size)})")

    checksum = calculate_sha256(RAW_ZIP)
    print(f"SHA256 Checksum: {checksum}")

    # Extract
    if os.path.exists(EXTRACT_DIR) and len(os.listdir(EXTRACT_DIR)) > 0:
        print(f"Extraction target already populated: {EXTRACT_DIR}")
    else:
        extract_archive(RAW_ZIP, EXTRACT_DIR)

    subdirs = os.listdir(EXTRACT_DIR)
    print(f"Extracted directory contents: {subdirs}")

    meta = {
        "source_url": DATASET_URL,
        "archive_path": os.path.relpath(RAW_ZIP, BASE_DIR),
        "archive_size_bytes": archive_size,
        "archive_size_formatted": format_size(archive_size),
        "sha256_checksum": checksum,
        "extraction_location": os.path.relpath(EXTRACT_DIR, BASE_DIR),
        "disk_free_remaining": format_size(shutil.disk_usage(BASE_DIR).free)
    }

    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Metadata recorded to {META_FILE}")
    print("=== Step 3 Completed Successfully ===")

if __name__ == "__main__":
    main()
