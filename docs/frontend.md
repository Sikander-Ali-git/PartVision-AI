# PartVision AI — Frontend Developer Documentation

## 1. Overview & Architecture

The **PartVision AI Frontend** is a modern, responsive single-page application built with **React 18**, **TypeScript**, **Vite**, and **Tailwind CSS**. It provides an intuitive, high-tech interface for automotive exterior spare-part identification and vehicle compatibility inspection.

```
  ┌─────────────────────────────────────────────────────────────┐
  │                 User Browser / React SPA                    │
  │   • Image Uploader (Drag & Drop, JPG/PNG/WEBP, Max 20MB)    │
  │   • High-Precision SVG Segmentation & Bounding Box Overlay  │
  │   • Interactive Part Instance List & Confidence Meters      │
  │   • Authoritative Fitment Panel (OEM vs Demonstration)      │
  │   • Parts Catalog Explorer (19 Classes, 5 Categories)       │
  │   • System Architecture & YOLO11n-seg Model Metrics Page    │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ HTTP / JSON
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               FastAPI Backend (Port 8000)                   │
  │   • POST /api/analyze         • GET /health                 │
  │   • GET  /api/parts           • GET /api/parts/{name}       │
  │   • GET  /api/vehicles        • GET /api/compatibility/...  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
  ┌─────────────────────────────┐ ┌─────────────────────────────┐
  │   M6A Inference Engine      │ │  M6B Compatibility DB       │
  │   YOLO11n-seg (Frozen V3)   │ │  SQLite WAL (Authoritative) │
  │   • 19 Part Classes         │ │  • Zero AI Hallucination    │
  └─────────────────────────────┘ └─────────────────────────────┘
```

### Core Design Rules
1. **Presentation Layer Only**: Zero AI inference is performed in JavaScript; zero compatibility calculations or fitment rules are implemented in React.
2. **Authoritative Decoupling**: Visual segmentation comes exclusively from the frozen **YOLO11n-seg** engine via `POST /api/analyze`; vehicular fitment is determined exclusively by the relational SQLite database.
3. **Verified Fitment Segregation**: Verified OEM catalog records are strictly segregated from demonstration or unverified fitments in the UI.
4. **Zero-Distortion SVG Mapping**: Detection polygons and bounding boxes map 1:1 to original image dimensions using responsive SVG viewports with identical aspect ratio preservation.

---

## 2. Directory Structure

```
frontend/
├── index.html                   # HTML entry point with dark theme and fonts
├── package.json                 # Dependencies and npm scripts
├── postcss.config.js            # PostCSS configuration for Tailwind
├── tailwind.config.js           # Custom automotive dark theme & colors
├── tsconfig.json                # TypeScript compiler configuration (strict)
├── vite.config.ts               # Vite configuration with proxy and test setup
├── .env.example                 # Template for environment variables
├── .env                         # Local runtime environment configuration
└── src/
    ├── App.tsx                  # Root component with tab navigation
    ├── main.tsx                 # React DOM mount point
    ├── index.css                # Tailwind directives and custom scrollbars
    ├── vite-env.d.ts            # Vite client types & ImportMetaEnv
    ├── components/
    │   ├── Header.tsx           # Global branding, tabs, and live API status badge
    │   ├── Footer.tsx           # Architecture principles and project credits
    │   ├── ImageUploader.tsx    # Drag-and-drop file upload, preview, and limits
    │   ├── DetectionViewer.tsx  # SVG polygon masks and bounding box overlays
    │   ├── DetectionList.tsx    # Detected instance cards with confidence bars
    │   ├── CompatibilityPanel.tsx # Strict OEM vs demonstration fitment breakdown
    │   └── SummaryPanel.tsx     # KPI metrics (counts, confidence, latency)
    ├── pages/
    │   ├── AnalyzePage.tsx      # Main image analysis workspace
    │   ├── PartsPage.tsx        # 19-class parts catalog with fitment modal
    │   └── AboutPage.tsx        # Technical architecture and V3 model metrics
    ├── hooks/
    │   ├── useAnalysis.ts       # State management for file upload and API analysis
    │   └── useApiHealth.ts      # Periodic API health status polling
    ├── services/
    │   └── api.ts               # Centralized typed HTTP client for FastAPI backend
    ├── types/
    │   └── api.ts               # TypeScript interfaces mirroring FastAPI Pydantic schemas
    ├── utils/
    │   └── colors.ts            # Taxonomy palette mapping for all 19 part classes
    └── test/
        ├── setup.ts             # Vitest test setup (jest-dom matchers)
        ├── api.test.ts          # Unit tests for API service layer
        └── App.test.tsx         # Component and navigation integration tests
```

---

## 3. Getting Started

### Prerequisites
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **npm**: v9.0.0 or higher
- Running **PartVision FastAPI backend** on `http://127.0.0.1:8000`

### Installation
From the repository root:
```bash
cd frontend
npm install
```

