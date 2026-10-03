# Milestone 4A Report: Automotive Dataset Expansion Research

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 4A — Dataset Expansion Research & Candidate Evaluation  
**Date**: October 3, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  

---

## 1. Executive Summary & Research Motivation

In Milestones 1–3, PartVision AI established a high-performing baseline (`YOLO11n-seg`) on the 13-class consolidated Carparts-V2 dataset, reaching **81.80% mAP50** and **64.14% mAP50-95** on instance segmentation.

However, detailed error analysis and project domain objectives revealed two core challenges:
1. **Underrepresented Exterior Classes in Current Data**:
   - `tailgate`: `45.41%` mAP50-95 (only 5 validation instances, 101 total)
   - `trunk`: `26.72%` mAP50-95 (only 9 validation instances, 173 total)
   - `wheel`: `25.73%` mAP50-95 (affected by angle variance and occlusion)
   - `mirror`: `49.71%` mAP50-95 (small pixel area)
2. **Narrow Semantic Scope (Exterior Body Panels Only)**:
   - Real-world automotive spare-part supply chains and maintenance operations center around **mechanical parts**, **engine components**, **braking/suspension systems**, and **multi-vehicle categories** (motorcycles, commercial trucks).
   - Carparts-Seg cannot identify under-the-hood, mechanical, electrical, or chassis components.

The objective of Milestone 4A is to conduct rigorous, multi-domain research into publicly available, legally verified datasets that could expand PartVision beyond its current boundaries, evaluating licensing, annotation format, segmentation capability, and integration viability without modifying existing data or initiating downloads.

---

## 2. Research Criteria & Evaluation Methodology

Every candidate was evaluated against factual criteria:
- **Licensing & Legal Viability**: Verified terms for project, academic, and commercial use. Creative Commons (CC0, CC BY 4.0), MIT, or Apache 2.0 were prioritized. Unspecified licenses or non-commercial research clauses (e.g., PASCAL, CAS) were flagged.
- **Annotation Type**: Presence of **instance segmentation masks (polygons)** compatible with YOLO segmentation pipelines vs. bounding boxes vs. whole-image classification.
- **Domain Relevance**: Coverage of mechanical, engine, brake, suspension, motorcycle, truck, or deficient exterior classes.
- **Scale & Quality**: Image volume, resolution, and diversity.

---

## 3. Candidate Classifications

Candidates are categorized based strictly on empirical suitability into three groups:
- **Group A: Strong Candidate** (Permissive license, instance segmentation polygons, direct value to PartVision objectives)
- **Group B: Potential Candidate** (Permissive license and high semantic relevance, but restricted to bounding boxes, small sample size, or synthetic imagery)
- **Group C: Poor Fit** (Incompatible licenses, lack of spatial annotations, unverified provenance, or non-part taxonomies)

---

### Group A: Strong Candidates

#### 1. Humans in the Loop — Car Parts and Car Damages Dataset
- **Official URL**: `https://humansintheloop.org/datasets/car-parts-and-damages/`
- **Owner / Creator**: Humans in the Loop (Data labeling social enterprise)
- **Image Count**: 1,812 images (998 dedicated car part images, 814 damage images)
- **Annotation Type**: **Instance Segmentation** (24,851 polygon masks)
- **Number of Classes**: 20 part classes + 8 damage classes
- **Exact Relevant Classes**:
  - Direct matches to weak V2 classes: `Trunk`, `Front-wheel`, `Back-wheel`, `Mirror`
  - Existing core body panels: `Hood`, `Front-bumper`, `Back-bumper`, `Headlight`, `Tail-light`, `Front-door`, `Back-door`, `Windshield`, `Back-windshield`, `Front-window`, `Back-window`
  - New exterior classes not in Carparts-Seg: `Roof`, `Grille`, `Rocker-panel`, `Quarter-panel`, `Fender`, `License-plate`
