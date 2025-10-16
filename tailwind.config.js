/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      boxShadow: {
        glass: 'inset 0 2px 22px 0 rgba(255, 255, 255, 0.6)',
      },
    },
  },
  plugins: [],
}
