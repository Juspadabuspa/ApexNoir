/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      '../backend/src/**/*.py', // optionally scan backend templates
      './pages/**/*.{js,ts,jsx,tsx}',
      './components/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
      extend: {
        colors: {
          black: '#000000',
          gold: '#D4AF37',
          // you can dynamically add team colors in your components
        },
      },
    },
    plugins: [],
  }
  