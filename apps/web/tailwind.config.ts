import type { Config } from "tailwindcss";
import preset from "../../packages/ui/src/tailwind-preset";

export default {
  presets: [preset],
  content: [
    "./src/**/*.{ts,tsx,mdx}",
    "../../packages/ui/src/**/*.{ts,tsx}",
  ],
} satisfies Config;
