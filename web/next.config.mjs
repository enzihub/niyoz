import path from 'node:path';

// Demo mode swaps Clerk for a local stand-in with one invented user,
// so the app runs on your machine without any accounts. See src/demo/.
const demo = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';

/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    if (demo) {
      config.resolve.alias = {
        ...config.resolve.alias,
        '@clerk/nextjs/server$': path.resolve('src/demo/clerk-server.ts'),
        '@clerk/nextjs$': path.resolve('src/demo/clerk.tsx'),
      };
    }
    return config;
  },
};

export default nextConfig;
