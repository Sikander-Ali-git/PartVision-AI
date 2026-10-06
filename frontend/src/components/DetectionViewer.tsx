/**
 * frontend/src/components/DetectionViewer.tsx
 * Interactive image workspace rendering segmentation polygons and bounding boxes with 1:1 coordinate mapping.
 */

import React, { useState } from 'react';
import { Detection } from '../types/api';
import { getPartColor } from '../utils/colors';
import { Eye, EyeSlash } from '@phosphor-icons/react';

interface DetectionViewerProps {
  imageUrl: string;
  imageWidth: number;
  imageHeight: number;
  detections: Detection[];
  selectedIndex: number | null;
  hoveredIndex: number | null;
  onSelectDetection: (index: number) => void;
  onHoverDetection: (index: number | null) => void;
}

export const DetectionViewer: React.FC<DetectionViewerProps> = ({
  imageUrl,
  imageWidth,
  imageHeight,
  detections,
  selectedIndex,
  hoveredIndex,
  onSelectDetection,
  onHoverDetection,
}) => {
  const [showMasks, setShowMasks] = useState<boolean>(true);
  const [showBoxes, setShowBoxes] = useState<boolean>(true);
  const [showLabels, setShowLabels] = useState<boolean>(true);

  return (
    <div className="bg-graphite-900 border border-graphite-800 rounded-2xl p-4 shadow-lg flex flex-col">
      {/* Controls Bar */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-graphite-800 text-xs">
        <div className="flex items-center gap-2 text-graphite-300 font-mono">
          <span className="text-white font-semibold">Segmentation Canvas</span>
          <span className="text-graphite-500">|</span>
          <span>{imageWidth} × {imageHeight} px</span>
          <span className="text-graphite-500">|</span>
          <span className="text-cyan-400 font-semibold">{detections.length} Detected Instances</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowMasks(!showMasks)}
            className={`px-2.5 py-1 rounded text-xs flex items-center gap-1.5 transition ${
              showMasks
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-400/30'
                : 'bg-graphite-850 text-graphite-500 hover:text-graphite-300'
            }`}
            title="Toggle Polygons"
          >
            {showMasks ? <Eye size={14} /> : <EyeSlash size={14} />}
            <span>Masks</span>
          </button>

          <button
            onClick={() => setShowBoxes(!showBoxes)}
            className={`px-2.5 py-1 rounded text-xs flex items-center gap-1.5 transition ${
              showBoxes
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-400/30'
                : 'bg-graphite-850 text-graphite-500 hover:text-graphite-300'
            }`}
            title="Toggle Bounding Boxes"
          >
            {showBoxes ? <Eye size={14} /> : <EyeSlash size={14} />}
            <span>Boxes</span>
          </button>

          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`px-2.5 py-1 rounded text-xs flex items-center gap-1.5 transition ${
              showLabels
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-400/30'
                : 'bg-graphite-850 text-graphite-500 hover:text-graphite-300'
            }`}
            title="Toggle Labels"
          >
            {showLabels ? <Eye size={14} /> : <EyeSlash size={14} />}
            <span>Labels</span>
          </button>
        </div>
      </div>

      {/* Responsive Viewport */}
      <div className="relative w-full rounded-xl overflow-hidden bg-graphite-950 border border-graphite-800 flex items-center justify-center">
        <img
          src={imageUrl}
          alt="Vehicle under analysis"
          className="w-full h-auto max-h-[620px] object-contain block select-none pointer-events-none"
        />

        {/* Scaled SVG Annotation Layer */}
        <svg
          viewBox={`0 0 ${imageWidth} ${imageHeight}`}
          className="absolute inset-0 w-full h-full pointer-events-auto"
          preserveAspectRatio="xMidYMid meet"
        >
          {detections.map((det, idx) => {
            const color = getPartColor(det.part_name);
            const isSelected = selectedIndex === idx;
            const isHovered = hoveredIndex === idx;
            const isDimmed = (selectedIndex !== null && !isSelected) || (hoveredIndex !== null && !isHovered && selectedIndex === null);

            const maskPoints = det.mask?.points
              ? det.mask.points.map((p) => `${p[0]},${p[1]}`).join(' ')
              : null;

            return (
              <g
                key={`det-${idx}-${det.part_name}`}
                className="cursor-pointer transition-opacity duration-150"
                style={{ opacity: isDimmed ? 0.35 : 1.0 }}
                onClick={() => onSelectDetection(idx)}
                onMouseEnter={() => onHoverDetection(idx)}
                onMouseLeave={() => onHoverDetection(null)}
              >
                {/* 1. Polygon Segmentation Mask */}
                {showMasks && maskPoints && (
                  <polygon
                    points={maskPoints}
                    fill={isSelected ? color.fill.replace('0.25', '0.5') : isHovered ? color.fill.replace('0.25', '0.4') : color.fill}
                    stroke={color.hex}
                    strokeWidth={isSelected ? 3.5 : isHovered ? 2.5 : 1.5}
                    strokeLinejoin="round"
                    style={{
                      filter: isSelected ? `drop-shadow(0 0 6px ${color.hex})` : undefined,
                    }}
                  />
                )}

                {/* 2. Bounding Box */}
                {showBoxes && (
                  <rect
                    x={det.bbox.x1}
                    y={det.bbox.y1}
                    width={det.bbox.x2 - det.bbox.x1}
                    height={det.bbox.y2 - det.bbox.y1}
                    fill="none"
                    stroke={color.hex}
                    strokeWidth={isSelected ? 3 : isHovered ? 2.5 : 1.5}
                    strokeDasharray={isSelected ? undefined : '4 2'}
                  />
                )}

                {/* 3. Text Label Badge */}
                {showLabels && (
                  <g
                    transform={`translate(${det.bbox.x1 + 4}, ${Math.max(16, det.bbox.y1 + 18)})`}
                    style={{ pointerEvents: 'none' }}
                  >
                    <rect
                      x={-2}
                      y={-14}
                      width={(det.display_name.length + 7) * 7.5}
                      height={18}
                      rx={3}
                      fill="#11131a"
                      fillOpacity={0.9}
                      stroke={color.hex}
                      strokeWidth={1}
                    />
                    <text
                      x={2}
                      y={-2}
                      fill="#ffffff"
                      fontSize={10.5}
                      fontFamily="JetBrains Mono, monospace"
                      fontWeight={isSelected ? 'bold' : 'normal'}
                    >
                      {det.display_name} {(det.confidence * 100).toFixed(1)}%
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-graphite-400">
        <span>Click on any detected segment to inspect vehicular compatibility.</span>
        {selectedIndex !== null && detections[selectedIndex] && (
          <span className="text-cyan-400 font-mono">
            Selected: {detections[selectedIndex].display_name} ({(detections[selectedIndex].confidence * 100).toFixed(1)}%)
          </span>
        )}
      </div>
    </div>
  );
};
