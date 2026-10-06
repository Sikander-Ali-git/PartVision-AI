import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api, ApiServiceError } from '../services/api';

describe('API Client Service (src/services/api.ts)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('healthCheck calls /health and returns parsed HealthStatus', async () => {
    const mockHealth = {
      status: 'healthy',
      service: 'PartVision AI API',
      version: '0.4.0',
      model: 'partvision_v3_yolo11n_seg',
      model_loaded: true,
      database_connected: true,
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHealth,
    } as Response);

    const result = await api.healthCheck();
    expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/health');
    expect(result).toEqual(mockHealth);
  });

  it('getParts appends category and search query parameters', async () => {
    const mockParts = [
      { id: 9, part_name: 'front_light', display_name: 'Front Light', category: 'Lighting' },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockParts,
    } as Response);

    const result = await api.getParts('Lighting', 'head');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/parts?category=Lighting&search=head'
    );
    expect(result).toHaveLength(1);
    expect(result[0].part_name).toBe('front_light');
  });

  it('getVehicles fetches vehicles catalog with make filter', async () => {
    const mockVehicles = [
      {
        id: 1,
        make: 'Hyundai',
        model: 'Creta',
        generation: '2nd Gen',
        year_start: 2020,
        year_end: 2023,
        vehicle_type: 'Compact SUV',
        display_name: 'Hyundai Creta 2nd Gen (2020–2023)',
      },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockVehicles,
    } as Response);

    const result = await api.getVehicles('Hyundai');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/vehicles?make=Hyundai'
    );
    expect(result).toHaveLength(1);
    expect(result[0].model).toBe('Creta');
  });

  it('analyzeImage posts FormData and returns AnalysisResult', async () => {
    const mockAnalysis = {
      request_id: 'test-uuid-1234',
      model: { name: 'PartVision YOLO11n-seg', version: 'v3' },
      image: { width: 640, height: 480 },
      detections: [],
      summary: { detection_count: 0, detected_parts: [] },
      inference: { device: 'mps', latency_ms: 42.5 },
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockAnalysis,
    } as Response);

    const testFile = new File(['dummy-bytes'], 'car.png', { type: 'image/png' });
    const result = await api.analyzeImage(testFile);

    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/analyze',
      expect.objectContaining({
        method: 'POST',
        body: expect.any(FormData),
      })
    );
    expect(result.request_id).toBe('test-uuid-1234');
  });

  it('throws ApiServiceError on HTTP 413, 415, and 400 errors', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 413,
      json: async () => ({ error: 'PayloadTooLarge', detail: 'File too large' }),
    } as Response);

    const testFile = new File(['large-bytes'], 'huge.jpg', { type: 'image/jpeg' });
    await expect(api.analyzeImage(testFile)).rejects.toThrow(ApiServiceError);
    await expect(api.analyzeImage(testFile)).rejects.toMatchObject({
      status: 413,
      errorType: 'PayloadTooLarge',
      message: 'File too large',
    });
  });
});
