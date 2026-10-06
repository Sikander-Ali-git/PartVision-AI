import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { App } from '../App';
import { DetectionList } from '../components/DetectionList';
import { CompatibilityPanel } from '../components/CompatibilityPanel';
import { Detection } from '../types/api';

describe('App & Component Tests', () => {
  beforeEach(() => {
    window.history.pushState(null, '', '/');
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: 'healthy',
        service: 'PartVision AI API',
        version: '0.4.0',
        model: 'partvision_v3_yolo11n_seg',
        model_loaded: true,
        database_connected: true,
      }),
    } as Response);
  });

  it('renders application header and default Analyze tab', () => {
    render(<App />);
    expect(screen.getAllByText(/PARTVISION/i)[0]).toBeInTheDocument();
    expect(screen.getByText(/Identify an automotive part/i)).toBeInTheDocument();
  });

  it('navigates between Analyze, Parts, Vehicles, and About tabs', () => {
    render(<App />);

    // Click Parts tab
    const partsTabBtn = screen.getByRole('button', { name: /^Parts$/i });
    fireEvent.click(partsTabBtn);
    expect(screen.getByText(/Browse the automotive components currently supported by PartVision/i)).toBeInTheDocument();
    expect(window.location.pathname).toBe('/parts');

    // Click Vehicles tab
    const vehiclesTabBtn = screen.getByRole('button', { name: /^Vehicles$/i });
    fireEvent.click(vehiclesTabBtn);
    expect(screen.getByText(/Browse supported vehicles and compatible OEM components/i)).toBeInTheDocument();
    expect(window.location.pathname).toBe('/vehicles');

    // Click About tab
    const aboutTabBtn = screen.getByRole('button', { name: /^About$/i });
    fireEvent.click(aboutTabBtn);
    expect(screen.getByText(/About PartVision/i)).toBeInTheDocument();
    expect(screen.getByText(/What is PartVision\?/i)).toBeInTheDocument();
    expect(window.location.pathname).toBe('/about');

    // Click back to Analyze
    const analyzeTabBtn = screen.getByRole('button', { name: /^Analyze$/i });
    fireEvent.click(analyzeTabBtn);
    expect(screen.getByText(/Identify an automotive part/i)).toBeInTheDocument();
    expect(window.location.pathname).toBe('/');
  });

  it('renders 404 page for unknown routes and navigates home', () => {
    window.history.pushState(null, '', '/unsupported/invalid/path');
    render(<App />);

    expect(screen.getByText(/Page Not Found/i)).toBeInTheDocument();
    expect(screen.getByText(/The requested route does not exist/i)).toBeInTheDocument();

    const homeBtn = screen.getByRole('button', { name: /Return to PartVision Home/i });
    fireEvent.click(homeBtn);
    expect(screen.getByText(/Identify an automotive part/i)).toBeInTheDocument();
    expect(window.location.pathname).toBe('/');
  });

  it('DetectionList preserves duplicate class instances distinctly', () => {
    const mockDetections: Detection[] = [
      {
        class_id: 18,
        part_name: 'wheel',
        display_name: 'Wheel',
        confidence: 0.954,
        bbox: { x1: 50, y1: 160, x2: 95, y2: 250 },
        compatibility: { verified_vehicles: [], unverified_vehicles: [], total_matches: 0 },
      },
      {
        class_id: 18,
        part_name: 'wheel',
        display_name: 'Wheel',
        confidence: 0.938,
        bbox: { x1: 175, y1: 268, x2: 274, y2: 452 },
        compatibility: { verified_vehicles: [], unverified_vehicles: [], total_matches: 0 },
      },
    ];

    render(
      <DetectionList
        detections={mockDetections}
        selectedIndex={0}
        onSelectDetection={vi.fn()}
        onHoverDetection={vi.fn()}
      />
    );

    // Both wheel instances must be rendered
    const wheelLabels = screen.getAllByText('Wheel');
    expect(wheelLabels).toHaveLength(2);
    expect(screen.getByText('95.4%')).toBeInTheDocument();
    expect(screen.getByText('93.8%')).toBeInTheDocument();
  });

  it('CompatibilityPanel strictly separates verified and unverified fitment records', () => {
    const mockDetection: Detection = {
      class_id: 5,
      part_name: 'front_bumper',
      display_name: 'Front Bumper',
      confidence: 0.942,
      bbox: { x1: 100, y1: 100, x2: 400, y2: 300 },
      compatibility: {
        verified_vehicles: [
          {
            id: 1,
            make: 'Maruti Suzuki',
            model: 'Swift',
            generation: '3rd Gen',
            year_start: 2018,
            year_end: 2024,
            compatibility_status: 'compatible',
            source: 'MSGP Catalog',
            verified: true,
          },
        ],
        unverified_vehicles: [
          {
            id: 99,
            make: 'Aftermarket',
            model: 'Universal Lip',
            compatibility_status: 'custom_fit',
            source: 'Demonstration Catalog',
            verified: false,
          },
        ],
        total_matches: 2,
      },
    };

    render(<CompatibilityPanel detection={mockDetection} />);

    expect(screen.getByText(/Front Bumper/i)).toBeInTheDocument();
    expect(screen.getByText(/Verified Fitment \(1\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Maruti Suzuki Swift/i)).toBeInTheDocument();
    expect(screen.getByText(/Unverified \/ Demonstration Fitment \(1\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Aftermarket Universal Lip/i)).toBeInTheDocument();
    expect(
      screen.getByText(
        /PartVision identifies the visible part using computer vision. Vehicle compatibility is retrieved from the structured fitment database./i
      )
    ).toBeInTheDocument();
  });
});
