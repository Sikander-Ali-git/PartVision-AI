/**
 * frontend/src/components/DetectionList.tsx
 * Lists all detected physical part instances with confidence scores and selection triggers.
 */

import React from 'react';
import { Detection } from '../types/api';
import { getPartColor } from '../utils/colors';
import { CheckCircle, ShieldCheck } from '@phosphor-icons/react';

interface DetectionListProps {
  detections: Detection[];
  selectedIndex: number | null;
  hoveredIndex: number | null;
  onSelectDetection: (index: number) => void;
  onHoverDetection: (index: number | null) => void;
}

export const DetectionList: React.FC<DetectionListProps> = ({
  detections,
  selectedIndex,
  hoveredIndex,
  onSelectDetection,
  onHoverDetection,
}) => {
  return (
    <div className="bg-graphite-900 border border-graphite-800 rounded-2xl p-4 shadow-lg flex flex-col">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-graphite-800">
        <div>
          <h3 className="text-sm font-semibold text-white">Detected Parts</h3>
          <p className="text-xs text-graphite-400">
            {detections.length} individual instances identified
          </p>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800 px-2 py-0.5 rounded">
          Conf: 25%–100%
        </span>
      </div>

      <div className="space-y-2 overflow-y-auto max-h-[380px] pr-1">
        {detections.map((det, idx) => {
          const color = getPartColor(det.part_name);
          const isSelected = selectedIndex === idx;
          const isHovered = hoveredIndex === idx;
          const pct = (det.confidence * 100).toFixed(1);
          const verifiedCount = det.compatibility.verified_vehicles.length;

          return (
            <div
              key={`card-${idx}-${det.part_name}`}
              onClick={() => onSelectDetection(idx)}
              onMouseEnter={() => onHoverDetection(idx)}
              onMouseLeave={() => onHoverDetection(null)}
              className={`p-3 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'bg-graphite-850 border-cyan-400 shadow-glow-cyan/30'
                  : isHovered
                  ? 'bg-graphite-850 border-graphite-700'
                  : 'bg-graphite-950/70 border-graphite-800 hover:border-graphite-700'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: color.hex }}
                  />
                  <div>
                    <h4 className="text-sm font-semibold text-white leading-tight">
                      {det.display_name}
                    </h4>
                    <span className="text-xs text-graphite-400 font-mono">
                      #{idx + 1} • {det.part_name}
                    </span>
                  </div>
                </div>

                {/* Detection Confidence Badge */}
                <div className="text-right">
                  <span className="inline-block px-2 py-0.5 rounded bg-graphite-800 border border-graphite-700 text-cyan-400 font-mono text-xs font-medium">
                    {pct}%
                  </span>
                  <p className="text-[10px] text-graphite-500 mt-0.5">Detection Conf.</p>
                </div>
              </div>

              {/* Fitment Status Preview */}
              <div className="mt-2.5 pt-2 border-t border-graphite-800/80 flex items-center justify-between text-xs text-graphite-400">
                <span className="flex items-center gap-1">
                  <CheckCircle size={13} className="text-emerald-400" />
                  <span>Detected</span>
                </span>

                <span className="flex items-center gap-1 font-mono text-graphite-300">
                  <ShieldCheck size={13} className="text-cyan-400" />
                  <span>{verifiedCount} Verified Fitment{verifiedCount === 1 ? '' : 's'}</span>
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
