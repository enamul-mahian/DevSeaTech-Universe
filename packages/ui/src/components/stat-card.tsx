import type { ReactNode } from "react";
import { cn } from "../lib/cn";
import { Card } from "./card";

interface StatCardProps {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  icon?: ReactNode;
  /** Optional 0–100 progress bar under the value. */
  progress?: number;
  className?: string;
}

/** Dashboard summary tile: label, large value, optional hint and progress. */
export function StatCard({
  label,
  value,
  hint,
  icon,
  progress,
  className,
}: StatCardProps) {
  return (
    <Card className={cn("p-5", className)}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="mt-1 text-3xl font-semibold tracking-tight">{value}</p>
          {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
        </div>
        {icon && (
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-md bg-accent/12 text-accent">
            {icon}
          </span>
        )}
      </div>
      {typeof progress === "number" && (
        <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-surface">
          <div
            className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
            style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
          />
        </div>
      )}
    </Card>
  );
}
