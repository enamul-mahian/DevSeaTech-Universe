import type { Metadata } from "next";
import { Card, CardContent } from "@devseatech/ui";
import { PageShell } from "@/components/page-shell";

export const metadata: Metadata = { title: "Download" };

export default function DownloadPage() {
  return (
    <PageShell
      title="Download"
      intro="DevSeaTech Universe runs on Windows and Linux. Signed installers are published only from approved, verified releases."
    >
      <div className="grid gap-5 sm:grid-cols-2">
        {["Windows", "Linux"].map((os) => (
          <Card key={os}>
            <CardContent className="pt-6">
              <h2 className="text-lg font-semibold">{os}</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Download links appear here once a signed release is published.
                Builds are verified before install; a git push never triggers an
                update.
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </PageShell>
  );
}