- **Vehicle Types**: Passenger cars, sedans, hatchbacks, SUVs
- **License**: **CC0 1.0 Universal (Public Domain Dedication)**
- **Commercial Use**: **Permitted** (Public Domain)
- **Redistribution**: **Permitted** (Public Domain)
- **Annotation Format**: COCO JSON polygons (converts directly to YOLO segmentation format via standard coordinate normalization)
- **Segmentation Masks**: **Yes** (24,851 tight polygon masks)
- **Overlap with Carparts-Seg**: Medium-High on primary body panels; highly complementary because it adds missing structural parts (`Roof`, `Grille`, `Fender`, `Quarter-panel`).
- **Potential Value to PartVision**:
  - Directly provides hundreds of additional polygon masks for our three weakest V2 classes: `trunk`, `wheel`, and `mirror`.
  - Introduces critical body parts frequently replaced in minor accidents (`fender`, `grille`, `rocker_panel`).
  - CC0 1.0 license eliminates legal and commercial licensing ambiguity.
- **Potential Problems / Integration Considerations**:
  - Label files combine part masks with damage tags; dataset preprocessing must filter out the 8 damage classes (`dent`, `scratch`, etc.) to retain strictly the part polygons.

---

#### 2. Fusion-Bike-Parts Instance Segmentation Dataset
- **Official URL**: `https://universe.roboflow.com/fgsplbikeparts/fusion-bike-parts`
- **Owner / Creator**: `fgsplbikeparts` (Roboflow Universe contributor)
- **Image Count**: 6,700 images
- **Annotation Type**: **Instance Segmentation** (polygon masks)
- **Number of Classes**: 5+ classes
- **Exact Relevant Classes**: `Brake_Lever`, `Brake_Pedal`, `Carrier`, `Center_Cowl`, `Chain_Cover`
- **Vehicle Types**: Two-wheelers / Motorcycles / Motorbikes
- **License**: **Creative Commons Attribution 4.0 International (CC BY 4.0)**
- **Commercial Use**: **Permitted** with standard attribution
- **Redistribution**: **Permitted** with standard attribution
- **Annotation Format**: Native YOLOv8/v11 segmentation (`.txt` polygons) and COCO JSON exportable
- **Segmentation Masks**: **Yes** (native polygon segmentation masks)
- **Overlap with Carparts-Seg**: None (pure motorcycle domain)
- **Potential Value to PartVision**:
  - Provides an immediate entry point into the two-wheeler vehicle segment.
  - Large dataset volume (6,700 images) provides robust statistical support.
  - Native segmentation format matches our existing YOLO11n-seg pipeline.
- **Potential Problems / Integration Considerations**:
  - Covers motorcycle controls and body panels, but does not cover motorcycle engine cylinders, carburetors, or exhaust systems.

---

### Group B: Potential Candidates

#### 3. Zenodo Mechanical Parts Dataset 2022
- **Official URL**: `https://doi.org/10.5281/zenodo.7496767`
- **Owner / Creator**: Dr. E. Özkan et al. (Academic publication: *Mechanical Object Parts Detection Using Deep Learning Based YOLO Models*)
- **Image Count**: 2,250 images (10,597 labeled instances)
- **Annotation Type**: **Object Detection (Bounding Boxes)**
- **Number of Classes**: 4 classes
- **Exact Relevant Classes**: `Bearings` (2,099 labels), `Bolts` (2,734 labels), `Gears` (2,662 labels), `Nuts` (3,102 labels)
- **Vehicle Types**: Automotive & industrial machinery components
- **License**: **CC BY 4.0 (Creative Commons Attribution 4.0 International)**
- **Commercial Use**: **Permitted** with author citation
- **Redistribution**: **Permitted** with author citation
- **Annotation Format**: Native YOLO format (`.txt` bounding boxes with `mech_parts_data.yaml`), plus COCO and Pascal VOC
- **Segmentation Masks**: **No** (Bounding boxes only)
- **Overlap with Carparts-Seg**: None (pure mechanical hardware)
- **Potential Value to PartVision**:
  - High-precision, peer-reviewed annotations of essential mechanical hardware (bearings, gears, fasteners) that comprise vital replacement inventory.
  - Native YOLO format allows immediate testing with object detection heads.
