/**
 * frontend/src/pages/PartsPage.tsx
 * Professional automotive spare-parts catalog covering all 19 canonical PartVision classes.
 * Includes category filtering, search, and deep-dive vehicle fitment detail modal.
 */

import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Part, PartDetail } from '../types/api';
import { MagnifyingGlass, X, SpinnerGap, Warning, ShieldCheck } from '@phosphor-icons/react';

const CATEGORIES = [
  'All',
  'Exterior Body',
  'Exterior Glass',
  'Lighting',
  'Mirrors',
  'Wheels',
];

export const PartsPage: React.FC = () => {
  const [parts, setParts] = useState<Part[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Selected Part for Detail View
  const [activePartName, setActivePartName] = useState<string | null>(null);
  const [partDetail, setPartDetail] = useState<PartDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchParts() {
      setLoading(true);
      setError(null);
      try {
        const catArg = selectedCategory === 'All' ? undefined : selectedCategory;
        const searchArg = searchQuery.trim() ? searchQuery.trim() : undefined;
        const data = await api.getParts(catArg, searchArg);
        setParts(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load parts catalog');
      } finally {
        setLoading(false);
      }
    }

    fetchParts();
  }, [selectedCategory, searchQuery]);

  const handleOpenDetail = async (partName: string) => {
    setActivePartName(partName);
    setLoadingDetail(true);
    setDetailError(null);
    try {
      const detail = await api.getPart(partName);
      setPartDetail(detail);
    } catch (err: unknown) {
      setDetailError(err instanceof Error ? err.message : 'Failed to load part details');
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleCloseDetail = () => {
    setActivePartName(null);
    setPartDetail(null);
    setDetailError(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Context */}
      <div>
        <h1 className="text-2xl font-bold text-sand-900 tracking-tight">
          Parts
        </h1>
        <p className="text-sm text-sand-500 mt-1">
          Browse the automotive components currently supported by PartVision.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-sand-200 rounded-xl p-4 shadow-card flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  isSelected
                    ? 'bg-sand-900 text-white font-semibold'
                    : 'bg-sand-100 text-sand-600 hover:text-sand-900 hover:bg-sand-200'
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-64 flex-shrink-0">
          <MagnifyingGlass
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-sand-400"
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search parts..."
            className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-sand-300 bg-sand-50/50 text-sand-900 text-xs focus:bg-white focus:outline-none focus:ring-1 focus:ring-auto-red-500"
          />
        </div>
      </div>

      {/* Parts Table / List */}
      {loading ? (
        <div className="bg-white border border-sand-200 rounded-xl p-12 text-center text-xs text-sand-500 flex flex-col items-center gap-2">
          <SpinnerGap size={24} className="animate-spin text-sand-400" />
          <span>Loading catalog...</span>
        </div>
      ) : error ? (
        <div className="bg-auto-rose-50 border border-auto-rose-200 rounded-xl p-4 text-xs text-auto-rose-700">
          {error}
        </div>
      ) : parts.length === 0 ? (
        <div className="bg-white border border-sand-200 rounded-xl p-12 text-center text-xs text-sand-500">
          No parts match your search criteria.
        </div>
      ) : (
        <div className="bg-white border border-sand-200 rounded-xl overflow-hidden shadow-card">
          <div className="divide-y divide-sand-200">
            {parts.map((p) => (
              <div
                key={p.part_name}
                onClick={() => handleOpenDetail(p.part_name)}
                className="px-5 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-sand-50 cursor-pointer transition-colors"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleOpenDetail(p.part_name);
                  }
                }}
              >
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sand-900 text-sm">
                      {p.display_name}
                    </span>
                    <span className="text-[11px] font-mono text-sand-400">
                      ({p.part_name})
                    </span>
                  </div>

                  {p.description && (
                    <p className="text-xs text-sand-500 line-clamp-1 max-w-2xl">
                      {p.description}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-3 flex-shrink-0 self-start sm:self-center">
                  <span className="px-2 py-0.5 rounded bg-sand-100 text-sand-600 text-xs font-mono">
                    {p.category}
                  </span>

                  <span className="text-xs text-auto-red-500 hover:text-auto-red-600 font-medium">
                    View fitment →
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Part Detail Modal */}
      {activePartName && (
        <div className="fixed inset-0 z-50 bg-sand-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white border border-sand-200 rounded-2xl max-w-xl w-full p-6 shadow-modal max-h-[90vh] overflow-y-auto space-y-5">
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-sand-200 pb-4">
              <div>
                <span className="text-xs font-mono uppercase text-sand-500">
                  Component Detail
                </span>
                <h2 className="text-lg font-bold text-sand-900 mt-0.5">
                  {partDetail ? partDetail.display_name : activePartName}
                </h2>
                <p className="text-xs font-mono text-sand-500">
                  Canonical: {activePartName}
                </p>
              </div>

              <button
                onClick={handleCloseDetail}
                className="p-1 rounded-md text-sand-400 hover:text-sand-700 hover:bg-sand-100 transition"
                aria-label="Close part details"
              >
                <X size={20} />
              </button>
            </div>

            {loadingDetail && (
              <div className="py-10 text-center text-xs text-sand-500 flex flex-col items-center gap-2">
                <SpinnerGap size={24} className="animate-spin text-auto-red-500" />
                <span>Loading compatibility records...</span>
              </div>
            )}

            {detailError && (
              <div className="p-3 bg-auto-rose-50 border border-auto-rose-200 rounded-lg text-xs text-auto-rose-700">
                {detailError}
              </div>
            )}

            {partDetail && (
              <div className="space-y-4 text-xs">
                {/* Description & Category */}
                <div className="p-3.5 bg-sand-50 rounded-lg border border-sand-200 space-y-1">
                  <div className="flex items-center justify-between text-sand-500">
                    <span className="font-mono uppercase text-[10px]">Category</span>
                    <span className="font-medium text-sand-700">{partDetail.category}</span>
                  </div>
                  <p className="text-sand-700 text-xs mt-1">
                    {partDetail.description || 'No description provided.'}
                  </p>
                </div>

                {/* Search Synonyms / Aliases */}
                {partDetail.aliases && partDetail.aliases.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-semibold text-sand-600 uppercase font-mono mb-1.5">
                      Known Aliases & Synonyms
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {partDetail.aliases.map((alias) => (
                        <span
                          key={alias}
                          className="px-2 py-0.5 rounded bg-sand-100 text-sand-700 font-mono text-[11px]"
                        >
                          {alias}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Compatibility List */}
                <div className="space-y-2 pt-2 border-t border-sand-200">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-sand-900 flex items-center gap-1.5">
                      <ShieldCheck size={16} className="text-auto-green-500" />
                      <span>Verified OEM Compatible Vehicles ({partDetail.compatibility.verified_vehicles.length})</span>
                    </h4>
                  </div>

                  {partDetail.compatibility.verified_vehicles.length > 0 ? (
                    <div className="space-y-2 max-h-56 overflow-y-auto">
                      {partDetail.compatibility.verified_vehicles.map((v) => (
                        <div
                          key={`modal-veh-${v.id}`}
                          className="p-3 bg-sand-50 rounded-lg border border-sand-200 text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-sand-900">
                              {v.make} {v.model} {v.generation ? `(${v.generation})` : ''}
                            </span>
                            <span className="text-[11px] font-mono text-auto-green-600 font-medium">
                              Direct Fit
                            </span>
                          </div>
                          <p className="text-sand-600 text-[11px] mt-0.5 font-mono">
                            {v.year_start}–{v.year_end || 'Present'} · {v.vehicle_type}
                          </p>
                          {v.notes && <p className="text-sand-600 text-[11px] mt-1">{v.notes}</p>}
                          <p className="text-[10px] text-sand-500 mt-1 font-mono">
                            Source: {v.source}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sand-500 italic py-2">
                      No verified OEM vehicle fitments registered in the current baseline catalog.
                    </p>
                  )}
                </div>

                {/* Unverified Section */}
                {partDetail.compatibility.unverified_vehicles.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-sand-200">
                    <h4 className="font-semibold text-auto-amber-700 flex items-center gap-1.5">
                      <Warning size={14} className="text-auto-amber-600" />
                      <span>Unverified / Demonstration Records</span>
                    </h4>
                    <div className="space-y-1.5">
                      {partDetail.compatibility.unverified_vehicles.map((v) => (
                        <div
                          key={`modal-unver-${v.id}`}
                          className="p-2.5 bg-auto-amber-50/50 rounded-lg border border-auto-amber-100 text-xs"
                        >
                          <span className="font-medium text-sand-900">
                            {v.make} {v.model}
                          </span>
                          <span className="text-sand-500 ml-2">
                            ({v.year_start}–{v.year_end || 'Present'})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
