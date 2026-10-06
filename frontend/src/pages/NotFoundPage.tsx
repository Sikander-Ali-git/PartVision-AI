/**
 * frontend/src/pages/NotFoundPage.tsx
 * Professional 404 empty state page for invalid routes.
 */

import React from 'react';
import { WarningCircle, House } from '@phosphor-icons/react';

interface NotFoundPageProps {
  onGoHome: () => void;
}

export const NotFoundPage: React.FC<NotFoundPageProps> = ({ onGoHome }) => {
  return (
    <div className="max-w-md mx-auto py-16 text-center space-y-4">
      <div className="w-16 h-16 mx-auto rounded-full bg-sand-100 border border-sand-200 flex items-center justify-center text-sand-500">
        <WarningCircle size={32} />
      </div>

      <div className="space-y-1">
        <h1 className="text-xl font-bold text-sand-900">
          Page Not Found
        </h1>
        <p className="text-xs text-sand-500">
          The requested route does not exist in the PartVision application catalog.
        </p>
      </div>

      <div className="pt-2">
        <button
          type="button"
          onClick={onGoHome}
          className="px-4 py-2 text-xs font-semibold text-white bg-auto-red-500 hover:bg-auto-red-600 rounded-lg shadow-subtle inline-flex items-center gap-1.5 transition-colors"
        >
          <House size={16} />
          <span>Return to PartVision Home</span>
        </button>
      </div>
    </div>
  );
};
