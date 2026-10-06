/**
 * frontend/src/components/DetectionViewer.tsx
 * Precision 1:1 SVG coordinate overlay viewer for automotive segmentation and bounding boxes.
 * Prominently highlights selected detection while subduing unselected detections.
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

  const formatPoints = (points: [number, number][]): string => {
    return points.map(([x, y]) => `${x},${y}`).join(' ');
  };

  return (
    <div className="bg-white border border-sand-200 rounded-xl overflow-hidden shadow-card flex flex-col">
      {/* Viewer Controls Toolbar */}
      <div className="px-4 py-2.5 bg-sand-50 border-b border-sand-200 flex flex-wrap items-center justify-between gap-2 text-xs">
        <span className="font-medium text-sand-700">
          Inspection Overlay ({detections.length} {detections.length === 1 ? 'part' : 'parts'} detected)
        </span>

        <div className="flex items-center gap-2">
          {/* Toggle Masks */}
          <button
            type="button"
            onClick={() => setShowMasks(!showMasks)}
            className={`px-2.5 py-1 rounded border text-xs font-medium flex items-center gap-1 transition-colors ${
              showMasks
                ? 'bg-white border-sand-300 text-sand-900 shadow-subtle'
                : 'bg-sand-100 border-sand-200 text-sand-500'
            }`}
          >
            {showMasks ? <Eye size={13} /> : <EyeSlash size={13} />}
            <span>Masks</span>
          </button>

          {/* Toggle Boxes */}
          <button
            type="button"
            onClick={() => setShowBoxes(!showBoxes)}
            className={`px-2.5 py-1 rounded border text-xs font-medium flex items-center gap-1 transition-colors ${
              showBoxes
                ? 'bg-white border-sand-300 text-sand-900 shadow-subtle'
                : 'bg-sand-100 border-sand-200 text-sand-500'
            }`}
          >
            {showBoxes ? <Eye size={13} /> : <EyeSlash size={13} />}
            <span>Boxes</span>
          </button>

          {/* Toggle Labels */}
          <button
            type="button"
            onClick={() => setShowLabels(!showLabels)}
            className={`px-2.5 py-1 rounded border text-xs font-medium flex items-center gap-1 transition-colors ${
              showLabels
                ? 'bg-white border-sand-300 text-sand-900 shadow-subtle'
                : 'bg-sand-100 border-sand-200 text-sand-500'
            }`}
          >
            {showLabels ? <Eye size={13} /> : <EyeSlash size={13} />}
            <span>Labels</span>
          </button>
        </div>
      </div>

      {/* Main Image Viewport with 1:1 SVG Overlay */}
      <div className="relative w-full bg-sand-100 flex items-center justify-center p-2 sm:p-4 select-none min-h-[360px] max-h-[640px] overflow-hidden">
        <div className="relative inline-block max-w-full max-h-full">
          {/* Base Vehicle Image */}
          <img
            src={imageUrl}
            alt="Analyzed vehicle inspection view"
            className="block max-w-full max-h-[600px] w-auto h-auto object-contain rounded"
          />

          {/* Precision Scaled SVG Coordinate Plane */}
          <svg
            viewBox={`0 0 ${imageWidth} ${imageHeight}`}
            preserveAspectRatio="xMidYMid meet"
            className="absolute inset-0 w-full h-full pointer-events-none"
          >
            {/* Layer 1: Segmentation Polygon Masks */}
            {showMasks &&
              detections.map((det, index) => {
                if (!det.mask || !det.mask.points || det.mask.points.length === 0) {
                  return null;
                }

                const isSelected = selectedIndex === index;
                const isHovered = hoveredIndex === index;
                const hasSelection = selectedIndex !== null;
                const color = getPartColor(det.part_name);

                // When a detection is selected, others are visually subdued
                let fill = color.fill;
                let stroke = color.stroke;
                let strokeWidth = 1.5;
                let opacity = 1.0;

                if (isSelected) {
                  fill = 'rgba(214, 69, 45, 0.35)'; // Automotive red
                  stroke = '#D6452D';
                  strokeWidth = 3;
                } else if (isHovered) {
                  fill = 'rgba(214, 69, 45, 0.22)';
                  stroke = '#D6452D';
                  strokeWidth = 2;
                } else if (hasSelection) {
                  // Subdued when another detection is focused
                  fill = 'rgba(107, 107, 104, 0.08)';
                  stroke = 'rgba(107, 107, 104, 0.35)';
                  strokeWidth = 1;
                  opacity = 0.5;
                }

                return (
                  <polygon
                    key={`mask-${index}`}
                    points={formatPoints(det.mask.points)}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    opacity={opacity}
                    className="pointer-events-auto cursor-pointer transition-opacity duration-150"
                    onClick={() => onSelectDetection(index)}
                    onMouseEnter={() => onHoverDetection(index)}
                    onMouseLeave={() => onHoverDetection(null)}
                  />
                );
              })}

            {/* Layer 2: Bounding Boxes */}
            {showBoxes &&
              detections.map((det, index) => {
                const isSelected = selectedIndex === index;
                const isHovered = hoveredIndex === index;
                const hasSelection = selectedIndex !== null;
                const color = getPartColor(det.part_name);

                const width = Math.max(0, det.bbox.x2 - det.bbox.x1);
                const height = Math.max(0, det.bbox.y2 - det.bbox.y1);

                let stroke = color.stroke;
                let strokeWidth = 1.5;
                let opacity = 0.85;

                if (isSelected) {
                  stroke = '#D6452D';
                  strokeWidth = 2.5;
                  opacity = 1.0;
                } else if (isHovered) {
                  stroke = '#D6452D';
                  strokeWidth = 2;
                  opacity = 1.0;
                } else if (hasSelection) {
                  stroke = 'rgba(107, 107, 104, 0.3)';
                  strokeWidth = 1;
                  opacity = 0.4;
                }

                return (
                  <rect
                    key={`bbox-${index}`}
                    x={det.bbox.x1}
                    y={det.bbox.y1}
                    width={width}
                    height={height}
                    fill="none"
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    strokeDasharray={isSelected ? undefined : '4 2'}
                    opacity={opacity}
                    className="pointer-events-auto cursor-pointer"
                    onClick={() => onSelectDetection(index)}
                    onMouseEnter={() => onHoverDetection(index)}
                    onMouseLeave={() => onHoverDetection(null)}
                  />
                );
              })}

            {/* Layer 3: Tags / Labels */}
            {showLabels &&
              detections.map((det, index) => {
                const isSelected = selectedIndex === index;
                const isHovered = hoveredIndex === index;
                const hasSelection = selectedIndex !== null;

                // When something is selected, show label prominently for selected/hovered item.
                // For other items, show subdued label if no selection, or hide if another is selected.
                if (hasSelection && !isSelected && !isHovered) {
                  return null;
                }

                const labelText = `${det.display_name} ${(det.confidence * 100).toFixed(1)}%`;
                const tagX = det.bbox.x1;
                const tagY = Math.max(16, det.bbox.y1 - 4);
                const color = getPartColor(det.part_name);

                const bgFill = isSelected || isHovered ? '#D6452D' : color.stroke;

                return (
                  <g
                    key={`label-${index}`}
                    className="pointer-events-auto cursor-pointer"
                    onClick={() => onSelectDetection(index)}
                    onMouseEnter={() => onHoverDetection(index)}
                    onMouseLeave={() => onHoverDetection(null)}
                  >
                    {/* Tag Background Box */}
                    <rect
                      x={tagX}
                      y={tagY - 14}
                      width={labelText.length * 7.5 + 12}
                      height={18}
                      rx={3}
                      fill={bgFill}
                      opacity={0.95}
                    />
                    {/* Tag Text */}
                    <text
                      x={tagX + 6}
                      y={tagY - 1}
                      fill="#FFFFFF"
                      fontSize="11"
                      fontFamily="Inter, sans-serif"
                      fontWeight="600"
                    >
                      {labelText}
                    </text>
                  </g>
                );
              })}
          </svg>
        </div>
      </div>
    </div>
  );
};
