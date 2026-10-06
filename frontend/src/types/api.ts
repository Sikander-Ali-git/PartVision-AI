/**
 * frontend/src/types/api.ts
 * Strict TypeScript types aligned with PartVision AI FastAPI schemas (Milestone 7 / 8).
 */

export interface HealthStatus {
  status: 'healthy' | 'degraded' | string;
  service: string;
  version: string;
  model: string;
  model_loaded: boolean;
  database_connected: boolean;
}

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface PolygonMask {
  format: string;
  points: [number, number][];
}

export interface CompatibleVehicle {
  id: number;
  make: string;
  model: string;
  generation?: string | null;
  year_start?: number | null;
  year_end?: number | null;
  variant?: string | null;
  vehicle_type?: string | null;
  compatibility_status: string;
  notes?: string | null;
  source: string;
  verified: boolean;
}

export interface PartCompatibility {
  verified_vehicles: CompatibleVehicle[];
  unverified_vehicles: CompatibleVehicle[];
  total_matches: number;
}

export interface Detection {
  class_id: number;
  part_name: string;
  display_name: string;
  confidence: number;
  bbox: BoundingBox;
  mask?: PolygonMask | null;
  compatibility: PartCompatibility;
}

export interface AnalysisSummary {
  detection_count: number;
  detected_parts: string[];
}

export interface AnalysisInference {
  device: string;
  latency_ms: number;
  total_pipeline_ms?: number | null;
}

export interface ModelMetadata {
  name: string;
  version: string;
}

export interface ImageMetadata {
  width: number;
  height: number;
}

export interface AnalysisResult {
  request_id: string;
  model: ModelMetadata;
  image: ImageMetadata;
  detections: Detection[];
  summary: AnalysisSummary;
  inference: AnalysisInference;
}

export interface Part {
  id: number;
  part_name: string;
  display_name: string;
  category: string;
  description?: string | null;
}

export interface PartDetail extends Part {
  aliases: string[];
  compatibility: PartCompatibility;
}

export interface Vehicle {
  id: number;
  make: string;
  model: string;
  generation?: string | null;
  year_start?: number | null;
  year_end?: number | null;
  variant?: string | null;
  vehicle_type?: string | null;
  notes?: string | null;
  display_name: string;
}

export interface VehiclePartFitment {
  part_id: number;
  part_name: string;
  display_name: string;
  category: string;
  compatibility_status: string;
  notes?: string | null;
  source: string;
  verified: boolean;
}

export interface VehicleDetail {
  vehicle: Vehicle;
  compatible_parts: VehiclePartFitment[];
  total_parts: number;
}

export interface CompatibilityResult {
  part: string;
  display_name: string;
  verified_vehicles: CompatibleVehicle[];
  unverified_vehicles: CompatibleVehicle[];
  total_matches: number;
}

export interface ApiError {
  error: string;
  detail: string;
  request_id?: string;
}
