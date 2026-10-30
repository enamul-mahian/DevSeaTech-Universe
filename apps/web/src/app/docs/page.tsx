import type { Metadata } from "next";
import { PageShell } from "@/components/page-shell";

export const metadata: Metadata = { title: "Documentation" };

export default function DocsPage() {
  return (
    <PageShell
      title="Documentation"
      intro="Product documentation, setup guides and policy references will be published here through the CMS."
    />
  );
}
