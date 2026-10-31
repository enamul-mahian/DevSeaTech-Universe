import type { Metadata } from "next";
import { Card, CardContent } from "@devseatech/ui";
import { PageShell } from "@/components/page-shell";

export const metadata: Metadata = { title: "Documentation" };

const DOC_SECTIONS = [
  {
    title: "Getting Started",
    description:
      "Install DevSeaTech Universe, set up your master password, and create your first browser profile.",
    status: "Available",
  },
  {
    title: "Profile Management",
    description:
      "Create, import, export, clone, and manage isolated browser profiles with backup and health checks.",
    status: "Available",
  },
  {
    title: "Security & Privacy",
    description:
      "Configure privacy modes, password vault, permissions, and audit logging for secure browsing.",
    status: "Available",
  },
  {
    title: "Licensing & Devices",
    description:
      "Understand device-based licensing, trial terms, renewal, and server-authoritative activation.",
    status: "Available",
  },
  {
    title: "Administration",
    description:
      "Admin dashboard, role-based controls, update policies, and platform configuration.",
    status: "Coming soon",
  },
  {
    title: "API Reference",
    description:
      "REST API endpoints for license management, device enrollment, and plan configuration.",
    status: "Coming soon",
  },
];

export default function DocsPage() {
  return (
    <PageShell
      title="Documentation"
      intro="Guides, references, and policy documents for DevSeaTech Universe."
    >
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {DOC_SECTIONS.map((doc) => (
          <Card key={doc.title}>
            <CardContent className="flex flex-col gap-3 pt-6">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">{doc.title}</h2>
                <span
                  className={`text-xs ${
                    doc.status === "Available"
                      ? "text-accent"
                      : "text-muted-foreground"
                  }`}
                >
                  {doc.status}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                {doc.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </PageShell>
  );
}
