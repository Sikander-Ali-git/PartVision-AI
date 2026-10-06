/**
 * frontend/src/pages/PartsPage.tsx
 * Catalog browsing page displaying all 19 canonical PartVision V3 taxonomy classes.
 */

import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Part, PartDetail } from '../types/api';
import { getPartColor } from '../utils/colors';
import {
  MagnifyingGlass,
  X,
  SpinnerGap,
} from '@phosphor-icons/react';

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

  // Selected Part for Detail Modal
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

  // Load Part Details when a part card is clicked
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
      {/* Header */}
      <div className="pb-3 border-b border-graphite-850">
        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>Automotive Spare-Parts Catalog</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-400/10 border border-cyan-400/30 text-cyan-400 font-mono font-medium">
            19 Classes
          </span>
        </h1>
        <p className="text-xs sm:text-sm text-graphite-400 mt-1">
          Explore the canonical PartVision V3 visual taxonomy and vehicle fitment cross-references.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-graphite-900 border border-graphite-800 p-3 rounded-2xl">
        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-400/40 shadow-sm'
                  : 'text-graphite-400 hover:text-white hover:bg-graphite-850'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative min-w-[220px]">
          <MagnifyingGlass
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-graphite-400"
          />
          <input
            type="text"
            placeholder="Search parts by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-graphite-950 border border-graphite-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-graphite-500 focus:outline-none focus:border-cyan-400 transition"
          />
        </div>
      </div>

      {/* Loading & Error States */}
      {loading && (
        <div className="py-16 text-center text-graphite-400 flex flex-col items-center justify-center gap-2">
          <SpinnerGap size={24} className="animate-spin text-cyan-400" />
          <span className="text-xs font-mono">Loading parts taxonomy...</span>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-950/20 border border-rose-800 rounded-xl text-xs text-rose-300 text-center">
          {error}
        </div>
      )}

      {/* Parts Cards Grid */}
      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {parts.map((part) => {
            const color = getPartColor(part.part_name);

            return (
              <div
                key={part.id}
                onClick={() => handleOpenDetail(part.part_name)}
                className="bg-graphite-900 border border-graphite-800 hover:border-cyan-400/50 rounded-2xl p-4 shadow-sm hover:shadow-glow-cyan/20 cursor-pointer transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: color.hex }}
                      />
                      <h3 className="text-sm font-bold text-white group-hover:text-cyan-400 transition-colors">
                        {part.display_name}
                      </h3>
                    </div>

                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-graphite-850 border border-graphite-800 text-graphite-300">
                      {part.category}
                    </span>
                  </div>

                  <p className="text-xs text-graphite-400 line-clamp-2 leading-relaxed">
                    {part.description || 'Automotive exterior replacement component.'}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-graphite-800/80 flex items-center justify-between text-xs">
                  <code className="text-[11px] text-cyan-400 font-mono">
                    {part.part_name}
                  </code>
                  <span className="text-[11px] text-graphite-400 group-hover:text-cyan-400 font-medium transition-colors">
                    View Fitment →
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* PART DETAIL MODAL */}
      {activePartName && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-graphite-900 border border-graphite-750 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 shadow-2xl space-y-5 animate-in fade-in duration-150">
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-3 border-b border-graphite-800">
              <div>
                <span className="text-xs uppercase font-mono text-cyan-400 tracking-wider">
                  Part Details & Vehicular Compatibility
                </span>
                <h2 className="text-xl font-bold text-white mt-1">
                  {partDetail ? partDetail.display_name : activePartName}
                </h2>
                <p className="text-xs text-graphite-400 font-mono">
                  Canonical: <code className="text-cyan-300">{activePartName}</code>
                </p>
              </div>

              <button
                onClick={handleCloseDetail}
                className="p-1.5 rounded-lg text-graphite-400 hover:text-white hover:bg-graphite-800 transition"
              >
                <X size={18} />
              </button>
            </div>

            {loadingDetail && (
              <div className="py-12 text-center text-graphite-400 flex flex-col items-center gap-2">
                <SpinnerGap size={24} className="animate-spin text-cyan-400" />
                <span className="text-xs font-mono">Fetching compatibility records...</span>
              </div>
            )}

            {detailError && (
              <div className="p-3 bg-rose-950/30 border border-rose-800 rounded-xl text-xs text-rose-300">
                {detailError}
              </div>
            )}

            {partDetail && (
              <div className="space-y-4 text-xs">
                {/* Description & Category */}
                <div className="bg-graphite-950 p-4 rounded-xl border border-graphite-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-graphite-400 font-semibold uppercase text-[10px] tracking-wider font-mono">
                      Category
                    </span>
                    <span className="text-cyan-400 font-mono font-medium">
                      {partDetail.category}
                    </span>
                  </div>
                  <p className="text-graphite-300 leading-relaxed">
                    {partDetail.description}
                  </p>
                </div>

                {/* Aliases & Search Synonyms */}
                {partDetail.aliases && partDetail.aliases.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-graphite-300 mb-2 font-mono uppercase tracking-wider">
                      Search Synonyms & Colloquial Aliases
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {partDetail.aliases.map((alias) => (
                        <span
                          key={alias}
                          className="px-2 py-0.5 rounded bg-graphite-850 border border-graphite-750 text-graphite-300 font-mono text-[11px]"
                        >
                          {alias}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Compatibility Matches */}
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between border-b border-graphite-800 pb-2">
                    <h4 className="text-xs font-semibold text-white uppercase tracking-wider font-mono">
                      Compatible Vehicles ({partDetail.compatibility.total_matches})
                    </h4>
                    <span className="text-[11px] text-cyan-400 font-mono">
                      {partDetail.compatibility.verified_vehicles.length} Verified OEM
                    </span>
                  </div>

                  {/* Verified List */}
                  {partDetail.compatibility.verified_vehicles.length > 0 ? (
                    <div className="space-y-2">
                      {partDetail.compatibility.verified_vehicles.map((v) => (
                        <div
                          key={`modal-v-${v.id}`}
                          className="p-3 bg-graphite-950 rounded-xl border border-emerald-500/20 text-xs space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-white">
                              {v.make} {v.model} {v.generation ? `(${v.generation})` : ''}
                            </span>
                            <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[10px]">
                              {v.compatibility_status}
                            </span>
                          </div>
                          <p className="text-graphite-400 text-[11px] font-mono">
                            {v.year_start}–{v.year_end || 'Present'} • {v.vehicle_type}
                          </p>
                          {v.notes && <p className="text-graphite-300 text-[11px]">{v.notes}</p>}
                          <p className="text-[10px] text-graphite-500">Source: {v.source}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-graphite-500 text-xs italic">
                      No verified OEM vehicle fitments registered in the current baseline catalog.
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
