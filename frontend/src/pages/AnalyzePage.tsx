/**
 * frontend/src/pages/AnalyzePage.tsx
 * Primary automotive image analysis workspace with visual segmentation and compatibility panels.
 */

import React from 'react';
import { useAnalysis } from '../hooks/useAnalysis';
import { ImageUploader } from '../components/ImageUploader';
import { DetectionViewer } from '../components/DetectionViewer';
import { DetectionList } from '../components/DetectionList';
import { CompatibilityPanel } from '../components/CompatibilityPanel';
import { SummaryPanel } from '../components/SummaryPanel';
import { ShieldCheck, Car } from '@phosphor-icons/react';

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
    result && selectedDetectionIndex !== null
      ? result.detections[selectedDetectionIndex] || null
      : null;

  return (
    <div className="space-y-6">
      {/* Top Banner / Heading */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-2 border-b border-graphite-850">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Automotive Vision Intelligence</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-400/10 border border-cyan-400/30 text-cyan-400 font-mono font-medium">
              V3 Model
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-graphite-400 mt-1">
            Segment 19 exterior body parts and query verified vehicular compatibility.
          </p>
        </div>

        {result && (
          <div className="flex items-center gap-2 text-xs font-mono text-graphite-400">
            <span>Req ID:</span>
            <span className="text-cyan-400 bg-graphite-900 border border-graphite-800 px-2 py-1 rounded truncate max-w-[140px] sm:max-w-[200px]">
              {result.request_id}
            </span>
          </div>
        )}
      </div>

      {/* Summary KPI Panel (When Results Available) */}
      {result && <SummaryPanel result={result} />}

      {/* Main Analysis Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (Upload & Detection Canvas) */}
        <div className="lg:col-span-7 space-y-6">
          <ImageUploader
            selectedFile={selectedFile}
            previewUrl={previewUrl}
            isAnalyzing={isAnalyzing}
            error={error}
            onFileSelected={selectFile}
            onClear={clearSelection}
            onAnalyze={runAnalysis}
          />

          {/* Interactive Segmentation Viewer */}
          {result && previewUrl && (
            <DetectionViewer
              imageUrl={previewUrl}
              imageWidth={result.image.width}
              imageHeight={result.image.height}
              detections={result.detections}
              selectedIndex={selectedDetectionIndex}
              hoveredIndex={hoveredDetectionIndex}
              onSelectDetection={setSelectedDetectionIndex}
              onHoverDetection={setHoveredDetectionIndex}
            />
          )}

          {/* Static Preview when file selected but not analyzed yet */}
          {!result && previewUrl && (
            <div className="bg-graphite-900 border border-graphite-800 rounded-2xl p-4 shadow-lg text-center">
              <h3 className="text-xs font-semibold text-graphite-400 uppercase tracking-wider mb-2 font-mono">
                Image Preview
              </h3>
              <div className="rounded-xl overflow-hidden bg-graphite-950 border border-graphite-800 flex items-center justify-center max-h-[500px]">
                <img
                  src={previewUrl}
                  alt="Selected vehicle"
                  className="max-h-[500px] w-auto object-contain"
                />
              </div>
            </div>
          )}
        </div>

        {/* Right Column (Detection List & Compatibility Panel) */}
        <div className="lg:col-span-5 space-y-6">
          {result ? (
            <>
              {/* Detection Cards List */}
              <DetectionList
                detections={result.detections}
                selectedIndex={selectedDetectionIndex}
                hoveredIndex={hoveredDetectionIndex}
                onSelectDetection={setSelectedDetectionIndex}
                onHoverDetection={setHoveredDetectionIndex}
              />

              {/* Vehicle Compatibility Breakdown */}
              <CompatibilityPanel detection={selectedDetection} />
            </>
          ) : (
            /* Clean Empty State */
            <div className="bg-graphite-900 border border-graphite-800 rounded-2xl p-6 sm:p-8 shadow-lg text-center space-y-5">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-cyan-950/30 border border-cyan-800/40 flex items-center justify-center text-cyan-400 shadow-glow-cyan/20">
                <Car size={32} weight="duotone" />
              </div>

              <div>
                <h3 className="text-base font-bold text-white">
                  Awaiting Vehicle Image
                </h3>
                <p className="text-xs text-graphite-400 mt-1 max-w-sm mx-auto leading-relaxed">
                  Upload an exterior photograph above and click <span className="text-cyan-400 font-semibold">Analyze Parts</span> to identify visible spare parts and check vehicular compatibility.
                </p>
              </div>

              <div className="pt-4 border-t border-graphite-800/80 text-left space-y-3">
                <h4 className="text-xs font-semibold text-graphite-300 flex items-center gap-1.5 font-mono">
                  <ShieldCheck size={14} className="text-cyan-400" />
                  <span>Authoritative Fitment Pipeline</span>
                </h4>
                <ul className="text-xs text-graphite-400 space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 font-bold">•</span>
                    <span><strong>Computer Vision:</strong> YOLO11n-seg segments bumpers, doors, lights, glass, fenders, wheels, mirrors, and hoods.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 font-bold">•</span>
                    <span><strong>Relational Database:</strong> SQLite maps canonical parts to verified vehicle catalogs with zero AI hallucination.</span>
                  </li>
                </ul>
              </div>

              <div className="p-3 bg-graphite-850 rounded-xl border border-graphite-800 text-[11px] text-graphite-400 text-center font-mono">
                19 Classes • 8 Representative Indian Vehicles • 51 Fitment Records
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
