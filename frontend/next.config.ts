import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone', // For Railway deployment
  poweredByHeader: false,
  // Force rebuild for Railway - v2 with explicit webpack aliases
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Explicitly resolve path aliases for Railway Docker builds
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
      '@/lib': path.resolve(__dirname, 'lib'),
      '@/components': path.resolve(__dirname, 'components'),
      '@/hooks': path.resolve(__dirname, 'hooks'),
      '@/app': path.resolve(__dirname, 'app'),
    };
    return config;
  },
};

export default nextConfig;
