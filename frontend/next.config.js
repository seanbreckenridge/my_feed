/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["localhost", "sean.fish"],
    loader: "custom",
  },
};

module.exports = nextConfig;
