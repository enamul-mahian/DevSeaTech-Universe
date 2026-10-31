/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@devseatech/ui", "@devseatech/contracts"],
  output: "standalone",
};

export default nextConfig;
