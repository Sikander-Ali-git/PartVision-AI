# PartVision AI — Milestone 8 Final Engineering Report
## Professional Automotive Frontend UX/UI Rebuild

**Project**: PartVision AI — Automotive Spare-Part Identification and Compatibility System  
**Milestone**: 8 — Professional Frontend UX/UI Rebuild  
**Date**: October 6, 2026  
**Workspace**: `/Volumes/Toshiba 1TB/PartVision`  
**Frontend Version**: `0.4.0`  
**Stack**: React 18, Vite 6, TypeScript 5, Tailwind CSS 3, Phosphor Icons  

---

## 1. Objective

The objective of Milestone 8 is to construct a professional, production-grade automotive software frontend for PartVision AI. The previous prototype utilized an artificial dark-neon "cyberpunk" theme that failed to reflect the needs of automotive diagnostic workflows. This milestone executes a complete ground-up rebuild implementing a **light-first, technical design system** optimized for parts technicians, repair appraisers, and automotive engineers.

### Core Product Principles Enforced:
1. **Primary Workflow**: `UPLOAD → ANALYZE → SEE DETECTED PARTS → SELECT PART → VIEW VERIFIED FITMENT → EXPLORE DETAILS`.
2. **Content Over Decoration**: The user's vehicle image, segmentation masks, and fitment records take primary visual priority over decorative elements.
3. **Architectural Decoupling**: Visual components are identified exclusively by the frozen **PartVision V3 YOLO11n-seg** engine; vehicular compatibility is determined exclusively by the relational SQLite database (`data/partvision.db`). No generative AI or LLMs are involved in compatibility determination.
4. **Verified vs Unverified Segregation**: Verified OEM catalog records and unverified demonstration records are strictly separated in the interface.

---

## 2. Design Philosophy

The interface was built to resemble modern industrial technical software (e.g. professional automotive diagnostic scan-tool software, OEM electronic parts catalogs, and engineering SaaS):
- **Light-First Foundation**: Clean light surface styling (`#F6F6F3` background, `#FFFFFF` surfaces, `#151515` primary text, `#6B6B68` secondary text, `#E3E3DF` borders).
- **Restrained Automotive Accent**: Single primary accent in Automotive Red (`#D6452D`) utilized exclusively for primary actions, selected component highlights, and active navigation indicators.
- **Zero AI Theatrics**: Elimination of neon glow, fake neural scan lines, floating cards, artificial multi-stage loading texts, and oversized marketing slogans.
- **5-Second Intuitiveness**: A technician can understand and operate the primary image identification workflow within five seconds without training.

---

## 3. UX Workflow

```
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. UPLOAD IMAGE                                             │
  │    Drag & drop or file picker (JPG/PNG/WEBP, Max 20 MB).    │
  │    Instant validation & large preview with file size.       │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. ANALYZE IMAGE                                            │
  │    Honest loading state: "Analyzing image...".              │
  │    POST /api/analyze execution via FastAPI.                 │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. DUAL-COLUMN WORKSPACE TRANSFORMATION                     │
  │    Left: High-resolution image viewer with 1:1 SVG overlay. │
  │    Right: Technical detection list & summary indicator.     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. INTERACTIVE PART SELECTION                               │
  │    Clicking a part highlights its mask in Automotive Red;   │
  │    other detections become subdued for clear visual focus.  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 5. VERIFIED COMPATIBILITY INSPECTION                        │
  │    Authoritative OEM vehicle fitment records displayed      │
  │    with generation, years, fitment status, and source.      │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 6. RESET OR EXPLORE                                         │
  │    "Analyze another image" resets state cleanly.            │
  │    Parts & Vehicles catalog tabs allow full exploration.    │
  └─────────────────────────────────────────────────────────────┘
```

---

## 4. Frontend Architecture

