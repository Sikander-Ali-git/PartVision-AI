# PartVision AI — Milestone 8 Final Engineering Report
## React Frontend

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 8 — React Frontend  
**Date**: October 6, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  
**Frontend Version**: `0.4.0`  
**UI Stack**: React 18, Vite 6, TypeScript 5, Tailwind CSS 3, Phosphor Icons, Framer Motion  

---

## 1. Milestone Objective

The objective of Milestone 8 is to build a responsive, production-ready React frontend for PartVision AI. The frontend interfaces with the running FastAPI backend (`http://127.0.0.1:8000`) and provides an intuitive, high-tech interface for uploading automotive exterior photographs, reviewing AI part detections with segmentation overlays, inspecting verified vehicle compatibility, and browsing the full parts catalog.

### Strict Scope Enforcements:
- **Presentation Layer Only**: No AI inference logic was duplicated in JavaScript.
- **Authoritative Data Sources**: No vehicular fitment or compatibility logic was invented or computed in React. The model detects visual parts; the SQLite database determines vehicular compatibility.
- **Catalog Consistency**: All 19 canonical PartVision V3 classes are supported across the catalog and visualizer.
- **Zero Hallucination Display**: Compatibility records are strictly partitioned into **Verified OEM** and **Demonstration/Unverified** categories, accompanied by explicit trust disclaimers.

---

## 2. Frontend Architecture

The frontend is architected as a decoupled Single Page Application (SPA) with a unidirectional data flow and clean separation of concerns.

```
                    ┌───────────────────────────────────────────────┐
                    │               User Interaction                │
                    │       Image Drop / File Picker / Browsing     │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │               React UI Components             │
                    │   Header • Uploader • Viewer • List • Fitment │
                    └───────────────────────┬───────────────────────┘
                                            │
                        ┌───────────────────┴───────────────────┐
                        ▼                                       ▼
        ┌───────────────────────────────┐       ┌───────────────────────────────┐
        │       Custom Hooks            │       │       API Service Layer       │
        │   • useAnalysis (Upload/State)│       │   • api.ts (Centralized HTTP) │
        │   • useApiHealth (Poll status)│       │   • Typed Requests/Responses  │
        └───────────────┬───────────────┘       └───────────────┬───────────────┘
                        │                                       │
                        └───────────────────┬───────────────────┘
                                            │ REST Calls (CORS-enabled)
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │           FastAPI Backend (Port 8000)         │
                    │       POST /api/analyze  •  GET /api/parts    │
                    │       GET  /health       •  GET /api/vehicles │
                    └───────────────────────────────────────────────┘
```

### Component Hierarchy:
- `App.tsx`: Top-level application shell with tab state (`analyze`, `parts`, `about`).
  - `Header.tsx`: Global branding, tab controls, and live health monitoring pill (`GET /health`).
  - `AnalyzePage.tsx`: Primary image analysis dashboard.
    - `ImageUploader.tsx`: Drag-and-drop file upload, file validation, thumbnail preview, reset action.
    - `DetectionViewer.tsx`: Interactive SVG overlay for bounding boxes and polygon masks with 1:1 image resolution mapping.
    - `DetectionList.tsx`: List of detection cards with confidence meters and fitment badges; handles duplicate class instances distinctly.
    - `CompatibilityPanel.tsx`: Verified OEM vs demonstration fitment breakdown and trust disclosures.
    - `SummaryPanel.tsx`: High-level KPI indicators (part count, categories, top confidence, latency).
  - `PartsPage.tsx`: Full catalog browser for all 19 canonical classes with category pills, search bar, and fitment detail modal.
  - `AboutPage.tsx`: System documentation, model specifications, dataset inventory, and architectural boundary disclosures.
  - `Footer.tsx`: Architecture credits and system status.

---

## 3. Visual Design System

The application embodies a futuristic, automotive intelligence aesthetic while maintaining professional software utility:
- **Graphite Palette**:
  - Root Canvas: `#090b10` (`bg-graphite-950`)
  - Elevated Cards: `#11131a` (`bg-graphite-900`)
  - Sub-cards / Hover States: `#1a1d26` (`bg-graphite-850`)
  - Borders: `#262933` (`border-graphite-800`)
- **Accents**:
  - Primary Accent: `#00f0ff` (Cyan) with subtle drop glows (`shadow-glow-cyan`)
  - Secondary Accent: `#0066ff` (Electric Blue)
- **Status Semantic Colors**:
  - Verified OEM / Success: `#10b981` (Emerald)
  - Trim Dependent / Warning: `#f59e0b` (Amber)
  - Incompatible / Error: `#f43f5e` (Rose)
- **Typography & Details**:
  - Clean sans-serif hierarchy paired with monospace badges for canonical names, timestamps, and confidence percentages.
  - Custom dark scrollbars and responsive touch targets.

---

## 4. Component Breakdown & Features

| Component | File | Responsibilities |
| :--- | :--- | :--- |
| **Header** | `src/components/Header.tsx` | Brand header, tab switches, and live backend health poller displaying `API Online` or `API Offline`. |
| **ImageUploader** | `src/components/ImageUploader.tsx` | Drag-and-drop, native file browser, client-side format validation (JPEG, PNG, WEBP), 20MB size limiter, thumbnail display, clear/reset button. |
| **DetectionViewer** | `src/components/DetectionViewer.tsx` | Overlays SVG polygons and bounding boxes directly onto image coordinates. Preserves exact aspect ratio. Supports interactive hover and click selection. |
| **DetectionList** | `src/components/DetectionList.tsx` | Displays distinct cards for every detection instance, correctly preserving duplicates (e.g. multiple distinct wheels or doors). Shows confidence meters and verified fitment badges. |
| **CompatibilityPanel** | `src/components/CompatibilityPanel.tsx` | Displays vehicle fitments segregated by Verified OEM vs Demonstration tabs. Features explicit model/make/generation cards and trust disclaimers. |
| **SummaryPanel** | `src/components/SummaryPanel.tsx` | Summarizes analysis KPIs: total detected parts, unique part classes, highest confidence score, verified vehicle count, and inference latency. |
| **PartsPage** | `src/pages/PartsPage.tsx` | Full catalog browsing for all 19 canonical parts with category filters (Body, Glass, Lighting, Mirrors, Wheels), query search, and detail modal. |
| **AboutPage** | `src/pages/AboutPage.tsx` | Explains system architecture, decoupled design, and publishes frozen YOLO11n-seg metrics (85.70% mAP50, 4,831 training images). |

