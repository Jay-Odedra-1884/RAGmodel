import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          900: "#0a0a0f",
          800: "#12101e",
          700: "#1e1a36",
          600: "#2d2650",
          purple: "#7c3aed",
          indigo: "#4f46e5",
          glow: "#a855f7",
        },
      },
      backgroundImage: {
        "purple-glow":
          "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(124,58,237,0.3), transparent)",
      },
      animation: {
        pulse_slow: "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow": "spin 3s linear infinite",
      },
    },
  },
  plugins: [],
};
export default config;
