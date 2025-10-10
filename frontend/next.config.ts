import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone', // For Railway deployment
  poweredByHeader: false,
  // Force rebuild for Railway - v3 with relative imports only
};

export default nextConfig;
