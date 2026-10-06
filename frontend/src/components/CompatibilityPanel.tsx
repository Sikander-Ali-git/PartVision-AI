/**
 * frontend/src/components/CompatibilityPanel.tsx
 * Displays authoritative vehicle fitment records with strict segregation of verified OEM vs demonstration data.
 */

import React, { useState } from 'react';
import { Detection } from '../types/api';
import { ShieldCheck, WarningCircle, Info, Car } from '@phosphor-icons/react';

interface CompatibilityPanelProps {
  detection: Detection | null;
}

export const CompatibilityPanel: React.FC<CompatibilityPanelProps> = ({ detection }) => {
  const [activeTab, setActiveTab] = useState<'all' | 'verified' | 'unverified'>('all');

  if (!detection) {
    return (
      <div className="bg-graphite-900 border border-graphite-800 rounded-2xl p-6 shadow-lg text-center">
        <Car size={36} className="text-graphite-600 mx-auto mb-2" weight="duotone" />
        <h3 className="text-sm font-semibold text-white">No Part Selected</h3>
        <p className="text-xs text-graphite-400 mt-1">
          Select any detected spare part to view authoritative vehicle compatibility records.
        </p>
      </div>
    );
  }

  const { verified_vehicles, unverified_vehicles, total_matches } = detection.compatibility;

  return (
    <div className="bg-graphite-900 border border-graphite-800 rounded-2xl p-5 shadow-lg flex flex-col space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between pb-3 border-b border-graphite-800">
        <div>
          <span className="text-xs uppercase tracking-wider text-cyan-400 font-mono">
            Compatibility Lookup
          </span>
          <h3 className="text-base font-bold text-white mt-0.5">
            {detection.display_name}
          </h3>
          <p className="text-xs text-graphite-400">
            Canonical Taxonomy: <code className="text-cyan-300 font-mono">{detection.part_name}</code>
          </p>
        </div>

        <div className="text-right">
          <span className="text-sm font-bold text-white font-mono">{total_matches}</span>
          <p className="text-xs text-graphite-400">Total Matches</p>
        </div>
      </div>

      {/* Trust Principle Notice */}
      <div className="p-3 bg-cyan-950/20 border border-cyan-800/40 rounded-xl flex items-start gap-2.5 text-xs text-cyan-200">
        <Info size={18} weight="fill" className="text-cyan-400 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          PartVision uses computer vision to identify the visible part. Compatibility is retrieved from the structured fitment database.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 text-xs">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-3 py-1.5 rounded-lg font-medium transition ${
            activeTab === 'all'
              ? 'bg-graphite-850 text-white border border-graphite-700'
              : 'text-graphite-400 hover:text-white'
          }`}
        >
          All ({total_matches})
        </button>
        <button
          onClick={() => setActiveTab('verified')}
          className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition ${
            activeTab === 'verified'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
              : 'text-graphite-400 hover:text-emerald-400'
          }`}
        >
          <ShieldCheck size={14} />
          <span>Verified OEM ({verified_vehicles.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('unverified')}
          className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition ${
            activeTab === 'unverified'
              ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30'
              : 'text-graphite-400 hover:text-yellow-400'
          }`}
        >
          <WarningCircle size={14} />
          <span>Demo / Unverified ({unverified_vehicles.length})</span>
        </button>
      </div>

      {/* Vehicle Cards Container */}
      <div className="space-y-4 max-h-[420px] overflow-y-auto pr-1">
        {/* SECTION 1: VERIFIED OEM FITMENT */}
        {(activeTab === 'all' || activeTab === 'verified') && verified_vehicles.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
              <ShieldCheck size={15} weight="fill" />
              <span>Verified Fitment (OEM Catalogs)</span>
            </div>

            {verified_vehicles.map((v) => {
              const years = v.year_start ? `${v.year_start}–${v.year_end || 'Present'}` : 'All Years';
              const gen = v.generation ? ` (${v.generation})` : '';

              return (
                <div
                  key={`verified-v-${v.id}`}
                  className="p-3 bg-graphite-950 rounded-xl border border-emerald-500/20 hover:border-emerald-500/40 transition text-xs space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-semibold text-white">
                        {v.make} {v.model}{gen}
                      </h4>
                      <p className="text-graphite-400 text-[11px] font-mono">
                        {years} • {v.vehicle_type || 'Passenger Vehicle'}
                      </p>
                    </div>

                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[10px] uppercase font-semibold">
                      {v.compatibility_status}
                    </span>
                  </div>

                  {v.notes && (
                    <p className="text-graphite-300 text-[11px] leading-relaxed">
                      {v.notes}
                    </p>
                  )}

                  <div className="pt-1.5 border-t border-graphite-850 flex items-center justify-between text-[10px] text-graphite-500">
                    <span className="truncate">Source: {v.source}</span>
                    <span className="text-emerald-400 font-mono">✓ Verified</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* SECTION 2: UNVERIFIED / DEMONSTRATION DATA */}
        {(activeTab === 'all' || activeTab === 'unverified') && unverified_vehicles.length > 0 && (
          <div className="space-y-2 pt-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-yellow-400">
              <WarningCircle size={15} weight="fill" />
              <span>Unverified / Demonstration Fitment</span>
            </div>

            {unverified_vehicles.map((v) => {
              const years = v.year_start ? `${v.year_start}–${v.year_end || 'Present'}` : 'All Years';
              const gen = v.generation ? ` (${v.generation})` : '';

              return (
                <div
                  key={`unverified-v-${v.id}`}
                  className="p-3 bg-graphite-950 rounded-xl border border-yellow-500/20 hover:border-yellow-500/40 transition text-xs space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-semibold text-white">
                        {v.make} {v.model}{gen}
                      </h4>
                      <p className="text-graphite-400 text-[11px] font-mono">
                        {years} • {v.vehicle_type || 'Demonstration'}
                      </p>
                    </div>

                    <span className="px-2 py-0.5 rounded bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 font-mono text-[10px] uppercase font-semibold">
                      {v.compatibility_status}
                    </span>
                  </div>

                  {v.notes && (
                    <p className="text-graphite-300 text-[11px] leading-relaxed">
                      {v.notes}
                    </p>
                  )}

                  <div className="pt-1.5 border-t border-graphite-850 flex items-center justify-between text-[10px] text-graphite-500">
                    <span className="truncate">Source: {v.source}</span>
                    <span className="text-yellow-400 font-mono">⚠ Demonstration</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {total_matches === 0 && (
          <div className="p-6 text-center text-graphite-500 text-xs">
            No specific vehicle fitment records registered for this part in the baseline database catalog.
          </div>
        )}
      </div>
    </div>
  );
};
