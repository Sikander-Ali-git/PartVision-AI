/**
 * frontend/src/pages/AnalyzePage.tsx
 * Primary automotive part identification and compatibility analysis workspace.
 * Follows the core workflow: Upload -> Analyze -> See Detections -> Select Part -> Inspect Verified Fitment.
 */

import React from 'react';
import { useAnalysis } from '../hooks/useAnalysis';
import { ImageUploader } from '../components/ImageUploader';
import { DetectionViewer } from '../components/DetectionViewer';
import { DetectionList } from '../components/DetectionList';
import { CompatibilityPanel } from '../components/CompatibilityPanel';
import { ArrowClockwise, CheckCircle } from '@phosphor-icons/react';

export const AnalyzePage: React.FC = () => {
  const {
    selectedFile,
    previewUrl,
    isAnalyzing,
    result,
    error,
    selectedDetectionIndex,
    hoveredDetectionIndex,
    selectFile,
    clearSelection,
    runAnalysis,
    setSelectedDetectionIndex,
    setHoveredDetectionIndex,
  } = useAnalysis();

  const selectedDetection =
    result && selectedDetectionIndex !== null ? result.detections[selectedDetectionIndex] : null;

  // Compute distinct part types and verified count
  const detectionCount = result?.detections.length || 0;
  const uniquePartTypes = result?.summary.detected_parts.length || 0;
  const verifiedFitmentAvailable =
    result?.detections.some(
      (d) => d.compatibility.verified_vehicles && d.compatibility.verified_vehicles.length > 0
    ) || false;

  return (
    <div className="space-y-6">
      {/* State 1: No Analysis Result Yet (Upload / Initial State) */}
      {!result ? (
        <div className="max-w-2xl mx-auto py-6 sm:py-10 space-y-8">
          {/* Focused Page Heading */}
          <div className="text-center space-y-2">
            <h1 className="text-2xl sm:text-3xl font-bold text-sand-900 tracking-tight">
              Identify an automotive part
            </h1>
            <p className="text-sm text-sand-500 max-w-lg mx-auto">
              Upload a vehicle image to identify visible components and check verified fitment.
            </p>
          </div>

          {/* Primary Upload Target */}
          <ImageUploader
            selectedFile={selectedFile}
            previewUrl={previewUrl}
            isAnalyzing={isAnalyzing}
            error={error}
            onFileSelected={selectFile}
            onClear={clearSelection}
            onAnalyze={runAnalysis}
          />
        </div>
      ) : (
        /* State 2: Active Analysis Workspace (Two-Column Layout) */
        <div className="space-y-4">
          {/* Workspace Action & Summary Header */}
          <div className="bg-white border border-sand-200 rounded-xl px-5 py-3.5 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-sand-900">
                  Analysis Results
                </h2>
                <span className="text-xs font-mono text-sand-500">
                  · {result.inference.latency_ms.toFixed(0)} ms
                </span>
              </div>

              {/* Compact Technical Summary */}
              <div className="flex flex-wrap items-center gap-2 text-xs text-sand-600 mt-1 font-mono">
                <span>{detectionCount} detections</span>
                <span>·</span>
                <span>{uniquePartTypes} unique part types</span>
                {verifiedFitmentAvailable && (
                  <>
                    <span>·</span>
                    <span className="text-auto-green-600 font-medium inline-flex items-center gap-1">
                      <CheckCircle size={13} weight="bold" />
                      Verified fitment available
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Action to Analyze Another Image */}
            <button
              type="button"
              onClick={clearSelection}
              className="px-3.5 py-1.5 text-xs font-medium text-sand-700 bg-white border border-sand-300 hover:bg-sand-50 rounded-lg shadow-subtle transition-colors flex items-center justify-center gap-1.5 self-start sm:self-center"
            >
              <ArrowClockwise size={14} />
              <span>Analyze another image</span>
            </button>
          </div>

          {/* Dual-Column Analysis Workspace */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* LEFT COLUMN: Large Image Viewer (Receives Largest Visual Priority) */}
            <div className="lg:col-span-7 xl:col-span-8">
              <DetectionViewer
                imageUrl={previewUrl || ''}
                imageWidth={result.image.width}
                imageHeight={result.image.height}
                detections={result.detections}
                selectedIndex={selectedDetectionIndex}
                hoveredIndex={hoveredDetectionIndex}
                onSelectDetection={setSelectedDetectionIndex}
                onHoverDetection={setHoveredDetectionIndex}
              />
            </div>

            {/* RIGHT COLUMN: Technical Detection List & Selected Part Fitment */}
            <div className="lg:col-span-5 xl:col-span-4 space-y-4">
              <DetectionList
                detections={result.detections}
                selectedIndex={selectedDetectionIndex}
                onSelectDetection={setSelectedDetectionIndex}
                onHoverDetection={setHoveredDetectionIndex}
              />

              <CompatibilityPanel detection={selectedDetection} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
