# PartVision — Professional Automotive Frontend Documentation

## 1. Overview & Product Architecture

The **PartVision Frontend** is a professional automotive computer-vision web application engineered for automotive technicians, spare-parts managers, and repair estimators. It is built with **React 18**, **TypeScript 5**, **Vite 6**, and **Tailwind CSS 3**, implementing a **light-first, technical design system**.

The frontend is strictly decoupled from AI inference and database queries:
- **Presentation Layer Only**: Zero AI inference is conducted in JavaScript; zero compatibility calculations or fitment heuristics are implemented in the client.
- **Authoritative Decoupling**: Visual segmentation comes exclusively from the frozen **PartVision V3 YOLO11n-seg** engine via `POST /api/analyze`; vehicular fitment is determined exclusively by the relational SQLite database (`data/partvision.db`).
- **Trust & Verification**: Verified OEM catalog records are strictly segregated from unverified demonstration records.

```
                    ┌───────────────────────────────────────────────┐
                    │               User Interaction                │
                    │       Image Upload / Browse Parts & Vehicles  │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │            React 18 Client (Light UI)         │
                    │  Header • ImageUploader • DetectionViewer     │
                    │  DetectionList • CompatibilityPanel • Catalogs│
                    └───────────────────────┬───────────────────────┘
                                            │ HTTP / JSON
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │               FastAPI Backend (Port 8000)     │
                    │   • POST /api/analyze    • GET /health        │
                    │   • GET  /api/parts      • GET /api/vehicles  │
                    └───────────────────────┬───────────────────────┘
                                            │
                        ┌───────────────────┴───────────────────┐
                        ▼                                       ▼
        ┌───────────────────────────────┐       ┌───────────────────────────────┐
        │   M6A Inference Engine        │       │   M6B Compatibility Database  │
        │   YOLO11n-seg (Frozen V3)     │       │   SQLite WAL (Authoritative)  │
        │   • 19 Part Classes           │       │   • Zero AI Hallucination     │
        └───────────────────────────────┘       └───────────────────────────────┘
```

---

## 2. Design System & Tokens

The application employs a calm, information-dense, automotive-grade light palette:
- **Background**: `#F6F6F3` (`sand-50`)
- **Card / Surface**: `#FFFFFF` (`white`)
- **Primary Text**: `#151515` (`sand-900`)
- **Secondary Text**: `#6B6B68` (`sand-500`)
- **Borders & Dividers**: `#E3E3DF` (`sand-200`)
- **Muted Surfaces**: `#F0F0EC` (`sand-100`)
- **Primary Accent (Automotive Red)**: `#D6452D` (`auto-red-500`)
- **Success (Verified OEM)**: `#18794E` (`auto-green-500`)
- **Warning (Unverified / Trim-dependent)**: `#A66A00` (`auto-amber-500`)
- **Error**: `#B42318` (`auto-rose-500`)

---

## 3. Directory & Component Structure

