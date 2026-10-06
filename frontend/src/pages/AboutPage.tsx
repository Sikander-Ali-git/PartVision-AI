/**
 * frontend/src/pages/AboutPage.tsx
 * Calm, professional system overview and technical specifications.
 */

import React, { useState } from 'react';
import { CaretDown, CaretUp, ShieldCheck, Database, Cpu } from '@phosphor-icons/react';

export const AboutPage: React.FC = () => {
  const [techOpen, setTechOpen] = useState(false);

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-sand-900 tracking-tight">
          About PartVision
        </h1>
        <p className="text-sm text-sand-500 mt-1">
          Automotive computer-vision diagnostic software for spare-part identification and verified fitment.
        </p>
      </div>

      {/* Section 1: What is PartVision? */}
      <section className="bg-white border border-sand-200 rounded-xl p-6 shadow-card space-y-3">
        <h2 className="text-base font-bold text-sand-900">
          What is PartVision?
        </h2>
        <p className="text-sm text-sand-600 leading-relaxed">
          PartVision is a dedicated automotive computer-vision service designed to identify visible exterior vehicle components from standard photographs and immediately look up verified OEM vehicular fitment records.
        </p>
      </section>

      {/* Section 2: How It Works */}
      <section className="bg-white border border-sand-200 rounded-xl p-6 shadow-card space-y-4">
        <h2 className="text-base font-bold text-sand-900">
          How It Works
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 items-center text-xs font-mono py-2">
          <div className="p-3 rounded-lg bg-sand-50 border border-sand-200 text-center font-medium text-sand-900">
            Image Upload
          </div>
          <div className="text-center text-sand-400 hidden sm:block">→</div>
          <div className="p-3 rounded-lg bg-sand-50 border border-sand-200 text-center font-medium text-sand-900">
            YOLO11n-seg (V3)
          </div>
          <div className="text-center text-sand-400 hidden sm:block">→</div>
          <div className="p-3 rounded-lg bg-sand-50 border border-sand-200 text-center font-medium text-sand-900">
            SQLite Database
          </div>
        </div>

        <div className="space-y-3 text-sm text-sand-600 pt-2 border-t border-sand-200">
          <div className="flex items-start gap-2.5">
            <Cpu size={18} className="text-auto-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-sand-900 font-medium">1. Computer Vision Segmentation:</strong>
              <p className="text-xs text-sand-500 mt-0.5">
                The image is processed by the frozen YOLO11n-seg model, detecting visible spare parts, delineating bounding boxes, and extracting polygon segmentation masks.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <Database size={18} className="text-auto-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-sand-900 font-medium">2. Authoritative Compatibility Lookup:</strong>
              <p className="text-xs text-sand-500 mt-0.5">
                Canonical part identifiers are queried directly against a normalized SQLite compatibility database to retrieve verified vehicle makes, models, and generation years.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <ShieldCheck size={18} className="text-auto-green-500 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-sand-900 font-medium">3. Architectural Decoupling:</strong>
              <p className="text-xs text-sand-500 mt-0.5">
                The AI model never infers or invents vehicle fitment. Computer vision identifies what is visible; the relational database determines compatibility.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Model & Dataset Specifications */}
      <section className="bg-white border border-sand-200 rounded-xl p-6 shadow-card space-y-4">
        <h2 className="text-base font-bold text-sand-900">
          Model & Dataset Metrics
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-3.5 bg-sand-50 rounded-lg border border-sand-200">
            <div className="text-xl font-bold font-mono text-sand-900">19</div>
            <div className="text-xs text-sand-500 mt-0.5">Canonical classes</div>
          </div>

          <div className="p-3.5 bg-sand-50 rounded-lg border border-sand-200">
            <div className="text-xl font-bold font-mono text-sand-900">4,831</div>
            <div className="text-xs text-sand-500 mt-0.5">Training images</div>
          </div>

          <div className="p-3.5 bg-sand-50 rounded-lg border border-sand-200">
            <div className="text-xl font-bold font-mono text-sand-900">35,759</div>
            <div className="text-xs text-sand-500 mt-0.5">Polygon instances</div>
          </div>

          <div className="p-3.5 bg-sand-50 rounded-lg border border-sand-200">
            <div className="text-xl font-bold font-mono text-auto-green-600">85.70%</div>
            <div className="text-xs text-sand-500 mt-0.5">Mask mAP50</div>
          </div>
        </div>

        <p className="text-xs text-sand-500 italic">
          Metrics reflect evaluation against the held-out PartVision V3 test split on Apple Silicon (MPS).
        </p>
      </section>

      {/* Section 4: Expandable Technical Specifications */}
      <section className="bg-white border border-sand-200 rounded-xl overflow-hidden shadow-card">
        <button
          type="button"
          onClick={() => setTechOpen(!techOpen)}
          className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-sand-50 transition-colors"
        >
          <span className="text-sm font-semibold text-sand-900">
            Technical Implementation Details
          </span>
          {techOpen ? <CaretUp size={16} /> : <CaretDown size={16} />}
        </button>

        {techOpen && (
          <div className="px-6 pb-6 pt-2 border-t border-sand-200 text-xs font-mono space-y-2 text-sand-600">
            <div className="flex justify-between py-1 border-b border-sand-100">
              <span className="text-sand-500">Vision Architecture:</span>
              <span className="text-sand-900">YOLO11n-seg (Frozen V3)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-sand-100">
              <span className="text-sand-500">Inference Engine:</span>
              <span className="text-sand-900">PartVisionInferenceEngine (PyTorch/MPS)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-sand-100">
              <span className="text-sand-500">Backend Framework:</span>
              <span className="text-sand-900">FastAPI 0.115+ (Uvicorn / Pydantic V2)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-sand-100">
              <span className="text-sand-500">Database Engine:</span>
              <span className="text-sand-900">SQLite 3 (WAL Mode, Foreign Key Enforcement)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-sand-100">
              <span className="text-sand-500">Client Architecture:</span>
              <span className="text-sand-900">React 18 + Vite 6 + TypeScript 5</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-sand-500">API Contract:</span>
              <span className="text-sand-900">REST (POST /api/analyze, GET /health, GET /api/parts, GET /api/vehicles)</span>
            </div>
          </div>
        )}
      </section>
    </div>
  );
};
