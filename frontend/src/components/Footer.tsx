/**
 * frontend/src/components/Footer.tsx
 * Footer component highlighting architecture, model version, and trust principles.
 */

import React from 'react';
import { Cpu, Database, CheckCircle } from '@phosphor-icons/react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-graphite-950 border-t border-graphite-800 text-graphite-400 text-xs py-8 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-semibold text-graphite-100 tracking-wider">PARTVISION AI</span>
            <span className="text-graphite-600">|</span>
            <span>Frozen YOLO11n-seg V3 Model</span>
            <span className="text-graphite-600">|</span>
            <span>19 Canonical Classes</span>
          </div>

          <div className="flex items-center gap-4 text-graphite-400">
            <div className="flex items-center gap-1.5">
              <Cpu size={15} className="text-cyan-400" />
              <span>Vision Identification</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Database size={15} className="text-electric-500" />
              <span>SQLite Fitment Engine</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle size={15} className="text-emerald-400" />
              <span>Zero LLM Hallucination</span>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-graphite-900 text-center text-graphite-500">
          PartVision AI uses computer vision to identify the visible part. Compatibility is retrieved from the structured fitment database.
        </div>
      </div>
    </footer>
  );
};
