/**
 * frontend/src/pages/VehiclesPage.tsx
 * Professional vehicle catalog covering registered makes, models, and OEM component mappings.
 */

import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Vehicle, VehicleDetail } from '../types/api';
import { MagnifyingGlass, X, SpinnerGap, CheckCircle, Car } from '@phosphor-icons/react';

export const VehiclesPage: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedMake, setSelectedMake] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Vehicle Detail View
  const [activeVehicleId, setActiveVehicleId] = useState<number | null>(null);
  const [vehicleDetail, setVehicleDetail] = useState<VehicleDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchVehicles() {
      setLoading(true);
      setError(null);
      try {
        const makeArg = selectedMake === 'All' ? undefined : selectedMake;
        const data = await api.getVehicles(makeArg);
        setVehicles(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load vehicle catalog');
      } finally {
        setLoading(false);
      }
    }

    fetchVehicles();
  }, [selectedMake]);

  // Extract unique makes for filtering
  const availableMakes = ['All', ...Array.from(new Set(vehicles.map((v) => v.make)))];

  // Filter vehicles by search query
  const filteredVehicles = vehicles.filter((v) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      v.make.toLowerCase().includes(q) ||
      v.model.toLowerCase().includes(q) ||
      (v.generation && v.generation.toLowerCase().includes(q)) ||
      (v.vehicle_type && v.vehicle_type.toLowerCase().includes(q))
    );
  });

  const handleOpenDetail = async (vehicleId: number) => {
    setActiveVehicleId(vehicleId);
    setLoadingDetail(true);
    setDetailError(null);
    try {
      const detail = await api.getVehicle(vehicleId);
      setVehicleDetail(detail);
    } catch (err: unknown) {
      setDetailError(err instanceof Error ? err.message : 'Failed to load vehicle details');
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleCloseDetail = () => {
    setActiveVehicleId(null);
    setVehicleDetail(null);
    setDetailError(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Context */}
      <div>
        <h1 className="text-2xl font-bold text-sand-900 tracking-tight">
          Vehicles
        </h1>
        <p className="text-sm text-sand-500 mt-1">
          Browse supported vehicles and compatible OEM components.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-sand-200 rounded-xl p-4 shadow-card flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Make Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {availableMakes.map((make) => {
            const isSelected = selectedMake === make;
            return (
              <button
                key={make}
                type="button"
                onClick={() => setSelectedMake(make)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  isSelected
                    ? 'bg-sand-900 text-white font-semibold'
                    : 'bg-sand-100 text-sand-600 hover:text-sand-900 hover:bg-sand-200'
                }`}
              >
                {make}
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
            placeholder="Search make or model..."
            className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-sand-300 bg-sand-50/50 text-sand-900 text-xs focus:bg-white focus:outline-none focus:ring-1 focus:ring-auto-red-500"
          />
        </div>
      </div>

      {/* Vehicles Table / List */}
      {loading ? (
        <div className="bg-white border border-sand-200 rounded-xl p-12 text-center text-xs text-sand-500 flex flex-col items-center gap-2">
          <SpinnerGap size={24} className="animate-spin text-sand-400" />
          <span>Loading vehicles catalog...</span>
        </div>
      ) : error ? (
        <div className="bg-auto-rose-50 border border-auto-rose-200 rounded-xl p-4 text-xs text-auto-rose-700">
          {error}
        </div>
      ) : filteredVehicles.length === 0 ? (
        <div className="bg-white border border-sand-200 rounded-xl p-12 text-center text-xs text-sand-500">
          No vehicles match your search criteria.
        </div>
      ) : (
        <div className="bg-white border border-sand-200 rounded-xl overflow-hidden shadow-card">
          <div className="divide-y divide-sand-200">
            {filteredVehicles.map((v) => (
              <div
                key={v.id}
                onClick={() => handleOpenDetail(v.id)}
                className="px-5 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-sand-50 cursor-pointer transition-colors"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleOpenDetail(v.id);
                  }
                }}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sand-900 text-sm">
                      {v.make} {v.model}
                    </span>
                    {v.generation && (
                      <span className="text-xs text-sand-500 font-mono">
                        ({v.generation})
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs text-sand-500 font-mono">
                    <span>
                      {v.year_start}–{v.year_end || 'Present'}
                    </span>
                    {v.vehicle_type && (
                      <>
                        <span>·</span>
                        <span>{v.vehicle_type}</span>
                      </>
                    )}
                  </div>

                  {v.notes && (
                    <p className="text-xs text-sand-500 line-clamp-1 max-w-xl">
                      {v.notes}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-3 flex-shrink-0 self-start sm:self-center">
                  <span className="text-xs text-auto-red-500 hover:text-auto-red-600 font-medium">
                    View components →
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vehicle Detail Modal */}
      {activeVehicleId !== null && (
        <div className="fixed inset-0 z-50 bg-sand-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white border border-sand-200 rounded-2xl max-w-xl w-full p-6 shadow-modal max-h-[90vh] overflow-y-auto space-y-5">
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-sand-200 pb-4">
              <div>
                <span className="text-xs font-mono uppercase text-sand-500">
                  Vehicle Specifications
                </span>
                <h2 className="text-lg font-bold text-sand-900 mt-0.5">
                  {vehicleDetail ? `${vehicleDetail.vehicle.make} ${vehicleDetail.vehicle.model}` : 'Loading...'}
                </h2>
                {vehicleDetail && (
                  <p className="text-xs font-mono text-sand-500">
                    {vehicleDetail.vehicle.generation && `${vehicleDetail.vehicle.generation} · `}
                    {vehicleDetail.vehicle.year_start}–{vehicleDetail.vehicle.year_end || 'Present'} · {vehicleDetail.vehicle.vehicle_type}
                  </p>
                )}
              </div>

              <button
                onClick={handleCloseDetail}
                className="p-1 rounded-md text-sand-400 hover:text-sand-700 hover:bg-sand-100 transition"
                aria-label="Close vehicle details"
              >
                <X size={20} />
              </button>
            </div>

            {loadingDetail && (
              <div className="py-10 text-center text-xs text-sand-500 flex flex-col items-center gap-2">
                <SpinnerGap size={24} className="animate-spin text-auto-red-500" />
                <span>Loading compatible components...</span>
              </div>
            )}

            {detailError && (
              <div className="p-3 bg-auto-rose-50 border border-auto-rose-200 rounded-lg text-xs text-auto-rose-700">
                {detailError}
              </div>
            )}

            {vehicleDetail && (
              <div className="space-y-4 text-xs">
                {/* Compatible Components List */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-sand-900 flex items-center gap-1.5">
                      <Car size={16} className="text-sand-600" />
                      <span>Compatible OEM Components ({vehicleDetail.total_parts})</span>
                    </h4>
                  </div>

                  {vehicleDetail.compatible_parts.length > 0 ? (
                    <div className="space-y-2 max-h-72 overflow-y-auto">
                      {vehicleDetail.compatible_parts.map((p) => (
                        <div
                          key={`veh-part-${p.part_id}`}
                          className="p-3 bg-sand-50 rounded-lg border border-sand-200 text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-sand-900">
                              {p.display_name}
                            </span>
                            <span className="text-[11px] font-mono text-auto-green-600 font-medium flex items-center gap-1">
                              <CheckCircle size={13} weight="bold" />
                              <span>{p.compatibility_status === 'compatible' ? 'Direct Fit' : p.compatibility_status}</span>
                            </span>
                          </div>

                          <div className="flex items-center gap-2 text-sand-500 font-mono text-[11px] mt-0.5">
                            <span>{p.category}</span>
                            <span>·</span>
                            <span>{p.part_name}</span>
                          </div>

                          {p.notes && <p className="text-sand-600 text-[11px] mt-1">{p.notes}</p>}
                          <p className="text-[10px] text-sand-500 mt-1 font-mono">
                            Source: {p.source}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sand-500 italic py-2">
                      No components currently mapped to this vehicle in the database.
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
