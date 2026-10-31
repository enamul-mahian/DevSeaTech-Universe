import type { Metadata } from "next";
import { ThemeProvider, COMPANY } from "@devseatech/ui";
import { PortalShell } from "@/components/portal-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: `My Account · ${COMPANY.product}`,
    template: `%s · ${COMPANY.product}`,
  },
  description: "Manage your DevSeaTech Universe licenses, devices, and account.",
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-dvh bg-space-gradient font-sans antialiased">
        <ThemeProvider>
          <PortalShell>{children}</PortalShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
