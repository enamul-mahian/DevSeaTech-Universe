import { cn } from "../lib/cn";

/**
 * DevSeaTech Universe wordmark + placeholder mark.
 * The official logo asset is swapped in before any branded binary ships
 * (see README). This is an original placeholder, not a copy of another product.
 */
export function BrandMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 48 48"
      className={cn("h-8 w-8", className)}
      role="img"
      aria-label="DevSeaTech Universe"
    >
      <defs>
        <linearGradient id="dst-mark" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="hsl(var(--accent))" />
          <stop offset="1" stopColor="hsl(var(--primary))" />
        </linearGradient>
      </defs>
      <path
        d="M16 12c-6 0-10 4-10 12s4 12 10 12c5 0 8-3 10-8 2 5 5 8 10 8 6 0 10-4 10-12S42 12 36 12c-5 0-8 3-10 8-2-5-5-8-10-8Zm0 6c3 0 5 2 5 6s-2 6-5 6-5-2-5-6 2-6 5-6Zm20 0c3 0 5 2 5 6s-2 6-5 6-5-2-5-6 2-6 5-6Z"
        fill="url(#dst-mark)"
      />
    </svg>
  );
}

export function BrandWordmark({
  className,
  subtitle = true,
}: {
  className?: string;
  subtitle?: boolean;
}) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <BrandMark />
      <span className="leading-none">
        <span className="text-lg font-bold tracking-tight">
          Dev<span className="text-accent">Sea</span>Tech
        </span>
        {subtitle && (
          <span className="block text-[0.6rem] font-medium uppercase tracking-[0.3em] text-muted-foreground">
            Universe
          </span>
        )}
      </span>
    </span>
  );
}
