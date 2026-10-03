"""
PartVision AI - Fast Parallel Download of HITL Images via huggingface_hub
Pulls all full binary images and metadata directly into data/external/humans_in_the_loop.
Caches strictly inside the workspace on the external drive.
"""

import os
import sys
from pathlib import Path

WORKSPACE = Path("/Volumes/Toshiba 1TB/PartVision")
CACHE_DIR = WORKSPACE / ".hf_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ["HF_HOME"] = str(CACHE_DIR)

from huggingface_hub import snapshot_download

HITL_DIR = WORKSPACE / "data" / "external" / "humans_in_the_loop"
REPO_ID = "yusufnull/car-parts-and-damage-dataset"

def run_download():
    print("=" * 60)
    print("DOWNLOADING HUMANS IN THE LOOP DATASET (PARALLEL WORKERS)")
    print("=" * 60)
    print(f"Target Directory: {HITL_DIR}")
    print(f"Cache Directory:  {CACHE_DIR}")

    path = snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        local_dir=str(HITL_DIR),
        max_workers=8
    )

    print("=" * 60)
    print(f"DOWNLOAD COMPLETE! Local directory: {path}")
    print("=" * 60)

if __name__ == "__main__":
    run_download()
