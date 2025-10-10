import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone', // For Railway deployment
  poweredByHeader: false,
  // Force rebuild for Railway
};

export default nextConfig;
