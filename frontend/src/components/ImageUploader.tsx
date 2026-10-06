/**
 * frontend/src/components/ImageUploader.tsx
 * Professional automotive image upload and inspection component.
 */

import React, { useState, useRef } from 'react';
import { UploadSimple, FileImage, SpinnerGap, ArrowClockwise, WarningCircle } from '@phosphor-icons/react';

interface ImageUploaderProps {
  selectedFile: File | null;
  previewUrl: string | null;
  isAnalyzing: boolean;
  error: string | null;
  onFileSelected: (file: File) => void;
  onClear: () => void;
  onAnalyze: () => void;
}

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20 MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

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
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const validateAndSelect = (file: File) => {
    setValidationError(null);

    if (!ALLOWED_TYPES.includes(file.type.toLowerCase())) {
      setValidationError('Please select a valid image file (JPG, PNG, or WEBP).');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setValidationError(
        `Image size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds the 20 MB maximum limit.`
      );
      return;
    }

    onFileSelected(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSelect(e.target.files[0]);
    }
  };

  const activeError = validationError || error;

  return (
    <div className="bg-white border border-sand-200 rounded-xl p-6 shadow-card">
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileChange}
        className="hidden"
        aria-label="Upload automotive image"
      />

      {/* Upload Box / Drag Target */}
      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-10 sm:p-14 text-center cursor-pointer transition-colors duration-150 ${
            isDragOver
              ? 'border-auto-red-500 bg-auto-red-50/50'
              : 'border-sand-300 hover:border-sand-400 bg-sand-50/50 hover:bg-sand-100/50'
          }`}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              fileInputRef.current?.click();
            }
          }}
          aria-label="Click or drag image to upload"
        >
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-white border border-sand-200 flex items-center justify-center text-sand-600 shadow-subtle">
            <UploadSimple size={24} />
          </div>

          <p className="text-sm font-semibold text-sand-900 mb-1">
            Drop image here, or <span className="text-auto-red-500 underline">browse files</span>
          </p>

          <p className="text-xs text-sand-500">
            JPG · PNG · WEBP · Maximum 20 MB
          </p>
        </div>
      ) : (
        /* Selected State with Image Preview & Controls */
        <div className="space-y-4">
          {/* Large Image Preview Container */}
          <div className="relative w-full rounded-lg border border-sand-200 bg-sand-100 overflow-hidden flex items-center justify-center max-h-[420px]">
            {previewUrl && (
              <img
                src={previewUrl}
                alt="Selected vehicle preview"
                className="w-full h-auto max-h-[420px] object-contain"
              />
            )}

            {/* Restrained Loading Indicator Overlay */}
            {isAnalyzing && (
              <div className="absolute inset-0 bg-white/80 backdrop-blur-[2px] flex flex-col items-center justify-center gap-3">
                <SpinnerGap size={32} className="animate-spin text-auto-red-500" />
                <p className="text-sm font-medium text-sand-900">
                  Analyzing image...
                </p>
              </div>
            )}
          </div>

          {/* File Metadata Bar */}
          <div className="flex items-center justify-between py-2 px-3 bg-sand-50 rounded-lg border border-sand-200 text-xs">
            <div className="flex items-center gap-2 overflow-hidden">
              <FileImage size={18} className="text-sand-500 flex-shrink-0" />
              <span className="font-medium text-sand-900 truncate max-w-xs">{selectedFile.name}</span>
              <span className="text-sand-500">({formatFileSize(selectedFile.size)})</span>
            </div>

            <button
              onClick={() => {
                setValidationError(null);
                onClear();
              }}
              disabled={isAnalyzing}
              className="text-xs text-sand-600 hover:text-auto-rose-600 disabled:opacity-50 transition-colors"
            >
              Remove
            </button>
          </div>

          {/* Actions Bar */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isAnalyzing}
              className="px-4 py-2 text-sm font-medium text-sand-700 bg-white border border-sand-300 hover:bg-sand-50 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1.5"
            >
              <ArrowClockwise size={16} />
              <span>Change image</span>
            </button>

            <button
              type="button"
              onClick={onAnalyze}
              disabled={isAnalyzing}
              className="px-6 py-2 text-sm font-semibold text-white bg-auto-red-500 hover:bg-auto-red-600 active:bg-auto-red-700 rounded-lg shadow-subtle transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <SpinnerGap size={18} className="animate-spin" />
                  <span>Analyzing image...</span>
                </>
              ) : (
                <span>Analyze image</span>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Validation or API Error Banner */}
      {activeError && (
        <div className="mt-4 p-3 bg-auto-rose-50 border border-auto-rose-200 rounded-lg flex items-start gap-2 text-xs text-auto-rose-700">
          <WarningCircle size={16} className="flex-shrink-0 mt-0.5 text-auto-rose-600" />
          <div className="flex-1">
            <p className="font-semibold">{activeError}</p>
            <p className="text-sand-600 mt-0.5">Please provide a clear automotive exterior image under 20 MB.</p>
          </div>
        </div>
      )}
    </div>
  );
};
