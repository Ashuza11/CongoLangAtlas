/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
  // Type checking runs as a separate required command because the current
  // Next.js build worker cannot parse `tsc --showConfig` in this environment.
  typescript: { ignoreBuildErrors: true },
};

export default nextConfig;
