/**
 * frontend/src/App.tsx
 * Professional automotive single-page application with browser URL routing and deep-linking.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { AnalyzePage } from './pages/AnalyzePage';
import { PartsPage } from './pages/PartsPage';
import { VehiclesPage } from './pages/VehiclesPage';
import { AboutPage } from './pages/AboutPage';
import { NotFoundPage } from './pages/NotFoundPage';

type NavTab = 'analyze' | 'parts' | 'vehicles' | 'about';

interface ParsedRoute {
  tab: NavTab | '404';
  partName?: string | null;
  vehicleId?: number | null;
}

function parseCurrentRoute(): ParsedRoute {
  const path = window.location.pathname.replace(/\/+$/, '') || '/';

  if (path === '/' || path === '/analyze') {
    return { tab: 'analyze' };
  }

  if (path === '/parts') {
    return { tab: 'parts', partName: null };
  }

  const partsMatch = path.match(/^\/parts\/([^/]+)$/);
  if (partsMatch) {
    return { tab: 'parts', partName: decodeURIComponent(partsMatch[1]) };
  }

  if (path === '/vehicles') {
    return { tab: 'vehicles', vehicleId: null };
  }

  const vehiclesMatch = path.match(/^\/vehicles\/(\d+)$/);
  if (vehiclesMatch) {
    return { tab: 'vehicles', vehicleId: parseInt(vehiclesMatch[1], 10) };
  }

  if (path === '/about') {
    return { tab: 'about' };
  }

  return { tab: '404' };
}

export const App: React.FC = () => {
  const [route, setRoute] = useState<ParsedRoute>(parseCurrentRoute);

  // Sync state with browser back/forward buttons
  useEffect(() => {
    const handlePopState = () => {
      setRoute(parseCurrentRoute());
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = useCallback((path: string) => {
    if (window.location.pathname !== path) {
      window.history.pushState(null, '', path);
    }
    setRoute(parseCurrentRoute());
  }, []);

  const handleSelectTab = useCallback((tab: NavTab) => {
    const targetPath = tab === 'analyze' ? '/' : `/${tab}`;
    navigate(targetPath);
  }, [navigate]);

  const handlePartSelect = useCallback((partName: string | null) => {
    const targetPath = partName ? `/parts/${encodeURIComponent(partName)}` : '/parts';
    navigate(targetPath);
  }, [navigate]);

  const handleVehicleSelect = useCallback((vehicleId: number | null) => {
    const targetPath = vehicleId !== null ? `/vehicles/${vehicleId}` : '/vehicles';
    navigate(targetPath);
  }, [navigate]);

  const currentTab: NavTab = route.tab === '404' ? 'analyze' : route.tab;

  return (
    <div className="min-h-screen flex flex-col bg-sand-50 text-sand-900 font-sans">
      {/* Global Navigation Header */}
      <Header
        activeTab={currentTab}
        onSelectTab={handleSelectTab}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {route.tab === 'analyze' && <AnalyzePage />}
        {route.tab === 'parts' && (
          <PartsPage
            initialPartName={route.partName}
            onPartSelect={handlePartSelect}
          />
        )}
        {route.tab === 'vehicles' && (
          <VehiclesPage
            initialVehicleId={route.vehicleId}
            onVehicleSelect={handleVehicleSelect}
          />
        )}
        {route.tab === 'about' && <AboutPage />}
        {route.tab === '404' && (
          <NotFoundPage onGoHome={() => navigate('/')} />
        )}
      </main>

      {/* Technical Footer */}
      <Footer />
    </div>
  );
};

export default App;
