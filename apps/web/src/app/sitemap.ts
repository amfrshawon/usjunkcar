import type { MetadataRoute } from 'next';
import { CANONICAL_ORIGIN } from '@/server/config';
import { publicRoutes, type PublicRoute } from '@/server/publication';

export const dynamic = 'force-static';

type SitemapEntry = MetadataRoute.Sitemap[number];
type VideoObject = { '@type': 'VideoObject'; name: string; description: string; thumbnailUrl: string; contentUrl: string; duration: string; uploadDate: string };

// Next writes video fields into the XML without escaping them.
const xmlText = (value: string) => value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** Video entries come from the route's VideoObject JSON-LD, so the sitemap and the page never disagree. */
function videos(route: PublicRoute): NonNullable<SitemapEntry['videos']> {
  const nodes = (Array.isArray(route.jsonLd) ? route.jsonLd : [route.jsonLd]) as Array<Partial<VideoObject> | null>;
  return nodes.filter((n): n is VideoObject => n?.['@type'] === 'VideoObject').map(v => {
    const [, minutes = '0', seconds = 'NaN'] = /^PT(?:(\d+)M)?(\d+)S$/.exec(v.duration) ?? [];
    return {
      title: xmlText(v.name),
      description: xmlText(v.description),
      thumbnail_loc: v.thumbnailUrl,
      content_loc: v.contentUrl,
      duration: Number(minutes) * 60 + Number(seconds),
      publication_date: v.uploadDate,
    };
  });
}

/** Lists only routes that are public in this build's environment (approved routes in production). */
export default function sitemap(): MetadataRoute.Sitemap {
  return publicRoutes().map(route => {
    const entry: SitemapEntry = { url: `${CANONICAL_ORIGIN}${route.path}`, lastModified: route.lastModified ?? '2026-10-18' };
    const list = videos(route);
    if (list.length) entry.videos = list;
    return entry;
  });
}
