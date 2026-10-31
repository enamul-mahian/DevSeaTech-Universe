import type { Metadata } from "next";
import { ThemeProvider, COMPANY } from "@devseatech/ui";
import { AdminShell } from "@/components/admin-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: `Admin · ${COMPANY.product}`,
    template: `%s · Admin · ${COMPANY.product}`,
  },
  description: "DevSeaTech Universe super-admin dashboard.",
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
          <AdminShell>{children}</AdminShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
