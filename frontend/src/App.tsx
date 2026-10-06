/**
 * frontend/src/App.tsx
 * Main application container with tab navigation, global layout, and backend health monitoring.
 */

import React, { useState } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { AnalyzePage } from './pages/AnalyzePage';
import { PartsPage } from './pages/PartsPage';
import { AboutPage } from './pages/AboutPage';
import { useApiHealth } from './hooks/useApiHealth';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'analyze' | 'parts' | 'about'>('analyze');
  const { isOnline, isLoading } = useApiHealth();

  return (
    <div className="min-h-screen flex flex-col bg-graphite-950 text-graphite-100">
      {/* Fixed Header */}
      <Header
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        isApiOnline={isOnline}
        apiChecking={isLoading}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {currentTab === 'analyze' && <AnalyzePage />}
        {currentTab === 'parts' && <PartsPage />}
        {currentTab === 'about' && <AboutPage />}
      </main>

      {/* Global Footer */}
      <Footer />
    </div>
  );
};

export default App;
