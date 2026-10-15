import type { MetadataRoute } from 'next';
import { CANONICAL_ORIGIN } from '@/server/config';
import { publicRoutes } from '@/server/publication';

export const dynamic = 'force-static';

/** Lists only routes that are public in this build's environment (approved routes in production). */
export default function sitemap(): MetadataRoute.Sitemap {
  return publicRoutes().map(route => ({ url: `${CANONICAL_ORIGIN}${route.path}`, lastModified: '2026-10-15' }));
}
