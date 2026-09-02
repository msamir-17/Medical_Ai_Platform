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
        /* Primary Brand Palette — Clinical Teal-Blue */
        'primary': {
          '50': '#EFF6FF',
          '100': '#DBEAFE',
          '200': '#BFDBFE',
          '400': '#3B82F6',
          '500': '#0F52BA',
          '600': '#0E47A1',
          '700': '#1E3A8A',
        },

        /* Semantic Colors */
        'success': '#16A34A',
        'warning': '#D97706',
        'danger': '#DC2626',
        'info': '#2563EB',

        /* Risk Score Colors */
        'risk': {
          'low': '#16A34A',
          'moderate': '#D97706',
          'high': '#DC2626',
        },

        /* Neutrals — Light Mode */
        'bg': {
          'primary': '#FFFFFF',
          'secondary': '#F8FAFC',
          'tertiary': '#F1F5F9',
        },
        'border': {
          'DEFAULT': '#E2E8F0',
          'strong': '#CBD5E1',
        },
        'text': {
          'primary': '#0F172A',
          'secondary': '#475569',
          'muted': '#94A3B8',
        },

        /* Dark Mode Neutrals */
        'dark': {
          'bg': '#0B0F19',
          'bg-secondary': '#151B26',
          'bg-tertiary': '#1E2638',
          'border': '#262F45',
          'border-strong': '#384563',
          'text': '#F8FAFC',
          'text-secondary': '#94A3B8',
          'text-muted': '#64748B',
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
            boxShadow: '0 0 15px rgba(15, 82, 186, 0.15), 0 0 30px rgba(15, 82, 186, 0.08)',
          },
          '50%': {
            boxShadow: '0 0 25px rgba(15, 82, 186, 0.25), 0 0 50px rgba(15, 82, 186, 0.15)',
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
