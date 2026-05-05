/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'fin-dark': '#0a0a0f',
        'fin-card': '#151520',
        'fin-accent': '#00d4ff',
        'fraud-red': '#ff4757',
        'legit-green': '#2ed573',
      },
    },
  },
  plugins: [],
}