### Environment Configuration
The frontend connects to the backend via `VITE_API_BASE_URL`. Copy the template if `.env` does not exist:
```bash
cp .env.example .env
```
Default `.env` contents:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Running Development Server
```bash
npm run dev
```
By default, the Vite development server starts at:
```
http://localhost:5173
```
API requests to `/api` and `/health` are automatically proxied to `http://127.0.0.1:8000` if relative paths are used, or accessed directly via `VITE_API_BASE_URL`.

### Building for Production
```bash
npm run build
```
This runs `tsc` for complete type-checking followed by Vite's production bundler, producing optimized static assets in `frontend/dist/`.

### Previewing Production Build
```bash
npm run preview
```

### Running Automated Tests
```bash
npm run test
```
Runs the Vitest suite covering API client methods and React component rendering.

---

## 4. Key Components and Features

### 4.1 Image Uploader (`ImageUploader.tsx`)
- Drag-and-drop zone and click-to-browse file selector.
- Enforces allowed MIME types (`image/jpeg`, `image/png`, `image/webp`).
- Rejects files exceeding the 20MB limit with immediate user feedback.
- Generates a local preview thumbnail before submission.
- One-click reset clears current upload and resets analysis state.

### 4.2 High-Precision Detection Viewer (`DetectionViewer.tsx`)
- Displays the original vehicle image in an responsive container.
- Renders an SVG overlay matching the backend image's coordinate space (`viewBox="0 0 width height"`).
- Features toggleable bounding boxes, polygon segmentation masks, and label tags.
- Interactive cross-highlighting: hovering or clicking a polygon highlights both the mask and corresponding detection card.
- Renders segmented masks with class-specific color schemes from `colors.ts`.

### 4.3 Detection List (`DetectionList.tsx`)
- Displays distinct cards for every detection instance, correctly preserving duplicates (e.g. multiple distinct wheels or doors).
- Shows class display name, confidence percentage bar, canonical taxonomy string, and verified fitment counter.
- Clicking an instance focuses the vehicle compatibility panel.

### 4.4 Compatibility Panel (`CompatibilityPanel.tsx`)
- Enforces the architectural rule: **"YOLO detects visual parts; SQLite determines compatibility."**
- Filters fitments by tab: **All**, **Verified OEM**, or **Demonstration/Unverified**.
- Displays vehicle make, model, generation, year span, vehicle type, fitment status (`direct_fit`, `trim_dependent`), and source.
- Prominently displays safety and trust disclaimers reminding users that compatibility is retrieved from relational database records, not generative AI.

### 4.5 Summary KPI Panel (`SummaryPanel.tsx`)
- Total parts detected in image.
- Count of unique part categories.
- Top model confidence percentage.
- Count of verified OEM vehicular fitments.
- Pipeline execution latency reported directly by backend.

### 4.6 Parts Catalog (`PartsPage.tsx`)
- Browses all 19 canonical PartVision V3 classes categorized into:
  - *Exterior Body* (`front_bumper`, `back_bumper`, `fender`, `hood`, `trunk`, `tailgate`, `quarter_panel`, `rocker_panel`, `roof`)
  - *Exterior Glass* (`front_glass`, `back_glass`, `side_window`)
  - *Lighting* (`front_light`, `back_light`)
  - *Mirrors* (`mirror`)
  - *Wheels* (`wheel`)
  - *Doors & Grille* (`front_door`, `back_door`, `grille`)
- Category pill filters and real-time search filter.
- Deep-dive modal displays part descriptions, known search aliases, and real-time compatibility lookup.

### 4.7 Technical Architecture Page (`AboutPage.tsx`)
- Documents the end-to-end pipeline and model specifications.
- Details the frozen PartVision V3 YOLO11n-seg model (85.70% mAP50, 4,831 training images, 35,759 polygon instances).
- Explains architectural decoupling ensuring zero AI hallucination in vehicular fitment.

---

## 5. Visual Styling & Color Tokens

Tailwind CSS has been configured with an automotive-grade dark graphite palette:
- **Base Background**: `#090b10` (`graphite-950`)
- **Card / Surface Background**: `#11131a` (`graphite-900`)
- **Card Highlight / Active**: `#1a1d26` (`graphite-850`)
- **Borders & Dividers**: `#262933` (`graphite-800`)
- **Primary Accent**: `#00f0ff` (Cyan) with subtle drop glows
- **Secondary Accent**: `#0066ff` (Electric Blue)
- **Status Colors**:
  - Success / Verified: `#10b981` (Emerald)
  - Warning / Trim-Dependent: `#f59e0b` (Amber)
  - Danger / Error: `#f43f5e` (Rose)

---

## 6. API Integration Contract

The frontend strictly uses the endpoints defined in Milestone 7:

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/health` | `GET` | Health monitoring badge; checks model and database readiness |
| `/api/analyze` | `POST` | Uploads multipart image and receives detections + compatibility |
| `/api/parts` | `GET` | Catalog browsing with category and query filters |
| `/api/parts/{part_name}` | `GET` | Detailed part description, aliases, and compatible vehicles |
| `/api/vehicles` | `GET` | List all supported vehicles in database |
| `/api/vehicles/{vehicle_id}` | `GET` | Vehicle details and all compatible parts |
| `/api/compatibility/{part_name}` | `GET` | Fast vehicle compatibility lookup for a specific part |