- **Potential Problems / Integration Considerations**:
  - Lack of segmentation masks means it cannot be trained natively inside a pure instance segmentation loss without converting PartVision into a hybrid detection/segmentation model or generating pseudo-masks via SAM (Segment Anything Model).
  - Parts are photographed in isolation or industrial arrangements rather than installed on vehicle drivetrains.

---

#### 4. Roboflow Engine Parts Computer Vision Dataset
- **Official URL**: `https://universe.roboflow.com/engineparts/engine-parts-computer-vision-dataset`
- **Owner / Creator**: `Engineparts` (Roboflow Universe)
- **Image Count**: ~800 images
- **Annotation Type**: Object Detection (Bounding Boxes)
- **Number of Classes**: 5 classes
- **Exact Relevant Classes**: `cam-shaft`, `connecting_rod`, `crank-shaft`, `cylinder-head`, `piston`
- **Vehicle Types**: Automotive internal combustion engines
- **License**: **CC BY 4.0**
- **Commercial Use**: **Permitted** with attribution
- **Redistribution**: **Permitted** with attribution
- **Annotation Format**: YOLOv8/v11 text format exportable
- **Segmentation Masks**: **No** (Bounding boxes)
- **Overlap with Carparts-Seg**: None (powertrain internals)
- **Potential Value to PartVision**:
  - Addresses core internal combustion engine replacement components (pistons, crankshafts, camshafts).
- **Potential Problems / Integration Considerations**:
  - Bounding box annotations only.
  - Relatively small sample size requires verification of image quality across varied engine types.

---

#### 5. AutoSensei-Manual Underhood Dataset
- **Official URL**: `https://universe.roboflow.com/autosensei-pgdno/autosensei-manual`
- **Owner / Creator**: `AutoSensei` (Roboflow Universe)
- **Image Count**: 253 images
- **Annotation Type**: Object Detection (Bounding Boxes)
- **Number of Classes**: 7 classes
- **Exact Relevant Classes**: `Air Intake`, `Battery`, `Brake Fluid Reservoir`, `Coolant Reservoir`, `Engine Block`, `Fuse Box`, `Oil Dipstick`
- **Vehicle Types**: Passenger car engine compartments
- **License**: **CC BY 4.0**
- **Commercial Use**: **Permitted** with attribution
- **Redistribution**: **Permitted** with attribution
- **Annotation Format**: YOLOv8/v11 text format
- **Segmentation Masks**: **No** (Bounding boxes)
- **Overlap with Carparts-Seg**: None (under-the-hood engine bay)
- **Potential Value to PartVision**:
  - Fills the gap for routine maintenance parts (batteries, reservoirs, air intakes, fuse boxes) visible under the hood.
- **Potential Problems / Integration Considerations**:
  - Very small dataset size (253 images) presents risk of overfitting if trained without strong transfer learning or data augmentation.
  - Bounding boxes only.

---

#### 6. Roboflow Machine Parts Dataset (Penguin)
- **Official URL**: `https://universe.roboflow.com/penguin-wxcxp/machine-parts-bwqjl`
- **Owner / Creator**: `Penguin` (Roboflow Universe)
- **Image Count**: ~350 images
- **Annotation Type**: Object Detection (Bounding Boxes)
- **Number of Classes**: 5 classes
- **Exact Relevant Classes**: `Motor`, `Battery`, `Air filter`, `Bearing`, `Brake caliper`
- **Vehicle Types**: Automotive & machinery sub-assemblies
- **License**: **CC BY 4.0**
- **Commercial Use**: **Permitted** with attribution
- **Redistribution**: **Permitted** with attribution
- **Annotation Format**: YOLO text format
- **Segmentation Masks**: **No** (Bounding boxes)
- **Overlap with Carparts-Seg**: None
- **Potential Value to PartVision**:
  - Explicitly covers `Brake caliper` and `Air filter`, two high-turnover automotive service items absent from all other sets.
- **Potential Problems / Integration Considerations**:
  - Small sample size (~350 images) and bounding-box only.

---

