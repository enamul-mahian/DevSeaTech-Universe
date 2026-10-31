"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrandWordmark, ThemeToggle, cn } from "@devseatech/ui";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "◎" },
  { href: "/licenses", label: "Licenses", icon: "◈" },
  { href: "/devices", label: "Devices", icon: "◉" },
  { href: "/plans", label: "Plans", icon: "✧" },
  { href: "/customers", label: "Customers", icon: "◷" },
  { href: "/settings", label: "Settings", icon: "⛉" },
] as const;

export function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-dvh">
      {/* Sidebar */}
      <aside className="hidden w-64 flex-col border-r border-white/10 bg-black/30 backdrop-blur-lg md:flex">
        <div className="flex h-14 items-center gap-2 border-b border-white/10 px-4">
          <BrandWordmark className="h-6" />
          <span className="text-xs text-muted-foreground">Admin</span>
        </div>
        <nav className="flex-1 space-y-1 px-2 py-3">
          {NAV_ITEMS.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-accent/12 text-accent"
                    : "text-muted-foreground hover:bg-white/5 hover:text-foreground",
                )}
              >
                <span aria-hidden className="text-base">
                  {item.icon}
                </span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/10 p-4">
          <ThemeToggle />
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        {/* Mobile header */}
        <header className="flex h-14 items-center justify-between border-b border-white/10 px-4 md:hidden">
          <BrandWordmark className="h-5" />
          <ThemeToggle />
        </header>
        <main className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
