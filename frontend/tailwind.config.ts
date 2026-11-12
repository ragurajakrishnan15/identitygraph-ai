import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: { 950: "#070b18", 900: "#0b1226", 800: "#111a33", 700: "#1a2547", 600: "#26335e" },
        accent: { DEFAULT: "#7c6cf6", soft: "#a79bff" },
        safe: "#2dd4bf",
        warn: "#fbbf24",
        danger: "#fb7185",
      },
    },
  },
  plugins: [],
};
export default config;