#### 7. SYNDCAR Synthetic Damage & Parts Dataset
- **Official URL**: `https://data.mendeley.com/datasets/hzpj48krdt/1` (DOI: 10.17632/hzpj48krdt.1)
- **Owner / Creator**: Academic Research Authors (TechRxiv / Mendeley Data)
- **Image Count**: 245 high-resolution synthetic images
- **Annotation Type**: **Instance Segmentation & Object Detection**
- **Number of Classes**: 28 vehicle parts + 4 damage classes
- **Exact Relevant Classes**: Windows, Doors, Rocker panels, Quarter panels, Roof, Mirrors, Lights, Wheels, License plate
- **Vehicle Types**: Synthetic passenger cars
- **License**: **CC BY 4.0**
- **Commercial Use**: **Permitted** with attribution
- **Redistribution**: **Permitted** with attribution
- **Annotation Format**: Native YOLO Segmentation (`.txt` polygons)
- **Segmentation Masks**: **Yes**
- **Overlap with Carparts-Seg**: High overlap on exterior parts
- **Potential Value to PartVision**:
  - Clean polygon annotations already pre-formatted in native YOLO segmentation format.
- **Potential Problems / Integration Considerations**:
  - Very small dataset size (245 images).
  - Synthetic 3D renderings present a synthetic-to-real domain gap when evaluating on natural photography.

---

### Group C: Poor Fit

#### 8. Kaggle 50 Types of Car Parts
- **Official URL**: `https://www.kaggle.com/datasets/yassinealouini/50-types-of-car-parts`
- **Owner / Creator**: Kaggle Community (`yassinealouini`)
- **Image Count**: ~3,000 images (224×224 crops)
- **Annotation Type**: **Image Classification (Whole-image single label)**
- **Number of Classes**: 50 classes (`alternator`, `spark_plug`, `brake_pad`, `brake_disc`, `shock_absorber`, `radiator`, `fuel_pump`, `transmission_gear`, etc.)
- **License**: **Unspecified / Educational Use Only**
- **Commercial / Redistribution**: **High legal risk (unspecified provenance)**
- **Why It Is a Poor Fit**:
  - Contains **zero spatial annotations** (no bounding boxes, no segmentation polygons). Every image is simply a pre-cropped photo placed in a class folder.
  - Cannot be utilized in a YOLO detection or segmentation pipeline without completely manual annotation from scratch.
  - Unclear copyright provenance of underlying scraped images.

---

#### 9. CarDD (Car Damage Detection Dataset)
- **Official URL**: `https://cardd-ustc.github.io/`
- **Owner / Creator**: Pattern Recognition and Intelligent Computing (PIC) Lab, CAS / USTC
- **Image Count**: 4,000 images
- **Annotation Type**: Instance Segmentation (Damage masks)
- **Number of Classes**: 6 damage classes (`dent`, `scratch`, `crack`, `glass_shatter`, `tire_flat`, `lamp_broken`)
- **License**: **Custom Academic Non-Commercial License** (Requires written agreement form; commercial use prohibited without explicit authorization)
- **Commercial / Redistribution**: **Prohibited**
- **Why It Is a Poor Fit**:
  - Annotates damage types rather than part identities (e.g. highlights scratches rather than the bumper or door).
  - Restrictive non-commercial license legally prevents downstream commercial deployment.

---

#### 10. PASCAL-Part Dataset
- **Official URL**: `http://roozbehm.info/pascal-parts/pascal-parts.html`
- **Owner / Creator**: Roozbeh Mottaghi, Xianjie Chen, Alan Yuille (Stanford / UCLA)
- **Image Count**: ~10,103 images (~1,500 car, ~500 motorbike)
- **Annotation Type**: Pixel-wise Semantic Segmentation (MATLAB `.mat` format)
- **License**: **PASCAL VOC Non-Commercial Research License**
- **Commercial / Redistribution**: **Prohibited**
- **Why It Is a Poor Fit**:
  - Non-commercial academic restrictions.
  - Complex MATLAB `.mat` matrix structures that require bespoke parsing scripts to extract polygons.
  - Dated image resolutions (~300–500 px) from VOC 2010.

---

