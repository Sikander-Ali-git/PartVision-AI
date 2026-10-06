/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sand: {
          50: '#F6F6F3',
          100: '#F0F0EC',
          200: '#E3E3DF',
          300: '#D1D1CB',
          400: '#A8A8A2',
          500: '#6B6B68',
          600: '#4A4A47',
          700: '#2E2E2C',
          800: '#1F1F1D',
          900: '#151515',
        },
        auto: {
          red: {
            50: '#FDF2F0',
            100: '#FCE4E1',
            200: '#F8C8C1',
            300: '#F19F94',
            400: '#E66F5F',
            500: '#D6452D', // Primary accent
            600: '#BD3822',
            700: '#9E2C19',
            800: '#7E2516',
            900: '#682217',
          },
          green: {
            50: '#EDF7F2',
            100: '#D7EFE2',
            500: '#18794E', // Success
            600: '#12603D',
            700: '#0F4D31',
          },
          amber: {
            50: '#FFF9EB',
            100: '#FEF0CE',
            500: '#A66A00', // Warning
            600: '#875600',
            700: '#684200',
          },
          rose: {
            50: '#FEF3F2',
            100: '#FEE4E2',
            500: '#B42318', // Error
            600: '#911B13',
            700: '#73160F',
          },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)',
        dropdown: '0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05)',
        modal: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}
