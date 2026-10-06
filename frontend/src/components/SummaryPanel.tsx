/**
 * frontend/src/components/SummaryPanel.tsx
 * Top metrics panel displaying detection counts, confidence peaks, and hardware latency.
 */

import React from 'react';
import { AnalysisResult } from '../types/api';
import { Car, Tag, Sparkle, ShieldCheck, Lightning } from '@phosphor-icons/react';

interface SummaryPanelProps {
  result: AnalysisResult;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ result }) => {
  const { detections, summary, inference } = result;

  // Compute highest confidence directly from detections
  const highestConfidence = detections.length > 0
    ? Math.max(...detections.map((d) => d.confidence))
    : 0;

  // Compute total verified compatibility matches across all detected parts
  const totalVerifiedMatches = detections.reduce(
    (acc, det) => acc + det.compatibility.verified_vehicles.length,
    0
  );

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      {/* 1. Total Detected Parts */}
      <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-2xl shadow-sm">
        <div className="flex items-center gap-2 text-graphite-400 text-xs mb-1">
          <Car size={16} className="text-cyan-400" />
          <span>Detected Instances</span>
        </div>
        <div className="text-2xl font-bold font-mono text-white">
          {summary.detection_count}
        </div>
        <p className="text-[11px] text-graphite-500 mt-1">Physical components</p>
      </div>

      {/* 2. Unique Part Types */}
      <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-2xl shadow-sm">
        <div className="flex items-center gap-2 text-graphite-400 text-xs mb-1">
          <Tag size={16} className="text-electric-500" />
          <span>Unique Part Types</span>
        </div>
        <div className="text-2xl font-bold font-mono text-white">
          {summary.detected_parts.length}
        </div>
        <p className="text-[11px] text-graphite-500 mt-1">Taxonomy classes</p>
      </div>

      {/* 3. Highest Confidence */}
      <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-2xl shadow-sm">
        <div className="flex items-center gap-2 text-graphite-400 text-xs mb-1">
          <Sparkle size={16} className="text-amber-400" weight="fill" />
          <span>Top Confidence</span>
        </div>
        <div className="text-2xl font-bold font-mono text-cyan-400">
          {(highestConfidence * 100).toFixed(1)}%
        </div>
        <p className="text-[11px] text-graphite-500 mt-1">YOLO segmentation</p>
      </div>

      {/* 4. Verified Compatibility */}
      <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-2xl shadow-sm">
        <div className="flex items-center gap-2 text-graphite-400 text-xs mb-1">
          <ShieldCheck size={16} className="text-emerald-400" weight="fill" />
          <span>Verified Fitments</span>
        </div>
        <div className="text-2xl font-bold font-mono text-emerald-400">
          {totalVerifiedMatches}
        </div>
        <p className="text-[11px] text-graphite-500 mt-1">OEM catalog matches</p>
      </div>

      {/* 5. Latency & Hardware */}
      <div className="p-4 bg-graphite-900 border border-graphite-800 rounded-2xl shadow-sm col-span-2 sm:col-span-1">
        <div className="flex items-center gap-2 text-graphite-400 text-xs mb-1">
          <Lightning size={16} className="text-yellow-400" weight="fill" />
          <span>Pipeline Latency</span>
        </div>
        <div className="text-2xl font-bold font-mono text-white">
          {inference.total_pipeline_ms ? `${Math.round(inference.total_pipeline_ms)} ms` : `${Math.round(inference.latency_ms)} ms`}
        </div>
        <p className="text-[11px] text-graphite-500 mt-1">
          Device: <span className="text-cyan-400 uppercase font-mono">{inference.device}</span> ({inference.latency_ms.toFixed(0)}ms model)
        </p>
      </div>
    </div>
  );
};
