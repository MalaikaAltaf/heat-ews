/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          sidebar: "#0f231f",
          sidebarHover: "#183630",
          sidebarActive: "#20463e",
          canvas: "#f7f5f1",
          card: "#ffffff",
          border: "#e6e3dd",
          orange: "#d9653b",
          green: "#2d6a4f",
          amber: "#d99b26",
          darkText: "#182622",
          mutedText: "#687a74"
        }
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      }
    },
  },
  plugins: [],
}

