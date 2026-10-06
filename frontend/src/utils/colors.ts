/**
 * frontend/src/utils/colors.ts
 * Visual color palette and styling utilities for the 19 PartVision taxonomy classes.
 */

export interface PartColor {
  hex: string;
  rgb: string;
  border: string;
  fill: string;
  text: string;
}

export const PART_COLORS: Record<string, PartColor> = {
  back_bumper: {
    hex: '#ef4444',
    rgb: '239, 68, 68',
    border: 'border-red-500',
    fill: 'rgba(239, 68, 68, 0.25)',
    text: 'text-red-400',
  },
  back_door: {
    hex: '#10b981',
    rgb: '16, 185, 129',
    border: 'border-emerald-500',
    fill: 'rgba(16, 185, 129, 0.25)',
    text: 'text-emerald-400',
  },
  back_glass: {
    hex: '#eab308',
    rgb: '234, 179, 8',
    border: 'border-yellow-500',
    fill: 'rgba(234, 179, 8, 0.25)',
    text: 'text-yellow-400',
  },
  back_light: {
    hex: '#3b82f6',
    rgb: '59, 130, 246',
    border: 'border-blue-500',
    fill: 'rgba(59, 130, 246, 0.25)',
    text: 'text-blue-400',
  },
  fender: {
    hex: '#f97316',
    rgb: '249, 115, 22',
    border: 'border-orange-500',
    fill: 'rgba(249, 115, 22, 0.25)',
    text: 'text-orange-400',
  },
  front_bumper: {
    hex: '#a855f7',
    rgb: '168, 85, 247',
    border: 'border-purple-500',
    fill: 'rgba(168, 85, 247, 0.25)',
    text: 'text-purple-400',
  },
  front_door: {
    hex: '#06b6d4',
    rgb: '6, 182, 212',
    border: 'border-cyan-500',
    fill: 'rgba(6, 182, 212, 0.25)',
    text: 'text-cyan-400',
  },
  front_glass: {
    hex: '#ec4899',
    rgb: '236, 72, 153',
    border: 'border-pink-500',
    fill: 'rgba(236, 72, 153, 0.25)',
    text: 'text-pink-400',
  },
  front_light: {
    hex: '#84cc16',
    rgb: '132, 204, 22',
    border: 'border-lime-500',
    fill: 'rgba(132, 204, 22, 0.25)',
    text: 'text-lime-400',
  },
  grille: {
    hex: '#f43f5e',
    rgb: '244, 63, 94',
    border: 'border-rose-500',
    fill: 'rgba(244, 63, 94, 0.25)',
    text: 'text-rose-400',
  },
  hood: {
    hex: '#14b8a6',
    rgb: '20, 184, 166',
    border: 'border-teal-500',
    fill: 'rgba(20, 184, 166, 0.25)',
    text: 'text-teal-400',
  },
  mirror: {
    hex: '#c084fc',
    rgb: '192, 132, 252',
    border: 'border-purple-400',
    fill: 'rgba(192, 132, 252, 0.25)',
    text: 'text-purple-300',
  },
  quarter_panel: {
    hex: '#d97706',
    rgb: '217, 119, 6',
    border: 'border-amber-600',
    fill: 'rgba(217, 119, 6, 0.25)',
    text: 'text-amber-500',
  },
  rocker_panel: {
    hex: '#fde047',
    rgb: '253, 224, 71',
    border: 'border-yellow-300',
    fill: 'rgba(253, 224, 71, 0.25)',
    text: 'text-yellow-300',
  },
  roof: {
    hex: '#b91c1c',
    rgb: '185, 28, 28',
    border: 'border-red-700',
    fill: 'rgba(185, 28, 28, 0.25)',
    text: 'text-red-300',
  },
  side_window: {
    hex: '#6ee7b7',
    rgb: '110, 231, 183',
    border: 'border-emerald-300',
    fill: 'rgba(110, 231, 183, 0.25)',
    text: 'text-emerald-300',
  },
  tailgate: {
    hex: '#ca8a04',
    rgb: '202, 138, 4',
    border: 'border-yellow-600',
    fill: 'rgba(202, 138, 4, 0.25)',
    text: 'text-yellow-500',
  },
  trunk: {
    hex: '#fdba74',
    rgb: '253, 186, 116',
    border: 'border-orange-300',
    fill: 'rgba(253, 186, 116, 0.25)',
    text: 'text-orange-300',
  },
  wheel: {
    hex: '#00f0ff',
    rgb: '0, 240, 255',
    border: 'border-cyan-400',
    fill: 'rgba(0, 240, 255, 0.25)',
    text: 'text-cyan-400',
  },
};

const DEFAULT_COLOR: PartColor = {
  hex: '#00f0ff',
  rgb: '0, 240, 255',
  border: 'border-cyan-400',
  fill: 'rgba(0, 240, 255, 0.25)',
  text: 'text-cyan-400',
};

export function getPartColor(partName: string): PartColor {
  return PART_COLORS[partName.toLowerCase()] || DEFAULT_COLOR;
}
