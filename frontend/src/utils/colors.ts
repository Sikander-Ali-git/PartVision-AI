/**
 * frontend/src/utils/colors.ts
 * Clean, technical color palette for automotive components.
 * Prioritizes high legibility against photography without neon glare.
 */

export interface PartColor {
  hex: string;
  rgb: string;
  fill: string;
  stroke: string;
  tagBg: string;
  tagText: string;
}

export const PART_COLORS: Record<string, PartColor> = {
  back_bumper: {
    hex: '#C0392B',
    rgb: '192, 57, 43',
    fill: 'rgba(192, 57, 43, 0.18)',
    stroke: '#C0392B',
    tagBg: '#FDF2F0',
    tagText: '#9E2C19',
  },
  back_door: {
    hex: '#1E7E34',
    rgb: '30, 126, 52',
    fill: 'rgba(30, 126, 52, 0.18)',
    stroke: '#1E7E34',
    tagBg: '#EDF7F2',
    tagText: '#12603D',
  },
  back_glass: {
    hex: '#D97706',
    rgb: '217, 119, 6',
    fill: 'rgba(217, 119, 6, 0.18)',
    stroke: '#D97706',
    tagBg: '#FFF9EB',
    tagText: '#875600',
  },
  back_light: {
    hex: '#B91C1C',
    rgb: '185, 28, 28',
    fill: 'rgba(185, 28, 28, 0.18)',
    stroke: '#B91C1C',
    tagBg: '#FEF3F2',
    tagText: '#911B13',
  },
  fender: {
    hex: '#EA580C',
    rgb: '234, 88, 12',
    fill: 'rgba(234, 88, 12, 0.18)',
    stroke: '#EA580C',
    tagBg: '#FFF4ED',
    tagText: '#9A3412',
  },
  front_bumper: {
    hex: '#D6452D', // Primary Automotive Red
    rgb: '214, 69, 45',
    fill: 'rgba(214, 69, 45, 0.22)',
    stroke: '#D6452D',
    tagBg: '#FDF2F0',
    tagText: '#BD3822',
  },
  front_door: {
    hex: '#0284C7',
    rgb: '2, 132, 199',
    fill: 'rgba(2, 132, 199, 0.18)',
    stroke: '#0284C7',
    tagBg: '#F0F9FF',
    tagText: '#0369A1',
  },
  front_glass: {
    hex: '#0D9488',
    rgb: '13, 148, 136',
    fill: 'rgba(13, 148, 136, 0.18)',
    stroke: '#0D9488',
    tagBg: '#F0FDFA',
    tagText: '#0F766E',
  },
  front_light: {
    hex: '#CA8A04',
    rgb: '202, 138, 4',
    fill: 'rgba(202, 138, 4, 0.18)',
    stroke: '#CA8A04',
    tagBg: '#FEFCE8',
    tagText: '#854D0E',
  },
  grille: {
    hex: '#475569',
    rgb: '71, 85, 105',
    fill: 'rgba(71, 85, 105, 0.20)',
    stroke: '#475569',
    tagBg: '#F1F5F9',
    tagText: '#334155',
  },
  hood: {
    hex: '#059669',
    rgb: '5, 150, 105',
    fill: 'rgba(5, 150, 105, 0.18)',
    stroke: '#059669',
    tagBg: '#ECFDF5',
    tagText: '#047857',
  },
  mirror: {
    hex: '#7C3AED',
    rgb: '124, 58, 237',
    fill: 'rgba(124, 58, 237, 0.18)',
    stroke: '#7C3AED',
    tagBg: '#F5F3FF',
    tagText: '#6D28D9',
  },
  quarter_panel: {
    hex: '#B45309',
    rgb: '180, 83, 9',
    fill: 'rgba(180, 83, 9, 0.18)',
    stroke: '#B45309',
    tagBg: '#FFFBEB',
    tagText: '#92400E',
  },
  rocker_panel: {
    hex: '#65A30D',
    rgb: '101, 163, 13',
    fill: 'rgba(101, 163, 13, 0.18)',
    stroke: '#65A30D',
    tagBg: '#F7FEE7',
    tagText: '#4D7C0F',
  },
  roof: {
    hex: '#4F46E5',
    rgb: '79, 70, 229',
    fill: 'rgba(79, 70, 229, 0.18)',
    stroke: '#4F46E5',
    tagBg: '#EEF2FF',
    tagText: '#4338CA',
  },
  side_window: {
    hex: '#0891B2',
    rgb: '8, 145, 178',
    fill: 'rgba(8, 145, 178, 0.18)',
    stroke: '#0891B2',
    tagBg: '#ECFEFF',
    tagText: '#0E7490',
  },
  tailgate: {
    hex: '#9333EA',
    rgb: '147, 51, 234',
    fill: 'rgba(147, 51, 234, 0.18)',
    stroke: '#9333EA',
    tagBg: '#FAF5FF',
    tagText: '#7E22CE',
  },
  trunk: {
    hex: '#C2410C',
    rgb: '194, 65, 12',
    fill: 'rgba(194, 65, 12, 0.18)',
    stroke: '#C2410C',
    tagBg: '#FFF7ED',
    tagText: '#9A3412',
  },
  wheel: {
    hex: '#334155',
    rgb: '51, 65, 85',
    fill: 'rgba(51, 65, 85, 0.22)',
    stroke: '#334155',
    tagBg: '#F8FAFC',
    tagText: '#1E293B',
  },
};

const DEFAULT_COLOR: PartColor = {
  hex: '#D6452D',
  rgb: '214, 69, 45',
  fill: 'rgba(214, 69, 45, 0.20)',
  stroke: '#D6452D',
  tagBg: '#FDF2F0',
  tagText: '#BD3822',
};

export function getPartColor(partName: string): PartColor {
  return PART_COLORS[partName.toLowerCase()] || DEFAULT_COLOR;
}
