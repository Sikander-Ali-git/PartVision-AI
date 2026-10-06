/**
 * frontend/src/components/Footer.tsx
 * Restrained, informative footer reinforcing architectural integrity and trust principles.
 */

import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-sand-200 bg-white mt-auto py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-xs text-sand-500">
          <div className="space-y-1">
            <p className="font-medium text-sand-700">
              PartVision AI — Automotive Parts Identification & Compatibility
            </p>
            <p className="text-sand-500">
              Visual components identified via frozen YOLO11n-seg (V3) · Vehicular fitment resolved by SQLite database.
            </p>
          </div>

          <div className="flex items-center gap-6 text-sand-500 font-mono">
            <span>19 Classes</span>
            <span>·</span>
            <span>85.7% mAP50</span>
            <span>·</span>
            <span>v0.4.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
