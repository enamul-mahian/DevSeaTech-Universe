import type { Metadata } from "next";
import { PageShell } from "@/components/page-shell";

export const metadata: Metadata = { title: "Features" };

export default function FeaturesPage() {
  return (
    <PageShell
      title="Features"
      intro="Full feature detail is managed through the CMS and will be published here. The homepage summarizes the core capabilities."
    />
  );
}
