import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow LAN access to dev server HMR (for http://192.168.x.x access)
  allowedDevOrigins: ["192.168.29.240"],

  output: "export",
  images: {
    unoptimized: true,
  },
  // Silence workspace root detection warning
  turbopack: {
    root: __dirname,
  },

  async redirects() {
    return [
      {
        source: '/knowledge-graph',
        destination: '/graph',
        permanent: true,
      },
      {
        source: '/evidence-library',
        destination: '/evidence',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
