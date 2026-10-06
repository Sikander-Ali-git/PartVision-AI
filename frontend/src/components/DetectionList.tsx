/**
 * frontend/src/components/DetectionList.tsx
 * Clean, technical list of detected automotive parts.
 * Features compact rows, distinct duplicate handling, and clear selection states.
 */

import React from 'react';
import { Detection } from '../types/api';
import { CheckCircle } from '@phosphor-icons/react';

interface DetectionListProps {
  detections: Detection[];
  selectedIndex: number | null;
  onSelectDetection: (index: number) => void;
  onHoverDetection: (index: number | null) => void;
}

export const DetectionList: React.FC<DetectionListProps> = ({
  detections,
  selectedIndex,
  onSelectDetection,
  onHoverDetection,
}) => {
  if (detections.length === 0) {
    return (
      <div className="p-4 bg-sand-50 rounded-lg border border-sand-200 text-center text-xs text-sand-500">
        No components detected in this image.
      </div>
    );
  }

  return (
    <div className="bg-white border border-sand-200 rounded-xl overflow-hidden shadow-card">
      <div className="px-4 py-3 border-b border-sand-200 bg-sand-50 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-sand-900">
            Detected Components ({detections.length})
          </h3>
          <p className="text-[11px] text-sand-500">
            Select a row to focus on image and view verified vehicular compatibility
          </p>
        </div>
      </div>

      <div className="divide-y divide-sand-200 max-h-72 overflow-y-auto" role="listbox" aria-label="Detected parts list">
        {detections.map((det, index) => {
          const isSelected = selectedIndex === index;
          const hasVerified =
            det.compatibility &&
            det.compatibility.verified_vehicles &&
            det.compatibility.verified_vehicles.length > 0;

          const verifiedCount = det.compatibility?.verified_vehicles?.length || 0;

          return (
            <button
              key={`det-item-${index}`}
              type="button"
              onClick={() => onSelectDetection(index)}
              onMouseEnter={() => onHoverDetection(index)}
              onMouseLeave={() => onHoverDetection(null)}
              className={`w-full text-left px-4 py-2.5 flex items-center justify-between gap-3 transition-colors ${
                isSelected
                  ? 'bg-auto-red-50 text-sand-900 border-l-4 border-auto-red-500'
                  : 'hover:bg-sand-50 text-sand-800'
              }`}
              role="option"
              aria-selected={isSelected}
            >
              <div className="flex items-center gap-2.5 overflow-hidden">
                <span className="text-xs font-mono text-sand-400 w-4 text-right flex-shrink-0">
                  {index + 1}
                </span>

                <div className="truncate">
                  <div className="text-sm font-medium text-sand-900 truncate">
                    {det.display_name}
                  </div>
                  <div className="text-[11px] font-mono text-sand-500">
                    {det.part_name}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 flex-shrink-0">
                {/* Fitment Indicator Badge */}
                {hasVerified ? (
                  <span
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-auto-green-50 text-auto-green-600 border border-auto-green-100 text-[11px] font-medium"
                    title={`${verifiedCount} verified OEM vehicle fitments`}
                  >
                    <CheckCircle size={12} weight="bold" />
                    <span>{verifiedCount} Verified</span>
                  </span>
                ) : (
                  <span className="text-[11px] text-sand-400">
                    No fitment
                  </span>
                )}

                {/* Model Confidence Score */}
                <div className="text-right min-w-[50px]">
                  <div
                    className="text-xs font-mono font-semibold text-sand-900"
                    title="Model detection confidence"
                  >
                    {(det.confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-sand-500">
                    Confidence
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
