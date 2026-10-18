import 'server-only';
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { HtmlFragment } from '@/components/Fragment';
import { buildEnv, CANONICAL_ORIGIN } from './config';
import { findRoute, isPublic, readFragment } from './publication';

const OG_IMAGE = { url: '/images/brand/og-image.png', width: 1200, height: 630, alt: 'US Junk Cars, powered by Super Intelligent' };

function requirePublic(id: string) {
  const route = findRoute(id);
  if (!route || !isPublic(route)) notFound();
  return route;
}

export function pageMetadata(id: string): Metadata {
  const route = findRoute(id);
  if (!route || !isPublic(route)) return { title: 'Page not found', robots: { index: false, follow: false } };
  const url = `${CANONICAL_ORIGIN}${route.path}`;
  return {
    title: { absolute: route.title },
    description: route.description,
    alternates: { canonical: url },
    openGraph: { type: 'website', siteName: 'USJunkCars', url, title: route.title, description: route.description, images: [OG_IMAGE] },
    twitter: { card: 'summary_large_image', title: route.title, description: route.description, images: [OG_IMAGE.url] },
    robots: buildEnv === 'production'
      ? { index: true, follow: true, 'max-image-preview': 'large' }
      : { index: false, follow: false },
  };
}

export function ContentPage({ id }: { id: string }) {
  const route = requirePublic(id);
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(route.jsonLd) }} />
      <HtmlFragment as="main" html={readFragment('pages', `${id}.html`)} />
    </>
  );
}
