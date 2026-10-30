import type { Metadata } from "next";
import { ThemeProvider } from "@devseatech/ui";
import { COMPANY } from "@devseatech/ui";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: `${COMPANY.product} — Secure Multi-Profile Browser Platform`,
    template: `%s · ${COMPANY.product}`,
  },
  description:
    "DevSeaTech Universe is a secure, multi-profile managed browser platform with centralized administration, proxy and privacy controls, and flexible licensing.",
  applicationName: COMPANY.product,
  keywords: [
    "secure browser",
    "multi-profile browser",
    "proxy management",
    "privacy",
    "DevSeaTech",
  ],
  openGraph: {
    type: "website",
    url: siteUrl,
    title: `${COMPANY.product} — Secure Multi-Profile Browser Platform`,
    description: COMPANY.tagline,
    siteName: COMPANY.product,
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-dvh bg-space-gradient font-sans antialiased">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
