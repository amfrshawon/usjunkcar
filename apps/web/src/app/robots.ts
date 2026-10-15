import type { MetadataRoute } from 'next';
import { buildEnv, CANONICAL_ORIGIN } from '@/server/config';

export const dynamic = 'force-static';

export default function robots(): MetadataRoute.Robots {
  if (buildEnv !== 'production') return { rules: { userAgent: '*', disallow: '/' } };
  return { rules: { userAgent: '*', allow: '/' }, sitemap: `${CANONICAL_ORIGIN}/sitemap.xml` };
}
