/**
 * frontend/src/components/CompatibilityPanel.tsx
 * Trust-centric compatibility display for selected automotive component.
 * Strictly distinguishes verified OEM records from demonstration fitment.
 */

import React from 'react';
import { Detection } from '../types/api';
import { CheckCircle, Warning, Info, ShieldCheck } from '@phosphor-icons/react';

interface CompatibilityPanelProps {
  detection: Detection | null;
}

export const CompatibilityPanel: React.FC<CompatibilityPanelProps> = ({ detection }) => {
  if (!detection) {
    return (
      <div className="bg-white border border-sand-200 rounded-xl p-6 shadow-card text-center text-xs text-sand-500">
        <ShieldCheck size={28} className="mx-auto text-sand-400 mb-2" />
        Select a detected part to inspect its verified vehicular compatibility records.
      </div>
    );
  }

  const { display_name, part_name, confidence, compatibility } = detection;
  const verifiedList = compatibility?.verified_vehicles || [];
  const unverifiedList = compatibility?.unverified_vehicles || [];

  return (
    <div className="bg-white border border-sand-200 rounded-xl overflow-hidden shadow-card">
      {/* Selected Component Header */}
      <div className="px-5 py-4 border-b border-sand-200 bg-sand-50">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-[11px] font-mono uppercase tracking-wider text-sand-500">
              Selected Component
            </div>
            <h3 className="text-base font-bold text-sand-900 mt-0.5">
              {display_name}
            </h3>
            <div className="text-xs font-mono text-sand-500">
              Canonical: <span className="text-sand-700">{part_name}</span>
            </div>
          </div>

          <div className="text-right">
            <div className="text-xs font-mono font-semibold text-sand-900">
              {(confidence * 100).toFixed(1)}%
            </div>
            <div className="text-[10px] text-sand-500" title="Model detection confidence">
              Model confidence
            </div>
          </div>
        </div>
      </div>

      <div className="p-5 space-y-5">
        {/* Section 1: Verified OEM Fitment */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <h4 className="text-xs font-semibold text-sand-900 uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle size={15} weight="fill" className="text-auto-green-500" />
              <span>Verified Fitment ({verifiedList.length})</span>
            </h4>
            <span className="text-[11px] text-auto-green-600 bg-auto-green-50 border border-auto-green-100 px-2 py-0.5 rounded font-medium">
              OEM Catalog Verified
            </span>
          </div>

          {verifiedList.length > 0 ? (
            <div className="space-y-2">
              {verifiedList.map((veh) => (
                <div
                  key={`verified-veh-${veh.id}`}
                  className="p-3 rounded-lg border border-sand-200 bg-sand-50/50 hover:bg-sand-50 transition-colors text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sand-900">
                      {veh.make} {veh.model}
                    </span>
                    <span className="text-[11px] font-mono text-auto-green-600 font-medium">
                      {veh.compatibility_status === 'compatible' ? 'Direct Fit' : veh.compatibility_status}
                    </span>
                  </div>

                  <div className="text-sand-600 text-[11px] mt-0.5">
                    {veh.generation && <span>{veh.generation} · </span>}
                    <span>{veh.year_start}–{veh.year_end || 'Present'}</span>
                    {veh.vehicle_type && <span> · {veh.vehicle_type}</span>}
                  </div>

                  {veh.notes && (
                    <p className="text-sand-600 text-[11px] mt-1 italic">
                      {veh.notes}
                    </p>
                  )}

                  <div className="text-[10px] text-sand-500 mt-1 font-mono">
                    Source: {veh.source}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-sand-500 bg-sand-50 p-3 rounded-lg border border-sand-200">
              No verified OEM fitment records are available for this component in the catalog.
            </p>
          )}
        </div>

        {/* Section 2: Unverified / Demonstration (Strictly Segregated) */}
        {unverifiedList.length > 0 && (
          <div className="pt-3 border-t border-sand-200">
            <div className="flex items-center justify-between mb-2.5">
              <h4 className="text-xs font-semibold text-auto-amber-700 uppercase tracking-wider flex items-center gap-1.5">
                <Warning size={15} weight="bold" className="text-auto-amber-600" />
                <span>Unverified / Demonstration Fitment ({unverifiedList.length})</span>
              </h4>
              <span className="text-[10px] text-auto-amber-700 bg-auto-amber-50 border border-auto-amber-100 px-1.5 py-0.5 rounded font-medium">
                Unverified
              </span>
            </div>

            <div className="space-y-2">
              {unverifiedList.map((veh) => (
                <div
                  key={`unverified-veh-${veh.id}`}
                  className="p-3 rounded-lg border border-auto-amber-100 bg-auto-amber-50/40 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sand-900">
                      {veh.make} {veh.model}
                    </span>
                    <span className="text-[10px] text-auto-amber-700 font-mono">
                      Unverified Fitment
                    </span>
                  </div>

                  <div className="text-sand-600 text-[11px] mt-0.5">
                    {veh.generation && <span>{veh.generation} · </span>}
                    <span>{veh.year_start}–{veh.year_end || 'Present'}</span>
                  </div>

                  {veh.notes && (
                    <p className="text-sand-600 text-[11px] mt-1">
                      {veh.notes}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mandatory Trust Disclosure */}
        <div className="pt-3 border-t border-sand-200 flex items-start gap-2 text-[11px] text-sand-500">
          <Info size={14} className="flex-shrink-0 mt-0.5 text-sand-500" />
          <p>
            PartVision identifies the visible part using computer vision. Vehicle compatibility is retrieved from the structured fitment database.
          </p>
        </div>
      </div>
    </div>
  );
};
