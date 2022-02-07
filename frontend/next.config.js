/** @type {import('next').NextConfig} */

const basePath = process.env.NODE_ENV === "production" ? "/feed" : undefined;

const nextConfig = {
  reactStrictMode: true,
  basePath: basePath,
  images: {
    domains: ["localhost", "sean.fish"],
    loader: "custom",
  },
  i18n: {
    locales: ["en"],
    defaultLocale: "en",
  },
};

module.exports = nextConfig;
