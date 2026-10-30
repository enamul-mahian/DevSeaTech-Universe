import type { ReactNode } from "react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export function PageShell({
  title,
  intro,
  children,
}: {
  title: string;
  intro?: string;
  children?: ReactNode;
}) {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <h1 className="text-4xl font-bold tracking-tight">{title}</h1>
        {intro && (
          <p className="mt-4 max-w-2xl text-lg text-muted-foreground">{intro}</p>
        )}
        <div className="mt-10">{children}</div>
      </main>
      <SiteFooter />
    </>
  );
}
