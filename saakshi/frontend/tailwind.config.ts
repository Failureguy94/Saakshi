import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        bg: '#0A0E14',
        surface: '#111826',
        border: '#1F2A3D',
        text: '#E6EDF7',
        muted: '#8A99B3',
        accent: '#2DD4BF',
        indigo: '#6366F1',
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      borderRadius: {
        xl: '12px',
      },
    },
  },
  plugins: [],
} satisfies Config;
