/**
 * frontend/src/services/api.ts
 * Centralized API client service connecting to PartVision AI FastAPI backend (Milestone 7 / 8).
 */

import {
  HealthStatus,
  AnalysisResult,
  Part,
  PartDetail,
  Vehicle,
  VehicleDetail,
  CompatibilityResult,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

class ApiServiceError extends Error {
  status: number;
  errorType: string;

  constructor(status: number, errorType: string, message: string) {
    super(message);
    this.name = 'ApiServiceError';
    this.status = status;
    this.errorType = errorType;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    let errorType = 'HttpError';

    try {
      const errJson = await response.json();
      if (errJson && typeof errJson === 'object') {
        errorType = errJson.error || errorType;
        errorDetail = errJson.detail || errorDetail;
      }
    } catch {
      // Body not JSON
    }

    throw new ApiServiceError(response.status, errorType, errorDetail);
  }

  return response.json() as Promise<T>;
}

export const api = {
  /**
   * Health and connectivity check.
   */
  async healthCheck(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE_URL}/health`);
    return handleResponse<HealthStatus>(res);
  },

  /**
   * Uploads an image file to POST /api/analyze for YOLO segmentation and compatibility matching.
   */
  async analyzeImage(file: File): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });

    return handleResponse<AnalysisResult>(res);
  },

  /**
   * Lists all 19 canonical parts with optional filtering.
   */
  async getParts(category?: string, search?: string): Promise<Part[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);

    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE_URL}/api/parts${query}`);
    return handleResponse<Part[]>(res);
  },

  /**
   * Retrieves full details, aliases, and compatibility for a specific part.
   */
  async getPart(partName: string): Promise<PartDetail> {
    const res = await fetch(`${API_BASE_URL}/api/parts/${encodeURIComponent(partName)}`);
    return handleResponse<PartDetail>(res);
  },

  /**
   * Lists all vehicles with optional make and model filtering.
   */
  async getVehicles(make?: string, model?: string): Promise<Vehicle[]> {
    const params = new URLSearchParams();
    if (make) params.append('make', make);
    if (model) params.append('model', model);

    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE_URL}/api/vehicles${query}`);
    return handleResponse<Vehicle[]>(res);
  },

  /**
   * Retrieves details and compatible parts for a specific vehicle.
   */
  async getVehicle(vehicleId: number): Promise<VehicleDetail> {
    const res = await fetch(`${API_BASE_URL}/api/vehicles/${vehicleId}`);
    return handleResponse<VehicleDetail>(res);
  },

  /**
   * Direct vehicle compatibility lookup for a canonical part name or alias.
   */
  async getCompatibility(partName: string, verifiedOnly: boolean = false): Promise<CompatibilityResult> {
    const params = new URLSearchParams();
    if (verifiedOnly) params.append('verified_only', 'true');

    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(
      `${API_BASE_URL}/api/compatibility/${encodeURIComponent(partName)}${query}`
    );
    return handleResponse<CompatibilityResult>(res);
  },
};

export { ApiServiceError };
