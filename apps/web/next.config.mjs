/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The design system and contracts ship as TypeScript source; Next transpiles them.
  transpilePackages: ["@devseatech/ui", "@devseatech/contracts"],
  env: {
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  },
};

export default nextConfig;