The frontend is architected as a lightweight Single Page Application (SPA) with a unidirectional data flow and strict separation of concerns.

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx              # Minimal navigation & real-time health indicator
│   │   ├── Footer.tsx              # Architecture summary and trust principles
│   │   ├── ImageUploader.tsx       # Drag-and-drop file upload, preview, and limits
│   │   ├── DetectionViewer.tsx     # 1:1 SVG polygon overlay & selected focus
│   │   ├── DetectionList.tsx       # Compact technical rows with confidence display
│   │   └── CompatibilityPanel.tsx  # OEM vs demonstration segregation & trust banner
│   ├── pages/
│   │   ├── AnalyzePage.tsx         # Primary analysis workspace
│   │   ├── PartsPage.tsx           # 19-class parts catalog with fitment modal
│   │   ├── VehiclesPage.tsx        # Vehicle catalog with make filter & fitment modal
│   │   └── AboutPage.tsx           # Technical architecture, V3 metrics, and specifications
│   ├── hooks/
│   │   ├── useAnalysis.ts          # Image upload, validation, and analysis state
│   │   └── useApiHealth.ts         # Periodic health polling for backend readiness
│   ├── services/
│   │   └── api.ts                  # Typed client service for all REST endpoints
│   ├── types/
│   │   └── api.ts                  # Strict TypeScript interfaces matching backend
│   └── utils/
│       └── colors.ts               # Clean technical color palette for 19 classes
```

---

## 5. Component Breakdown

| Component | File | Responsibilities |
| :--- | :--- | :--- |
| **Header** | `Header.tsx` | Minimal navigation (`Analyze`, `Parts`, `Vehicles`, `About`) and live API status badge (`● Online` / `● API unavailable`). |
| **Footer** | `Footer.tsx` | Technical footer stating system boundaries, model specs, and database authority. |
| **ImageUploader** | `ImageUploader.tsx` | Drag-and-drop zone, file picker, client-side format & 20MB validation, framed preview, file details, and honest loading state. |
| **DetectionViewer** | `DetectionViewer.tsx` | Responsive SVG coordinate canvas mapped 1:1 to original image dimensions. Prominently highlights selected parts in Automotive Red while subduing unselected parts. |
| **DetectionList** | `DetectionList.tsx` | Compact technical rows displaying part name, exact confidence percentage (`86.1%`), and fitment badge. Distinct rows for duplicate instances (e.g. multiple wheels). |
| **CompatibilityPanel** | `CompatibilityPanel.tsx` | Authoritative vehicle compatibility breakdown segregated into Verified OEM and Unverified fitments, accompanied by mandatory trust disclaimers. |
| **PartsPage** | `PartsPage.tsx` | Complete 19-class catalog with category filters, search, and deep-dive vehicle fitment modal. |
| **VehiclesPage** | `VehiclesPage.tsx` | Vehicle catalog with make filter, search, and vehicle-specific compatible parts list. |
| **AboutPage** | `AboutPage.tsx` | Concise technical overview, pipeline diagram, frozen V3 metrics, and expandable technical specifications. |

---

## 6. API Integration

All HTTP communication is centralized in `src/services/api.ts` utilizing `fetch` and typed responses:
- `api.healthCheck()`: `GET /health`
- `api.analyzeImage(file)`: `POST /api/analyze` (multipart upload)
- `api.getParts(category, search)`: `GET /api/parts`
- `api.getPart(name)`: `GET /api/parts/{part_name}`
- `api.getVehicles(make)`: `GET /api/vehicles`
- `api.getVehicle(id)`: `GET /api/vehicles/{vehicle_id}`
- `api.getCompatibility(partName)`: `GET /api/compatibility/{part_name}`

HTTP 400, 413, 415, and 500 status codes are captured cleanly and converted to friendly user error alerts.

---

## 7. Detection Visualization (1:1 SVG Mapping)

In `DetectionViewer.tsx`, image distortion is completely prevented:
1. The original image resolution (`width` and `height`) returned by `POST /api/analyze` is assigned to `<svg viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">`.
2. Raw polygon coordinates `[[x1, y1], [x2, y2], ...]` from YOLO are transformed into SVG `<polygon points="..." />`.
3. Bounding box coordinates `[x1, y1, x2, y2]` map directly into `<rect x={x1} y={y1} width={x2-x1} height={y2-y1} />`.
4. When a detection is selected, its stroke changes to `#D6452D` (`strokeWidth=3`) and fill to `rgba(214, 69, 45, 0.35)`. Other detections are rendered with low opacity (`0.5`), subduing clutter and directing technician focus.

---

## 8. Compatibility Presentation & Trust Framework

PartVision strictly enforces the boundary between vision and compatibility:
- **Trust Explanation**: Prominently displayed: *"PartVision identifies the visible part using computer vision. Vehicle compatibility is retrieved from the structured fitment database."*
- **Strict Segregation**: Verified OEM vehicle records (green shield checkmark, direct fit status, source attribution) are separated from demonstration or unverified records.
- **Honest Metrics**: Confidence is explicitly labeled as *"Model detection confidence"*, not accuracy or compatibility.

---

## 9. Responsive Design

The application was designed and tested across four responsive breakpoints:
- **Desktop (1440 × 900)**: Two-column layout with dominant visual priority given to the image viewer (8/12 grid columns) and sticky detection/fitment controls (4/12 grid columns).
- **Laptop (1280 × 800)**: Two-column layout with proportional scaling and scrollable detection tables.
- **Tablet (768 × 1024)**: Responsive column wrapping with full-width header controls.
- **Mobile (390 × 844)**: Stacked single-column layout (`Image → Detection List → Selected Part → Compatibility`), hamburger navigation menu, and touch targets exceeding 44px.

