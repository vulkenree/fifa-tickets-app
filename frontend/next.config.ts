import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone', // For Railway deployment
  poweredByHeader: false,
};

export default nextConfig;
