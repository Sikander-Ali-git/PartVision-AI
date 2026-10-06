/**
 * frontend/src/App.tsx
 * Professional automotive single-page application container.
 */

import React, { useState } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { AnalyzePage } from './pages/AnalyzePage';
import { PartsPage } from './pages/PartsPage';
import { VehiclesPage } from './pages/VehiclesPage';
import { AboutPage } from './pages/AboutPage';
import { useApiHealth } from './hooks/useApiHealth';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'analyze' | 'parts' | 'vehicles' | 'about'>('analyze');
  const { health, isLoading } = useApiHealth();

  return (
    <div className="min-h-screen flex flex-col bg-sand-50 text-sand-900 font-sans">
      {/* Global Navigation Header */}
      <Header
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        health={health}
        healthLoading={isLoading}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === 'analyze' && <AnalyzePage />}
        {activeTab === 'parts' && <PartsPage />}
        {activeTab === 'vehicles' && <VehiclesPage />}
        {activeTab === 'about' && <AboutPage />}
      </main>

      {/* Technical Footer */}
      <Footer />
    </div>
  );
};

export default App;
