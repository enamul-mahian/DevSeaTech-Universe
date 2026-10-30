/**
 * DevSeaTech Universe raw design tokens.
 *
 * These are the canonical brand values. The CSS custom properties in
 * `styles/globals.css` and the Tailwind preset both derive from this palette,
 * so there is a single source of truth. JS/Canvas consumers (e.g. the
 * starfield) import the raw values from here.
 */

export const brand = {
  // Deep space backgrounds (dark theme).
  space900: "#02091c",
  space800: "#030d22",
  space700: "#06142b",
  space600: "#09162c",
  surface: "#102341",
  // Neon accents (restrained — used for emphasis, never whole surfaces).
  neonCyan: "#36e6ff",
  neonBlue: "#15c9ff",
  blue500: "#078ad6",
  blue600: "#036bcb",
  // Foregrounds.
  textPrimary: "#e4f7ff",
  textSecondary: "#afcce6",
  textMuted: "#7192b5",
} as const;

/** Status colors used across the admin dashboard (running / stopped, etc.). */
export const status = {
  running: "#34d399",
  stopped: "#f87171",
  warning: "#fbbf24",
  info: "#38bdf8",
} as const;

/**
 * Starfield rendering parameters. Kept here so motion can be tuned in one
 * place and so both the React component and any tests share the same numbers.
 */
export const starfield = {
  /** Stars per 100k px² of canvas — keeps density consistent across sizes. */
  densityPer100kPx: 6,
  maxStars: 220,
  twinkleSpeed: 0.0006,
  shootingStarIntervalMs: 4200,
  shootingStarCount: 2,
} as const;

export type Brand = typeof brand;
export type StatusColor = keyof typeof status;
