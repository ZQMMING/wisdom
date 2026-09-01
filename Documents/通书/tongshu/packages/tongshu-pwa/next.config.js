/** @type {import('next').NextConfig} */
const nextConfig = {
  images: { unoptimized: true },
  async rewrites() {
    return [
      { source: "/daily/:path*", destination: "http://localhost:8000/daily/:path*" },
      { source: "/daily", destination: "http://localhost:8000/daily" },
      { source: "/profiles/:path*", destination: "http://localhost:8000/profiles/:path*" },
      { source: "/profiles", destination: "http://localhost:8000/profiles" },
      { source: "/calendar/:path*", destination: "http://localhost:8000/calendar/:path*" },
      { source: "/nfc/:path*", destination: "http://localhost:8000/nfc/:path*" },
      { source: "/health", destination: "http://localhost:8000/health" },
      { source: "/docs", destination: "http://localhost:8000/docs" },
    ];
  },
};
module.exports = nextConfig;