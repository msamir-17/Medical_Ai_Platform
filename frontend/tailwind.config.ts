import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './features/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        /* Primary Brand Palette */
        'primary': {
          '50': '#EEF2FF',
          '100': '#E0E7FF',
          '200': '#C7D2FE',
          '400': '#818CF8',
          '500': '#6366F1',
          '600': '#4F46E5',
          '700': '#4338CA',
        },

        /* Semantic Colors */
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'info': '#3B82F6',

        /* Risk Score Colors */
        'risk': {
          'low': '#10B981',
          'moderate': '#F59E0B',
          'high': '#EF4444',
        },

        /* Neutrals — Light Mode */
        'bg': {
          'primary': '#FFFFFF',
          'secondary': '#F9FAFB',
          'tertiary': '#F3F4F6',
        },
        'border': {
          'DEFAULT': '#E5E7EB',
          'strong': '#D1D5DB',
        },
        'text': {
          'primary': '#111827',
          'secondary': '#6B7280',
          'muted': '#9CA3AF',
        },

        /* Dark Mode Neutrals */
        'dark': {
          'bg': '#0F1117',
          'bg-secondary': '#1A1D27',
          'bg-tertiary': '#22263A',
          'border': '#2D3147',
          'border-strong': '#3D4266',
          'text': '#F9FAFB',
          'text-secondary': '#9CA3AF',
          'text-muted': '#6B7280',
        },
      },

      spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
        '20': '80px',
        '24': '96px',
      },

      fontSize: {
        'xs': ['0.75rem', '1.0rem'],
        'sm': ['0.875rem', '1.25rem'],
        'base': ['1rem', '1.5rem'],
        'lg': ['1.125rem', '1.75rem'],
        'xl': ['1.25rem', '1.75rem'],
        '2xl': ['1.5rem', '2rem'],
        '3xl': ['1.875rem', '2.25rem'],
        '4xl': ['2.25rem', '2.5rem'],
      },

      borderRadius: {
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '20px',
      },

      animation: {
        'float-slow': 'float-slow 6s ease-in-out infinite',
        'float-medium': 'float-medium 4.5s ease-in-out infinite',
        'float-fast': 'float-fast 5s ease-in-out infinite',
        'float-delayed': 'float-slow 5.5s ease-in-out infinite 0.8s',
        'pulse-glow': 'pulse-glow 3s ease-in-out infinite',
        'score-fill': 'score-fill 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards',
      },

      keyframes: {
        'float-slow': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        'float-medium': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'float-fast': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-glow': {
          '0%, 100%': {
            boxShadow: '0 0 15px rgba(99, 102, 241, 0.15), 0 0 30px rgba(6, 182, 212, 0.08)',
          },
          '50%': {
            boxShadow: '0 0 25px rgba(99, 102, 241, 0.25), 0 0 50px rgba(6, 182, 212, 0.15)',
          },
        },
        'score-fill': {
          'from': { strokeDashoffset: '264' },
        },
      },

      transitionDuration: {
        'fast': '100ms',
        'normal': '200ms',
        'slow': '350ms',
        'enter': '400ms',
      },

      transitionTimingFunction: {
        'ease-default': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'ease-spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'ease-out': 'cubic-bezier(0, 0, 0.2, 1)',
      },

      boxShadow: {
        'card': '0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04)',
        'card-hover': '0 4px 12px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  plugins: [],
};

export default config;
