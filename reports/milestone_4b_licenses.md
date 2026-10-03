# Milestone 4B: Open Dataset Licensing & Legal Compliance Record

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 4B — Multi-Dataset Acquisition & Taxonomy Design  
**Date**: October 3, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  

---

## 1. Legal Governance Framework

PartVision AI aims to provide commercial-ready computer-vision capabilities for automotive spare-part identification and supply chain integration. In accordance with open-source compliance standards, all external datasets incorporated into or evaluated for PartVision must possess unambiguous legal provenance.

Datasets are evaluated against four criteria:
1. **Commercial Exploitation Rights**: Explicit permission to train commercial models or embed model weights in commercial products.
2. **Redistribution Rights**: Permission to bundle, mirror, or publish modified annotations.
3. **Attribution Obligations**: Formal requirements for copyright notice and license text retention.
4. **Copyleft / Share-Alike Constraints**: Verification that upstream licenses do not impose viral copyleft restrictions on downstream application code.

---

## 2. Dataset A: Humans in the Loop — Car Parts and Damages

### Metadata & Provenance
- **Dataset Name**: Humans in the Loop Car Parts and Car Damages Dataset
- **Official Creator / Owner**: Humans in the Loop (Data labeling social enterprise)
- **Primary Source URL**: [humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset](https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/)
- **Secondary Distribution Mirros**:
  - Kaggle: [kaggle.com/datasets/humansintheloop/car-parts-and-car-damages](https://www.kaggle.com/datasets/humansintheloop/car-parts-and-car-damages)
  - Hugging Face: [huggingface.co/datasets/yusufnull/car-parts-and-damage-dataset](https://huggingface.co/datasets/yusufnull/car-parts-and-damage-dataset)
- **Local Workspace Location**: `data/external/humans_in_the_loop/`
- **Acquired Git Commit**: `e4870360afe5e0516e7567cea550d8718482611b`

### Legal Terms & Permissions
- **Governing License**: **Creative Commons Zero 1.0 Universal (CC0 1.0) Public Domain Dedication**
- **Commercial Use Status**: **PERMITTED** (CC0 waives all copyright and related rights worldwide).
- **Attribution Requirements**: **NONE LEGALLY REQUIRED** (CC0 does not mandate attribution, though scholarly and engineering courtesy attribution is maintained).
- **Redistribution Rights**: **PERMITTED** (Public domain dedication permits unrestricted sharing, modification, and merging).
- **Patent / Trademark Grants**: Standard CC0 waiver; does not convey trademark rights to the name "Humans in the Loop".
- **Restrictions**: No use restrictions.

### Exact Source Evidence
From the official Humans in the Loop portal and open dataset catalog:
> *"All of the datasets curated by Humans in the Loop are dedicated to the public domain under CC0 1.0 Universal. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission."*

---

## 3. Dataset B: Fusion-Bike-Parts Instance Segmentation

### Metadata & Provenance
- **Dataset Name**: Fusion-Bike-Parts Instance Segmentation Dataset
- **Official Creator / Owner**: `fgsplbikeparts` (Roboflow Universe contributor)
- **Primary Source URL**: [universe.roboflow.com/fgsplbikeparts/fusion-bike-parts](https://universe.roboflow.com/fgsplbikeparts/fusion-bike-parts)
- **Publication Date**: October 2024
- **Local Workspace Location**: `data/external/fusion_bike_parts/` (Directory initialized)

### Legal Terms & Permissions
- **Governing License**: **Creative Commons Attribution 4.0 International (CC BY 4.0)**
- **Commercial Use Status**: **PERMITTED** (CC BY 4.0 explicitly authorizes commercial reuse and derivative works).
- **Attribution Requirements**: **MANDATORY**. Downstream distributions and trained models referencing this dataset must provide appropriate credit, provide a link to the license, and indicate if changes were made.
- **Redistribution Rights**: **PERMITTED** under identical or compatible terms with proper attribution.
- **Restrictions**: You must give appropriate credit and provide a link to the CC BY 4.0 license.

### Required Citation
```bibtex
@misc{ fusion-bike-parts_dataset,
  title = { Fusion-Bike-Parts Dataset },
  type = { Open Source Dataset },
  author = { fgsplbikeparts },
  howpublished = { \url{ https://universe.roboflow.com/fgsplbikeparts/fusion-bike-parts } },
  url = { https://universe.roboflow.com/fgsplbikeparts/fusion-bike-parts },
  journal = { Roboflow Universe },
  publisher = { Roboflow },
  year = { 2024 },
  month = { oct }
}
```

### Operational Acquisition Constraint
While the **license** is fully permissive (CC BY 4.0), **programmatic acquisition** is gated by Roboflow Universe platform policies:
1. Automated requests without an active browser session trigger Cloudflare anti-bot verification (`HTTP 403 Forbidden`).
2. Programmatic export requires generating an API token tied to a Roboflow user account.
3. In compliance with Milestone 4B rules, acquisition was halted rather than attempting unauthorized automated workarounds.

---

## 4. Existing Baseline Dataset: Ultralytics Carparts-Seg

### Metadata & Provenance
- **Dataset Name**: Carparts-Seg (Official Ultralytics asset release)
- **Primary Source URL**: [github.com/ultralytics/assets/releases/download/v0.0.0/carparts-seg.zip](https://github.com/ultralytics/assets/releases/download/v0.0.0/carparts-seg.zip)
- **Archive SHA256**: `e2eea20030d02366b07174bcdbcc843f63791bdd53962a83e00636d15e78e41f`
- **License**: AGPL-3.0 / Enterprise Commercial (Ultralytics Open Source Dataset Collection)
- **Current Status**: Fully intact and verified in `data/processed/carparts-seg/` and derived `data/processed/carparts-v2/`.

---

## 5. Compliance Summary Matrix

| Dataset | License | Commercial Use | Redistribution | Attribution Req. | Acquisition Status |
|---|---|---|---|---|---|
| **Humans in the Loop** | CC0 1.0 Universal | **Yes** | **Yes** | None (Optional) | **Verified on Disk** |
| **Fusion-Bike-Parts** | CC BY 4.0 | **Yes** | **Yes** | Mandatory Citation | **Awaiting User API Key** |
| **Ultralytics Carparts-Seg** | AGPL-3.0 / Open | Permitted | Permitted | Mandatory | **Intact (Control V1/V2)** |
