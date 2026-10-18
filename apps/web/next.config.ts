import { fileURLToPath } from 'node:url';
import type { NextConfig } from 'next';

// Each build targets one environment; the runtime refuses to start under a different APP_ENV.
const appEnv = process.env.APP_ENV ?? 'local';
const repoRoot = fileURLToPath(new URL('../..', import.meta.url));

const nextConfig: NextConfig = {
  output: 'standalone',
  outputFileTracingRoot: repoRoot,
  outputFileTracingIncludes: { '/*': ['../../content/**/*'] },
  trailingSlash: true,
  poweredByHeader: false,
  reactStrictMode: true,
  env: { BUILD_APP_ENV: appEnv },
  async headers() {
    const headers = [
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
      { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
      { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
    ];
    if (appEnv !== 'production') headers.push({ key: 'X-Robots-Tag', value: 'noindex, nofollow, noarchive' });
    // Next serves public/ files with max-age=0, so repeat visitors revalidate every asset. Scripts are
    // referenced with a ?v= version and fonts are renamed when they change, so both are cached for a
    // year; images and video are not versioned, so they get a week.
    const cache = (value: string) => [{ key: 'Cache-Control', value }];
    return [
      { source: '/:path*', headers },
      { source: '/:script([^/]+\\.js)', has: [{ type: 'query', key: 'v' }], headers: cache('public, max-age=31536000, immutable') },
      { source: '/frontend/fonts/:path*', headers: cache('public, max-age=31536000, immutable') },
      { source: '/images/:path*', headers: cache('public, max-age=604800, stale-while-revalidate=86400') },
      { source: '/video/:path*', headers: cache('public, max-age=604800, stale-while-revalidate=86400') },
    ];
  },
};

export default nextConfig;
