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
    return [{ source: '/:path*', headers }];
  },
};

export default nextConfig;
