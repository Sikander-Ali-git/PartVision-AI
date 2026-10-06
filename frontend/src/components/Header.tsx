/**
 * frontend/src/components/Header.tsx
 * Professional automotive software navigation header.
 */

import React, { useState } from 'react';
import { List, X } from '@phosphor-icons/react';

interface HeaderProps {
  activeTab: 'analyze' | 'parts' | 'vehicles' | 'about';
  onSelectTab: (tab: 'analyze' | 'parts' | 'vehicles' | 'about') => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onSelectTab,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems: { id: 'analyze' | 'parts' | 'vehicles' | 'about'; label: string }[] = [
    { id: 'analyze', label: 'Analyze' },
    { id: 'parts', label: 'Parts' },
    { id: 'vehicles', label: 'Vehicles' },
    { id: 'about', label: 'About' },
  ];

  const handleNavClick = (tab: 'analyze' | 'parts' | 'vehicles' | 'about') => {
    onSelectTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <header className="bg-white border-b border-sand-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Product Name */}
          <div className="flex items-center gap-8">
            <button
              onClick={() => handleNavClick('analyze')}
              className="flex items-center gap-2.5 text-left focus:outline-none"
              aria-label="PartVision Home"
            >
              <div className="w-8 h-8 rounded bg-auto-red-500 flex items-center justify-center text-white font-bold text-sm tracking-wider shadow-subtle">
                PV
              </div>
              <div>
                <span className="font-semibold text-sand-900 tracking-tight text-base font-sans">
                  PARTVISION
                </span>
                <span className="hidden sm:inline-block ml-2 text-xs font-mono text-sand-500 font-normal">
                  v0.4.0
                </span>
              </div>
            </button>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-1" aria-label="Main Navigation">
              {navItems.map((item) => {
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id)}
                    className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-sand-100 text-sand-900 font-semibold'
                        : 'text-sand-500 hover:text-sand-900 hover:bg-sand-50'
                    }`}
                  >
                    {item.label}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right: Mobile Toggle */}
          <div className="flex items-center">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-md text-sand-600 hover:text-sand-900 hover:bg-sand-100 focus:outline-none"
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X size={20} /> : <List size={20} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-sand-200 bg-white px-4 pt-2 pb-4 space-y-1 shadow-dropdown">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium ${
                  isActive
                    ? 'bg-sand-100 text-sand-900 font-semibold'
                    : 'text-sand-600 hover:text-sand-900 hover:bg-sand-50'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
