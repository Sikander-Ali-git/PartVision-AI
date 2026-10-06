/**
 * frontend/src/pages/AboutPage.tsx
 * Architecture overview, model performance metrics, dataset inventory, and trust disclosures.
 */

import React from 'react';
import {
  Cpu,
  Database,
  ShieldCheck,
  ChartBar,
  Lock,
} from '@phosphor-icons/react';

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Title Banner */}
      <div className="pb-4 border-b border-graphite-850">
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <span>PartVision AI Architecture</span>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-400/10 border border-cyan-400/30 text-cyan-400 font-mono font-medium">
            System Guide
          </span>
        </h1>
        <p className="text-sm text-graphite-400 mt-1">
          Technical specifications, dataset provenance, model metrics, and architectural trust disclosures.
        </p>
      </div>

      {/* Core Architectural Principle Banner */}
      <div className="p-5 bg-gradient-to-br from-graphite-900 to-graphite-950 border border-cyan-400/30 rounded-2xl shadow-lg relative overflow-hidden">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-400/10 border border-cyan-400/30 flex items-center justify-center text-cyan-400 flex-shrink-0">
            <ShieldCheck size={26} weight="duotone" />
          </div>
          <div className="space-y-1">
            <h2 className="text-base font-bold text-white">
              Strict Decoupling: Vision vs Compatibility
            </h2>
            <p className="text-xs sm:text-sm text-graphite-300 leading-relaxed">
              PartVision enforces a strict separation of concerns. The deep learning model identifies <em>what</em> physical part is visible in an image, while an authoritative SQLite relational database determines <em>which</em> vehicles fit that part.
            </p>
            <div className="pt-2 flex flex-wrap gap-2 text-xs font-mono">
              <span className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300">
                AI = Visual Detection Only
              </span>
              <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300">
                SQLite = Authoritative Fitment
              </span>
              <span className="px-2 py-0.5 rounded bg-graphite-850 border border-graphite-700 text-graphite-300">
                Zero Generative Hallucination
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Model & Dataset Metrics Grid */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
          <ChartBar size={16} className="text-cyan-400" />
          <span>V3 Machine Learning & Dataset Metrics</span>
        </h3>
        <p className="text-xs text-graphite-400">
          *Note: Metrics represent offline model training and validation benchmarks on held-out test splits, not runtime client performance.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
          <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-xl">
            <span className="text-xs text-graphite-400 block font-mono">Architecture</span>
            <span className="text-lg font-bold text-white font-mono">YOLO11n-seg</span>
            <span className="text-[11px] text-cyan-400 block mt-0.5">Ultralytics Instance Seg</span>
          </div>

          <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-xl">
            <span className="text-xs text-graphite-400 block font-mono">Taxonomy</span>
            <span className="text-lg font-bold text-white font-mono">19 Classes</span>
            <span className="text-[11px] text-graphite-400 block mt-0.5">Automotive Exterior</span>
          </div>

          <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-xl">
            <span className="text-xs text-graphite-400 block font-mono">Training Corpus</span>
            <span className="text-lg font-bold text-white font-mono">4,831 Images</span>
            <span className="text-[11px] text-graphite-400 block mt-0.5">35,759 Polygons</span>
          </div>

          <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-xl">
            <span className="text-xs text-graphite-400 block font-mono">Mask mAP50</span>
            <span className="text-lg font-bold text-emerald-400 font-mono">85.70%</span>
            <span className="text-[11px] text-emerald-500 block mt-0.5">Held-out V3 Val Split</span>
          </div>
        </div>
      </div>

      {/* Multi-Tiered System Architecture */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Computer Vision Card */}
        <div className="p-5 bg-graphite-900 border border-graphite-800 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-cyan-400 text-sm font-semibold">
            <Cpu size={20} weight="duotone" />
            <span>Computer Vision Layer (M6A)</span>
          </div>
          <p className="text-xs text-graphite-300 leading-relaxed">
            Wrapped by a singleton Python inference engine executed via PyTorch and Apple Silicon Metal Performance Shaders (MPS). Generates bounding boxes, pixel-aligned polygon contours, and confidence scores across 19 exterior vehicle classes.
          </p>
          <ul className="text-xs text-graphite-400 space-y-1 font-mono">
            <li>• Checkpoint: partvision_v3_yolo11n_seg_best.pt</li>
            <li>• Parameters: 2,846,313 (5.71 MB)</li>
            <li>• Average Inference: ~41 ms per image (M3)</li>
          </ul>
        </div>

        {/* Database Fitment Card */}
        <div className="p-5 bg-graphite-900 border border-graphite-800 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-electric-500 text-sm font-semibold">
            <Database size={20} weight="duotone" />
            <span>Relational Compatibility Layer (M6B)</span>
          </div>
          <p className="text-xs text-graphite-300 leading-relaxed">
            Operates on an ACID-compliant SQLite 3 database in Write-Ahead Logging (WAL) mode. Maps canonical parts to high-volume production vehicles with explicit provenance, source attribution, and OEM manual citations.
          </p>
          <ul className="text-xs text-graphite-400 space-y-1 font-mono">
            <li>• Target: data/partvision.db (WAL Mode)</li>
            <li>• Seeded Vehicles: 8 Indian Market Models</li>
            <li>• Verified Records: 48 OEM Cross-References</li>
          </ul>
        </div>
      </div>

      {/* Safety & Compliance Guarantees */}
      <div className="p-5 bg-graphite-900 border border-graphite-800 rounded-2xl space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Lock size={18} className="text-cyan-400" />
          <span>Product Safety & Technical Constraints</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-graphite-300">
          <div className="p-3 bg-graphite-950 rounded-xl border border-graphite-850 space-y-1">
            <span className="font-semibold text-white block">No In-Memory Retention</span>
            <p className="text-graphite-400 text-[11px]">
              Uploaded vehicle images are discarded immediately after inference completion.
            </p>
          </div>

          <div className="p-3 bg-graphite-950 rounded-xl border border-graphite-850 space-y-1">
            <span className="font-semibold text-white block">Transparent Provenance</span>
            <p className="text-graphite-400 text-[11px]">
              Every fitment match cites manufacturer catalogs (MSGP, Hyundai Mobis, Honda Access).
            </p>
          </div>

          <div className="p-3 bg-graphite-950 rounded-xl border border-graphite-850 space-y-1">
            <span className="font-semibold text-white block">Isolated Verification</span>
            <p className="text-graphite-400 text-[11px]">
              Demonstration or aftermarket data is strictly quarantined from verified OEM records.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