```
frontend/
├── index.html                   # HTML entry with Inter/JetBrains fonts & light styling
├── package.json                 # Dependencies and npm scripts
├── postcss.config.js            # PostCSS configuration
├── tailwind.config.js           # Automotive light-first color tokens & typography
├── tsconfig.json                # Strict TypeScript configuration
├── vite.config.ts               # Vite configuration with proxy and vitest setup
├── .env.example                 # Environment template
├── .env                         # Local environment configuration
└── src/
    ├── App.tsx                  # Application root with tab routing (Analyze, Parts, Vehicles, About)
    ├── main.tsx                 # React entry point
    ├── index.css                # Tailwind directives and clean technical scrollbars
    ├── vite-env.d.ts            # Vite client types & ImportMetaEnv
    ├── components/
    │   ├── Header.tsx           # Brand, tab navigation, and live API status pill
    │   ├── Footer.tsx           # Architecture principles, model specs, and credits
    │   ├── ImageUploader.tsx    # Drag-and-drop file upload, preview, format & 20MB validation
    │   ├── DetectionViewer.tsx  # 1:1 SVG polygon overlay, selected part focus, subdued non-selected parts
    │   ├── DetectionList.tsx    # Compact technical rows, distinct duplicates, confidence badges
    │   └── CompatibilityPanel.tsx # Strict OEM vs demonstration fitment breakdown and trust banner
    ├── pages/
    │   ├── AnalyzePage.tsx      # Core diagnostic workflow & dual-column analysis workspace
    │   ├── PartsPage.tsx        # 19-class parts catalog with category pills & fitment modal
    │   ├── VehiclesPage.tsx     # Vehicle catalog with make filter & compatible parts drilldown
    │   └── AboutPage.tsx        # Technical architecture, V3 model metrics, and specifications
    ├── hooks/
    │   ├── useAnalysis.ts       # Upload validation, API analysis lifecycle, and selection state
    │   └── useApiHealth.ts      # Periodic API health polling (/health)
    ├── services/
    │   └── api.ts               # Typed client service for all FastAPI REST endpoints
    ├── types/
    │   └── api.ts               # Strict TypeScript types mirroring FastAPI Pydantic schemas
    ├── utils/
    │   └── colors.ts            # High-legibility technical color palette for 19 part classes
    └── test/
        ├── setup.ts             # Vitest test setup with @testing-library/jest-dom
        ├── api.test.ts          # Unit tests for API service layer
        └── App.test.tsx         # Component integration tests
```

---

## 4. Primary UX Workflow

1. **Upload**: User drops or selects an exterior vehicle photograph (JPEG, PNG, WEBP up to 20MB). Client immediately validates dimensions and file size.
2. **Preview & Confirm**: A large framed preview appears displaying filename, file size, "Change image", and prominent "Analyze image" action.
3. **Analyze**: Submits multipart payload to `POST /api/analyze`. Honest loading state ("Analyzing image...") without fabricated multi-stage animations.
4. **Inspect Results**:
   - **Workspace**: Transforms into a two-column desktop workspace.
   - **Left Column**: High-resolution image viewer with 1:1 SVG segmentation polygons and bounding boxes.
   - **Right Column**: Compact technical list of detected components with exact model confidence percentages.
5. **Interactive Selection**: Clicking a row or clicking on the image selects the component:
   - Selected part's mask is highlighted in Automotive Red (`#D6452D`).
   - Other detected components become visually subdued.
   - Compatibility panel focuses on the selected part.
6. **Verified Compatibility**: Displays verified OEM vehicle fitments (make, model, generation, year span, direct fit status) with OEM source attribution. Unverified records are strictly segregated.
7. **Reset**: "Analyze another image" button cleanly resets state without a full page reload.

---

## 5. Setup & Development

### Prerequisites
- Node.js 18+ (Node 20+ recommended)
- Running FastAPI backend on `http://127.0.0.1:8000`

### Installation
```bash
cd frontend
npm install
```

### Environment Configuration
```bash
cp .env.example .env
```
Default content:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Running Development Server
```bash
npm run dev
```
Available at `http://localhost:5173`.

### Running Automated Tests
```bash
npm run test
```

### Production Build
```bash
npm run build
```
Generates static assets in `frontend/dist/`.

---

## 6. API Integration Endpoints

| Endpoint | Method | Client Method | Purpose |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | `api.healthCheck()` | Polls backend readiness and model status |
| `/api/analyze` | `POST` | `api.analyzeImage(file)` | Uploads image; returns detections + fitment |
| `/api/parts` | `GET` | `api.getParts(category, search)` | Catalog list filtered by category/query |
| `/api/parts/{part_name}` | `GET` | `api.getPart(name)` | Full details, aliases, and compatible vehicles |
| `/api/vehicles` | `GET` | `api.getVehicles(make, model)` | Vehicles list with optional make filter |
| `/api/vehicles/{vehicle_id}` | `GET` | `api.getVehicle(id)` | Vehicle specifications and compatible OEM parts |
| `/api/compatibility/{part_name}` | `GET` | `api.getCompatibility(name)` | Direct compatibility query |
