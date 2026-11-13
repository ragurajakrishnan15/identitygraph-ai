import type { Config } from "tailwindcss";

const v = (name: string) => `rgb(var(--${name}) / <alpha-value>)`;

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: v("bg"), surface: v("surface"), fill: v("fill"), line: v("line"),
        ink: v("ink"), muted: v("muted"), subtle: v("subtle"),
        accent: { DEFAULT: v("accent"), soft: v("accent") },
        safe: v("safe"), warn: v("warn"), danger: v("danger"),
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"SF Pro Text"', 'Inter', '"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      },
      letterSpacing: { tightest: "-0.045em" },
      boxShadow: {
        card: "0 1px 2px rgb(0 0 0 / 0.04), 0 8px 30px rgb(0 0 0 / 0.04)",
        lift: "0 2px 4px rgb(0 0 0 / 0.04), 0 18px 50px rgb(0 0 0 / 0.10)",
      },
    },
  },
  plugins: [],
};
export default config;
