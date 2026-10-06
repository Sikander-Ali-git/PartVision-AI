/**
 * frontend/src/components/ImageUploader.tsx
 * Drag-and-drop file uploader with validation, preview, and analysis trigger.
 */

import React, { useRef, useState } from 'react';
import { UploadSimple, FileImage, X, SpinnerGap, Sparkle, WarningCircle } from '@phosphor-icons/react';

interface ImageUploaderProps {
  selectedFile: File | null;
  previewUrl: string | null;
  isAnalyzing: boolean;
  error: string | null;
  onFileSelected: (file: File) => void;
  onClear: () => void;
  onAnalyze: () => void;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  selectedFile,
  previewUrl,
  isAnalyzing,
  error,
  onFileSelected,
  onClear,
  onAnalyze,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  return (
    <div className="bg-graphite-900 border border-graphite-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <FileImage size={18} className="text-cyan-400" />
            <span>Vehicle Image Workspace</span>
          </h2>
          <p className="text-xs text-graphite-400">
            Upload an exterior vehicle photograph (JPEG, PNG, WEBP up to 20MB)
          </p>
        </div>

        {selectedFile && !isAnalyzing && (
          <button
            onClick={onClear}
            className="flex items-center gap-1 text-xs text-graphite-400 hover:text-rose-400 px-2 py-1 rounded hover:bg-graphite-850 transition"
          >
            <X size={14} />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Upload Zone or Preview */}
      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 ${
            isDragOver
              ? 'border-cyan-400 bg-cyan-950/20 shadow-glow-cyan'
              : 'border-graphite-700 hover:border-graphite-600 bg-graphite-950/50 hover:bg-graphite-850/50'
          }`}
        >
          <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-graphite-850 border border-graphite-700 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform">
            <UploadSimple size={28} weight="duotone" />
          </div>
          <p className="text-sm font-medium text-white mb-1">
            Drag and drop vehicle photograph here, or <span className="text-cyan-400 underline">browse</span>
          </p>
          <p className="text-xs text-graphite-500">
            Supports JPEG, PNG, WEBP (Max 20 MB)
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {previewUrl && (
            <div className="relative w-full h-40 rounded-xl overflow-hidden border border-graphite-800 bg-graphite-950 flex items-center justify-center">
              <img src={previewUrl} alt="Upload preview thumbnail" className="h-full w-full object-contain" />
            </div>
          )}

          {/* File Meta Pill */}
          <div className="flex items-center justify-between p-3 bg-graphite-850 rounded-xl border border-graphite-800 text-xs">
            <div className="flex items-center gap-2 overflow-hidden">
              <FileImage size={18} className="text-cyan-400 flex-shrink-0" />
              <span className="font-mono text-white truncate max-w-xs">{selectedFile.name}</span>
              <span className="text-graphite-400 font-mono">({formatFileSize(selectedFile.size)})</span>
            </div>
            <span className="text-xs text-cyan-400 font-mono">Ready to Analyze</span>
          </div>

          {/* Action Trigger */}
          <button
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className={`w-full py-3 px-4 rounded-xl font-medium text-sm flex items-center justify-center gap-2 transition-all ${
              isAnalyzing
                ? 'bg-graphite-800 text-graphite-400 cursor-not-allowed border border-graphite-700'
                : 'bg-gradient-to-r from-cyan-500 to-electric-500 hover:from-cyan-400 hover:to-electric-400 text-graphite-950 font-semibold shadow-glow-cyan/50 hover:shadow-glow-cyan'
            }`}
          >
            {isAnalyzing ? (
              <>
                <SpinnerGap size={18} className="animate-spin text-cyan-400" />
                <span className="text-white">Analyzing vehicle image...</span>
              </>
            ) : (
              <>
                <Sparkle size={18} weight="fill" />
                <span>Analyze Parts & Check Fitment</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Error Message Banner */}
      {error && (
        <div className="mt-4 p-3 bg-rose-950/30 border border-rose-800/60 rounded-xl flex items-start gap-2.5 text-xs text-rose-300">
          <WarningCircle size={18} weight="fill" className="text-rose-400 flex-shrink-0 mt-0.5" />
          <p className="flex-1 leading-relaxed">{error}</p>
        </div>
      )}
    </div>
  );
};