---

## 5. API Integration & Service Layer

The frontend interfaces with the FastAPI backend through a centralized, typed client in `src/services/api.ts`:
- **`healthCheck()`**: Invokes `GET /health` to verify backend and model readiness.
- **`analyzeImage(file)`**: Posts `multipart/form-data` with `file` to `POST /api/analyze`.
- **`getParts(category, query)`**: Fetches catalog items from `GET /api/parts`.
- **`getPart(partName)`**: Retrieves detailed information, aliases, and fitment records from `GET /api/parts/{part_name}`.
- **`getVehicles()`**: Queries `GET /api/vehicles`.
- **`getVehicle(id)`**: Queries `GET /api/vehicles/{vehicle_id}`.
- **`getCompatibility(partName)`**: Queries `GET /api/compatibility/{part_name}`.

Network failures and non-200 responses are automatically caught and formatted into human-readable error messages displayed within standard UI alert banners.

---

## 6. Detection & Segmentation Visualization (1:1 SVG Mapping)

A critical requirement is rendering segmentation masks accurately without distortion regardless of screen size:
1. The backend returns the original image dimensions: `image_width` and `image_height`.
2. The image element is rendered with `object-contain` inside a responsive viewport.
3. An SVG canvas is overlaid with `viewBox="0 0 {image_width} {image_height}"` and `preserveAspectRatio="xMidYMid meet"`.
4. Raw polygon coordinates `[[x1, y1], [x2, y2], ...]` from YOLO are transformed into SVG `<polygon points="..." />` strings.
5. Highlighting a polygon highlights its corresponding card in the detection list and sets active compatibility focus.

---

## 7. Compatibility UI & Trust Framework

PartVision enforces strict boundaries between computer vision and fitment authority:
- **Trust Banner**: Explicitly informs the user that YOLO detects visual exterior parts while SQLite provides vehicular compatibility records.
- **Verified vs Demonstration Segregation**:
  - **Verified OEM Fitment**: Displays a green verified shield, confirming exact OEM match across known vehicle generations.
  - **Demonstration / Unverified Fitment**: Displays an amber warning icon indicating research or unverified catalog entries.
- **No Generative Fill**: If no compatibility records exist, the UI clearly displays "No verified OEM fitments found" rather than inventing data.

---

## 8. Automated Testing Results

The frontend includes unit and component integration tests written with **Vitest** and **React Testing Library**:
- `src/test/api.test.ts`: Verifies API client methods (`healthCheck`, `analyzeImage`, `getParts`, `getPart`) including error handling.
- `src/test/App.test.tsx`: Verifies root rendering, navigation between all three tabs, distinct card rendering for duplicate part classes, and fitment segregation tabs.

### Vitest Execution Summary:
```
 ✓ src/test/api.test.ts (4 tests passed)
 ✓ src/test/App.test.tsx (4 tests passed)

Test Files  2 passed (2)
     Tests  8 passed (8)
```

### Full System Test Suite:
- **Backend Tests (Python/pytest)**: 82 passed (82 / 82)
  - `test_schemas.py`: 8 passed
  - `test_database.py`: 21 passed
  - `test_inference.py`: 33 passed
  - `test_api.py`: 20 passed
- **Frontend Tests (Vitest)**: 8 passed (8 / 8)
- **Total System Tests**: 90 passing tests across Python and TypeScript.

---

## 9. Production Build & Bundle Metrics

The application was built using TypeScript (`tsc`) and Vite's production bundler:
```bash
npm run build
```

### Build Output:
```
dist/index.html                   1.26 kB │ gzip:  0.71 kB
dist/assets/index-zMTHvOo9.css   28.41 kB │ gzip:  5.52 kB
dist/assets/index-ji1qrtGb.js   250.12 kB │ gzip: 71.59 kB
✓ built in 44.26s
```
- **Type Checking**: Zero TypeScript errors (`npx tsc --noEmit` exited cleanly).
- **Bundle Efficiency**: Main JS bundle is 250 kB (71.59 kB gzip) including React, Phosphor Icons, and Framer Motion.
- **CSS Footprint**: Tailored Tailwind CSS build is 28.4 kB (5.52 kB gzip).

---

## 10. End-to-End Verification

The complete pipeline was verified against the running backend:
1. `GET /health` verified live connectivity, updating the header badge to `● API Online`.
2. Image upload validated with valid vehicle photographs and oversized payloads (>20MB rejected).
3. `POST /api/analyze` executed successfully, delivering bounding boxes, polygons, and compatibility records.
4. Duplicate instances (e.g. front and rear wheels) rendered as distinct interactive cards.
5. Parts catalog loaded all 19 classes with filtering and compatibility drill-down modals.

---

## 11. Milestone Completion Status

Milestone 8 is **100% COMPLETE**.

All requirements for the PartVision AI React Frontend have been designed, implemented, tested, documented, and verified against frozen project artifacts.
