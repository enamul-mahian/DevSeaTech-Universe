"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { cn } from "../lib/cn";

type Mode = "light" | "dark" | "system";

const MODES: { value: Mode; label: string; glyph: string }[] = [
  { value: "light", label: "Light", glyph: "☀" },
  { value: "dark", label: "Dark", glyph: "☾" },
  { value: "system", label: "Auto", glyph: "⌁" },
];

/**
 * Segmented Dark / Light / Auto control.
 * Renders a stable placeholder until mounted to avoid a hydration mismatch
 * (the resolved theme is only known on the client).
 */
export function ThemeToggle({ className }: { className?: string }) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const current: Mode = (mounted ? (theme as Mode) : "dark") ?? "dark";

  return (
    <div
      role="radiogroup"
      aria-label="Color theme"
      className={cn(
        "inline-flex items-center gap-0.5 rounded-full border border-border bg-surface/60 p-0.5",
        className,
      )}
    >
      {MODES.map((mode) => {
        const active = current === mode.value;
        return (
          <button
            key={mode.value}
            type="button"
            role="radio"
            aria-checked={active}
            title={mode.label}
            onClick={() => setTheme(mode.value)}
            className={cn(
              "flex h-7 items-center gap-1 rounded-full px-2.5 text-xs font-medium transition-colors",
              active
                ? "bg-primary/90 text-primary-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            <span aria-hidden>{mode.glyph}</span>
            <span className="hidden sm:inline">{mode.label}</span>
          </button>
        );
      })}
    </div>
  );
}