---

## 10. Accessibility

- **Semantic HTML**: `<header>`, `<main>`, `<nav>`, `<footer>`, `<section>`, `<button>`, `<input>`.
- **Keyboard Navigation**: All interactive elements (drop target, detection rows, catalog cards, modal close buttons) are fully keyboard-navigable (`Tab`, `Enter`, `Space`).
- **Visible Focus States**: Dedicated accessible focus ring (`:focus-visible` with automotive red accent).
- **Color Independence**: Statuses and selections communicate via text labels and icons (`CheckCircle`, `Warning`, `ShieldCheck`), not color alone.
- **Screen Reader Support**: ARIA attributes (`role="status"`, `role="listbox"`, `role="option"`, `aria-selected`, `aria-label`).

---

## 11. Automated Testing Results

The frontend test suite was implemented with **Vitest** and **React Testing Library**:
- `src/test/api.test.ts`: 5 unit tests for API client methods and error handling.
- `src/test/App.test.tsx`: 4 integration tests for tab navigation, duplicate detection handling, and fitment segregation.

### Vitest Output:
```
 ✓ src/test/api.test.ts (5)
 ✓ src/test/App.test.tsx (4)

 Test Files  2 passed (2)
      Tests  9 passed (9)
   Duration  52.09s
```

### Full System Test Suite:
- Backend tests (`pytest`): 82 / 82 passing.
- Frontend tests (`vitest`): 9 / 9 passing.
- Total tests: **91 passing tests** across Python and TypeScript.

---

## 12. Visual QA Verification

| Viewport | Dimensions | Layout Check | Status |
| :--- | :--- | :--- | :--- |
| **Desktop** | 1440 × 900 | Two-column workspace; image receives visual priority; sidebar rows aligned. | **PASS** |
| **Laptop** | 1280 × 800 | Two-column workspace; proportional scaling; no clipping. | **PASS** |
| **Tablet** | 768 × 1024 | Responsive wrapping; touch-friendly controls; no horizontal overflow. | **PASS** |
| **Mobile** | 390 × 844 | Single-column stack; mobile menu functional; readable typography. | **PASS** |

---

## 13. Production Build Result

Executed `npm run build`:
```
dist/index.html                   1.35 kB │ gzip:  0.73 kB
dist/assets/index-xFf4vNFn.css   24.46 kB │ gzip:  5.03 kB
dist/assets/index-DyTx3T__.js   247.61 kB │ gzip: 70.35 kB
✓ built in 42.24s
```
- TypeScript compilation (`npx tsc --noEmit`): 0 errors, 0 warnings.
- Production bundle: 247.6 kB JS, 24.5 kB CSS.

---

## 14. Real End-to-End Test Execution

Tested against the live backend using test image `data/processed/partvision-v3/images/test/hitl_Car_damages_1033.png`:
- **Image Dimensions**: `699 × 527` pixels.
- **Health Check**: `GET /health` returned `200 OK` (`model_loaded: true`, `database_connected: true`).
- **Analysis Execution**: `POST /api/analyze` executed cleanly.
- **Detections**: 18 total detections extracted.
  - `Detection 0: Wheel (wheel) - 95.4% - 6 verified fitments`
  - `Detection 1: Wheel (wheel) - 93.8% - 6 verified fitments` (Duplicate wheels maintained separately)
  - `Detection 3: Front Light (front_light) - 93.4% - 5 verified fitments`
  - `Detection 4: Hood (hood) - 93.2% - 5 verified fitments`
  - `Detection 5: Fender (fender) - 92.9% - 1 verified fitment`
  - `Detection 6: Grille (grille) - 92.2% - 4 verified fitments`
  - `Detection 9: Front Bumper (front_bumper) - 86.1% - 8 verified fitments`
- **Fitment Matching**: Selecting `Front Bumper` resolved 8 verified vehicles (Maruti Suzuki Swift, Baleno, Dzire, Brezza, Hyundai Creta, Venue, i20, Tata Nexon).
- **Reset Workflow**: Clicking "Analyze another image" cleared the result state cleanly without requiring a page reload.

---

## 15. Known Limitations & Roadmap

- Dark mode is currently omitted in favor of the light-first technical palette (can be added as an optional toggle in future releases).
- Image zooming on mobile currently relies on browser pinch-to-zoom; dedicated zoom pan controls could be added in a future update.

---

## 16. Conclusion

Milestone 8 is **100% COMPLETE**. The PartVision AI frontend is now a professional, calm, highly usable automotive diagnostic product that reflects genuine industrial software standards.