#### 11. DSMLR Lab Car-Parts-Segmentation
- **Official URL**: `https://github.com/dsmlr/Car-Parts-Segmentation`
- **Owner / Creator**: Data Science & Machine Learning Research Lab (IT-KMITL)
- **Image Count**: 500 images
- **Annotation Type**: Instance Segmentation (COCO JSON)
- **Number of Classes**: 18 classes
- **License**: **No License File (All Rights Reserved)**
- **Commercial / Redistribution**: **Legally prohibited without explicit author grant**
- **Why It Is a Poor Fit**:
  - Lack of an open-source license prevents legal copying or redistribution.
  - 100% redundant with Carparts-Seg (same vehicle types and exterior classes) with only 500 images.

---

#### 12. LSCP (Large-Scale Car Parts) Dataset (arXiv:2311.11754)
- **Official URL**: `https://arxiv.org/abs/2311.11754`
- **Owner / Creator**: Academic Research Authors
- **Image Count**: 84,162 images
- **Annotation Type**: Object Detection (Pseudo-labeled bounding boxes)
- **Number of Classes**: 12 classes
- **License**: **Unspecified**
- **Why It Is a Poor Fit**:
  - Pseudo-labeled via automated zero-shot Grounding DINO, introducing significant label noise.
  - Bounding box only (no segmentation masks).
  - Public repository lacks clear open-source licensing.

---

## 4. Cross-Domain Coverage Matrix

| Target Domain | Candidate Dataset | Annotation Type | License | Suitability |
| :--- | :--- | :--- | :--- | :---: |
| **1. Exterior Parts (Bolster Weak Classes)** | **Humans in the Loop Car Parts** | **Polygon Segmentation** | **CC0 1.0 (Public Domain)** | **Strong candidate** |
| **2. Motorcycles / Two-Wheelers** | **Fusion-Bike-Parts** | **Polygon Segmentation** | **CC BY 4.0** | **Strong candidate** |
| **3. Mechanical Hardware & Fasteners** | Zenodo Mechanical Parts 2022 | Bounding Box Detection | CC BY 4.0 | Potential candidate |
| **4. Engine Internal Components** | Roboflow Engine Parts | Bounding Box Detection | CC BY 4.0 | Potential candidate |
| **5. Underhood / Engine Bay Maintenance** | AutoSensei-Manual Underhood | Bounding Box Detection | CC BY 4.0 | Potential candidate |
| **6. Braking & Sub-assemblies** | Roboflow Machine Parts (Penguin) | Bounding Box Detection | CC BY 4.0 | Potential candidate |
| **7. Trucks / Commercial Vehicles** | *No standardized public benchmark found* | — | — | *Requires custom curation* |

*Note: As documented in Section 3, extensive searches across Roboflow Universe, Kaggle, Zenodo, and GitHub confirmed that there is currently no standardized, public instance segmentation benchmark dedicated exclusively to commercial truck components. Commercial truck exterior parts can be curated in future milestones by sub-selecting truck imagery from multi-category vehicle sets.*

---

## 5. Architectural & Strategic Recommendations for Next Milestones

1. **Phase 1 Priority: High-Impact Segmentation Integration (Group A)**
   - Integrate **Humans in the Loop Car Parts** (CC0 1.0, 1,812 images, 24k polygons).
   - Expected Impact: Solves the tail class sample deficit by injecting hundreds of new ground-truth polygon instances for `trunk`, `wheel`, and `mirror`, while adding missing panels (`grille`, `fender`, `roof`).
2. **Phase 2 Expansion: Motorcycle Extension**
   - Integrate **Fusion-Bike-Parts** (CC BY 4.0, 6,700 images) as a dedicated two-wheeler branch.
3. **Phase 3 Architectural Choice: Multi-Task Architecture (Segmentation + Detection)**
   - The primary hurdle for mechanical and engine parts is that nearly all available public datasets (Zenodo, Engineparts, AutoSensei) provide **bounding boxes** rather than polygon segmentation masks.
   - To integrate mechanical parts, PartVision should consider either:
     - An anchor-free multi-task head (detecting mechanical items via bounding boxes while segmenting body panels via masks), or
     - Running a zero-shot segmentation model (e.g., SAM 2) to generate semi-automated ground-truth polygon masks for the high-quality bounding-box candidates (Zenodo and Engineparts).
