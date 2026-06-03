/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    container: {
      center: true,
      padding: '1rem',
      screens: {
        '2xl': '1400px'
      }
    },
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a'
        },
        bg2: '#0b1220',
        panel: {
          1: 'rgba(17, 24, 39, 0.72)',
          2: 'rgba(31, 41, 55, 0.55)'
        }
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(59, 130, 246, 0.25), 0 10px 40px rgba(0, 0, 0, 0.5)',
        soft: '0 8px 30px rgba(0,0,0,0.35)'
      },
      borderRadius: {
        xl: '1rem'
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' }
        }
      },
      animation: {
        shimmer: 'shimmer 1.2s ease-in-out infinite'
      }
    }
  },
  plugins: []
};

