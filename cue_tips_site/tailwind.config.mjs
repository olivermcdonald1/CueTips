/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
          dark: '#212227', // #212227
          iris: '#5D3FD3', // #5D3FD3
          poolGreen: '#0A6C03', // #0A6C03
          lightGray: '#CFCFCF', // #CFCFCF
      },
      fontFamily: {
        cakra: ['Cakra-Normal']
      },
    }
  },
  plugins: [],
};
