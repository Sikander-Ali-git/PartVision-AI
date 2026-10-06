/**
 * frontend/src/components/Header.tsx
 * Top navigation bar with branding, navigation links, and live API status indicator.
 */

import React from 'react';
import { ShieldCheck, Cpu, Car, Info } from '@phosphor-icons/react';

interface HeaderProps {
  currentTab: 'analyze' | 'parts' | 'about';
  onSelectTab: (tab: 'analyze' | 'parts' | 'about') => void;
  isApiOnline: boolean;
  apiChecking: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onSelectTab,
  isApiOnline,
  apiChecking,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-graphite-950/80 backdrop-blur-md border-b border-graphite-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => onSelectTab('analyze')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400/20 to-electric-500/20 border border-cyan-400/40 flex items-center justify-center shadow-glow-cyan/50">
            <Cpu size={22} weight="duotone" className="text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-wider text-white">PARTVISION</span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-cyan-400/10 border border-cyan-400/30 text-cyan-400 font-mono font-medium">
                AI v0.4
              </span>
            </div>
            <p className="text-xs text-graphite-400 hidden sm:block">Automotive Spare-Part Intelligence</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <button
            onClick={() => onSelectTab('analyze')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentTab === 'analyze'
                ? 'bg-graphite-850 text-cyan-400 border border-cyan-400/30 shadow-sm'
                : 'text-graphite-400 hover:text-white hover:bg-graphite-900'
            }`}
          >
            <Car size={18} weight={currentTab === 'analyze' ? 'fill' : 'regular'} />
            <span>Analyze</span>
          </button>

          <button
            onClick={() => onSelectTab('parts')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentTab === 'parts'
                ? 'bg-graphite-850 text-cyan-400 border border-cyan-400/30 shadow-sm'
                : 'text-graphite-400 hover:text-white hover:bg-graphite-900'
            }`}
          >
            <ShieldCheck size={18} weight={currentTab === 'parts' ? 'fill' : 'regular'} />
            <span>Parts Catalog</span>
          </button>

          <button
            onClick={() => onSelectTab('about')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentTab === 'about'
                ? 'bg-graphite-850 text-cyan-400 border border-cyan-400/30 shadow-sm'
                : 'text-graphite-400 hover:text-white hover:bg-graphite-900'
            }`}
          >
            <Info size={18} weight={currentTab === 'about' ? 'fill' : 'regular'} />
            <span>About</span>
          </button>
        </nav>

        {/* Status Badge */}
        <div className="flex items-center gap-2">
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border ${
              isApiOnline
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : apiChecking
                ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400'
                : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isApiOnline
                  ? 'bg-emerald-400 animate-pulse'
                  : apiChecking
                  ? 'bg-yellow-400 animate-ping'
                  : 'bg-rose-500'
              }`}
            />
            <span className="hidden sm:inline">
              {isApiOnline ? 'API Online' : apiChecking ? 'Connecting...' : 'API Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
