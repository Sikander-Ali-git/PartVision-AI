/**
 * frontend/src/hooks/useAnalysis.ts
 * Manages image selection, validation, API analysis submission, and detection selection states.
 */

import { useState, useCallback, useEffect } from 'react';
import { api, ApiServiceError } from '../services/api';
import { AnalysisResult } from '../types/api';

const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const ALLOWED_EXTS = ['.jpg', '.jpeg', '.png', '.webp'];

export function useAnalysis() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedDetectionIndex, setSelectedDetectionIndex] = useState<number | null>(null);
  const [hoveredDetectionIndex, setHoveredDetectionIndex] = useState<number | null>(null);

  // Clean up object URLs on unmount or file change
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const selectFile = useCallback((file: File) => {
    setError(null);

    // 1. Validate file extension & mime type
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    const isValidExt = ALLOWED_EXTS.includes(ext);
    const isValidType = ALLOWED_TYPES.includes(file.type.toLowerCase()) || isValidExt;

    if (!isValidType) {
      setError(`Unsupported file type "${file.name}". Supported formats: JPEG, PNG, WEBP.`);
      return false;
    }

    // 2. Validate maximum file size
    if (file.size > MAX_FILE_SIZE_BYTES) {
      const sizeMb = (file.size / (1024 * 1024)).toFixed(1);
      setError(`File size (${sizeMb} MB) exceeds maximum allowed limit of 20 MB.`);
      return false;
    }

    // Revoke old URL if existing
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const objectUrl = URL.createObjectURL(file);
    setSelectedFile(file);
    setPreviewUrl(objectUrl);
    setResult(null);
    setSelectedDetectionIndex(null);
    setHoveredDetectionIndex(null);
    return true;
  }, [previewUrl]);

  const clearSelection = useCallback(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setSelectedDetectionIndex(null);
    setHoveredDetectionIndex(null);
  }, [previewUrl]);

  const runAnalysis = useCallback(async () => {
    if (!selectedFile) {
      setError('Please select an automotive photograph to analyze.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const analysisData = await api.analyzeImage(selectedFile);
      setResult(analysisData);
      if (analysisData.detections.length > 0) {
        setSelectedDetectionIndex(0);
      } else {
        setSelectedDetectionIndex(null);
      }
    } catch (err: unknown) {
      if (err instanceof ApiServiceError) {
        if (err.status === 413) {
          setError('Image file is too large (exceeds 20MB limit).');
        } else if (err.status === 415) {
          setError('Unsupported media type. Please provide a JPEG, PNG, or WEBP image.');
        } else if (err.status === 400) {
          setError(`Invalid image payload: ${err.message}`);
        } else if (err.status >= 500) {
          setError('Internal server analysis failure. Please verify backend logs.');
        } else {
          setError(`Analysis request failed: ${err.message}`);
        }
      } else if (err instanceof Error) {
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          setError('PartVision API is unavailable. Make sure the backend is running on port 8000.');
        } else {
          setError(`Unexpected error: ${err.message}`);
        }
      } else {
        setError('An unexpected error occurred while communicating with the analysis server.');
      }
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile]);

  return {
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
  };
}
