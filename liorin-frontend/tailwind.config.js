/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'liorin-black': '#000000',
        'liorin-dark': '#141210',
        'liorin-surface': '#141210',
        'liorin-border': '#2a2622',
        'liorin-text': '#e8e2d4',
        'liorin-muted': '#8a8279',
        'liorin-dim': '#6a6258',
        'liorin-accent': '#e0b078',
        'liorin-accent-soft': '#c9a578',
        'liorin-accent-glow': 'rgba(224, 176, 120, 0.28)',
      },
      fontFamily: {
        display: ['"Noto Serif SC"', '"Source Han Serif"', 'Georgia', 'serif'],
        body: ['Inter', '"Noto Sans SC"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"SF Mono"', 'monospace'],
      },
      letterSpacing: {
        'wide-1': '0.15em',
        'wide-2': '0.2em',
        'wide-3': '0.3em',
      },
      keyframes: {
        'hero-hetu-leave': {
          '0%':   { opacity: '1',   transform: 'translate3d(0,0,0) scale(1) rotate(0deg)' },
          '100%': { opacity: '0',   transform: 'translate3d(0,0,0) scale(0.05) rotate(220deg)' },
        },
        'hero-gua-materialize': {
          '0%':   { opacity: '0',   transform: 'translate3d(0,0,0) scale(0.3)' },
          '60%':  { opacity: '0.65', transform: 'translate3d(0,0,0) scale(0.92)' },
          '100%': { opacity: '1',   transform: 'translate3d(0,0,0) scale(1)' },
        },
        'yao-breathing': {
          '0%':   { opacity: '1',    transform: 'scale(1)',     filter: 'brightness(1)' },
          '50%':  { opacity: '0.65',  transform: 'scale(0.94)',  filter: 'brightness(0.92)' },
          '100%': { opacity: '1',    transform: 'scale(1)',     filter: 'brightness(1)' },
        },
      },
      animation: {
        'hero-hetu-leave':       'hero-hetu-leave 1.8s ease-in forwards',
        'hero-gua-materialize':  'hero-gua-materialize 1.8s cubic-bezier(0.45, 0, 0.25, 1) forwards',
        'yao-breathing':         'yao-breathing 6.6s cubic-bezier(0.45, 0, 0.55, 1) infinite',
      },
    },
  },
  plugins: [],
};
