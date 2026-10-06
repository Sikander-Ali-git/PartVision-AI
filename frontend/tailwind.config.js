/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: '#090b10',
          900: '#11131a',
          850: '#161922',
          800: '#1c202c',
          700: '#282e3f',
          600: '#424a60',
          400: '#7e89a4',
          300: '#a4afc7',
          100: '#e2e7f3',
        },
        cyan: {
          400: '#00f0ff',
          500: '#00d2e0',
          900: '#00333d',
        },
        electric: {
          500: '#0066ff',
          600: '#0052cc',
          900: '#001a40',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        'glow-cyan': '0 0 20px -5px rgba(0, 240, 255, 0.3)',
        'glow-blue': '0 0 20px -5px rgba(0, 102, 255, 0.3)',
      },
    },
  },
  plugins: [],
}
