import Link from "next/link";
import {
  Badge,
  Button,
  Card,
  CardContent,
  Starfield,
  COMPANY,
} from "@devseatech/ui";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

const FEATURES = [
  {
    title: "Multi-Profile System",
    body: "Isolated cookies, cache, storage, history and identity for every profile. One master login opens them all.",
    glyph: "◎",
  },
  {
    title: "Proxies & Privacy",
    body: "HTTP, HTTPS and SOCKS5 per profile, with privacy modes from Standard to Strict.",
    glyph: "◉",
  },
  {
    title: "Engine Management",
    body: "Multi-version Chromium runtime selection, installed and removed under administrator policy.",
    glyph: "✧",
  },
  {
    title: "Session Time Control",
    body: "Server-authoritative session duration and timezone-based allowed-hours, managed centrally.",
    glyph: "◷",
  },
  {
    title: "Device Licensing",
    body: "One license per authorized device, 30-day standard terms, trials, renewal and revocation.",
    glyph: "◈",
  },
  {
    title: "Admin-Controlled",
    body: "Role-based control over settings, extensions, policies and engine changes, with audit trails.",
    glyph: "⛉",
  },
];

const STATS = [
  { value: "148+", label: "Chromium engine support" },
  { value: "30d", label: "Standard license term" },
  { value: "3", label: "Privacy modes + custom" },
  { value: "100%", label: "English-only interface" },
];

export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main>
        {/* Hero */}
        <section className="relative overflow-hidden">
          <Starfield />
          <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 sm:py-32">
            <div className="max-w-3xl animate-fade-up">
              <Badge tone="accent" className="mb-6">
                <span className="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden />
                {COMPANY.tagline}
              </Badge>
              <h1 className="text-balance text-5xl font-bold leading-[1.05] tracking-tight sm:text-6xl">
                Your all-in-one{" "}
                <span className="neon-text">secure browser</span> platform
              </h1>
              <p className="mt-6 max-w-2xl text-lg text-muted-foreground">
                {COMPANY.product} delivers multi-profile browsing with
                centralized administration, proxy and privacy controls, and
                flexible device licensing — built for teams that take privacy
                seriously.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link href="/download">
                  <Button size="lg">Download the browser</Button>
                </Link>
                <Link href="/pricing">
                  <Button size="lg" variant="outline">
                    View pricing
                  </Button>
                </Link>
              </div>
              <dl className="mt-14 grid max-w-2xl grid-cols-2 gap-6 sm:grid-cols-4">
                {STATS.map((s) => (
                  <div key={s.label}>
                    <dt className="sr-only">{s.label}</dt>
                    <dd className="text-2xl font-semibold text-accent">
                      {s.value}
                    </dd>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {s.label}
                    </p>
                  </div>
                ))}
              </dl>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="max-w-2xl">
            <h2 className="text-3xl font-bold tracking-tight">
              Built for secure, managed browsing
            </h2>
            <p className="mt-3 text-muted-foreground">
              Every capability is role-controlled and auditable, from profile
              isolation to engine policy.
            </p>
          </div>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => (
              <Card key={f.title}>
                <CardContent className="pt-5">
                  <span
                    className="grid h-11 w-11 place-items-center rounded-md bg-accent/12 text-xl text-accent"
                    aria-hidden
                  >
                    {f.glyph}
                  </span>
                  <h3 className="mt-4 text-lg font-semibold">{f.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{f.body}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="mx-auto max-w-7xl px-4 pb-24 sm:px-6">
          <Card className="relative overflow-hidden">
            <Starfield />
            <CardContent className="relative flex flex-col items-start gap-5 p-10 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">
                  Ready to take control of your browsing?
                </h2>
                <p className="mt-2 text-muted-foreground">
                  Start a trial or activate a license from the desktop app.
                </p>
              </div>
              <Link href="/download">
                <Button size="lg">Get {COMPANY.product}</Button>
              </Link>
            </CardContent>
          </Card>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
