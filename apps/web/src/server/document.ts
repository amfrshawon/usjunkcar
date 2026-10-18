import 'server-only';
import { buildEnv, CANONICAL_ORIGIN, GTM_ID, gtmBootstrap, peddleBootstrap } from './config';
import { findRoute, isPublic, readFragment } from './publication';

/**
 * Content pages are complete HTML documents served by static route handlers rather than React pages.
 * They have no client components, so React's hydration payload (a second copy of every fragment) and the
 * Next.js client runtime only cost mobile visitors ~200 KiB before first paint. The 404 page and the API
 * still use the App Router; app/layout.tsx shares the head pieces below.
 */

export const THEME_COLOR = '#0A2B5E';
export const SITE_NAME = 'USJunkCars';
export const ICONS: { rel: 'icon' | 'apple-touch-icon'; href: string; sizes?: string; type?: string }[] = [
  { rel: 'icon', href: '/images/favicon/favicon.ico', sizes: '48x48' },
  { rel: 'icon', href: '/images/favicon/favicon.svg', type: 'image/svg+xml' },
  { rel: 'icon', href: '/images/favicon/favicon-32.png', sizes: '32x32', type: 'image/png' },
  { rel: 'icon', href: '/images/favicon/favicon-16.png', sizes: '16x16', type: 'image/png' },
  { rel: 'apple-touch-icon', href: '/images/favicon/apple-touch-icon.png', sizes: '180x180' },
];
export const MANIFEST = '/images/favicon/site.webmanifest';
export const SCRIPTS = ['/clone.js?v=next2', '/peddle-offer.js?v=3', '/analytics.js?v=1', '/video-player.js?v=3'];
const OG_IMAGE = { url: '/images/brand/og-image.png', width: 1200, height: 630, alt: 'US Junk Cars, powered by Super Intelligent' };

/** The purged site stylesheet built by scripts/build-css.mjs, inlined so first paint needs no CSS request. */
export const siteCss = (): string => readFragment('generated', 'site.css');

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const meta = (attr: 'name' | 'property', key: string, content: string | number) => `<meta ${attr}="${key}" content="${esc(String(content))}"/>`;
const link = (attrs: Record<string, string | undefined>) => `<link ${Object.entries(attrs).filter(([, v]) => v !== undefined).map(([k, v]) => `${k}="${esc(v!)}"`).join(' ')}/>`;
// JSON inside <script> must not be able to close the element.
const jsonLd = (data: unknown) => `<script type="application/ld+json">${JSON.stringify(data).replace(/</g, '\\u003c')}</script>`;

export type DocumentOptions = {
  /** An image to fetch at high priority before CSS is parsed (the page's LCP element). */
  preloadImage?: string;
};

/** Main content of the 404 page, shared with app/not-found.tsx. */
export const NOT_FOUND_MAIN = `<section class="page-title"><div class="container"><h1 class="section-title">Page not found</h1><p class="page-title__lead">Sorry, that page does not exist. You can still get a cash offer for your junk car in minutes.</p><div class="page-cta-row"><a class="button button--default" href="/"><span class="button__inner">Go to the homepage</span></a><a class="button button--white" href="tel:+18445120697"><span class="button__inner" style="color:#DE193E">Call 1-844-512-0697</span></a></div></div></section>`;

type Page = { title: string; main: string; headTags: string[]; robots: string; jsonLd?: unknown; preloadImage?: string };

function renderDocument(page: Page): string {
  const head = [
    '<meta charset="utf-8"/>',
    '<meta name="viewport" content="width=device-width, initial-scale=1"/>',
    page.preloadImage ? link({ rel: 'preload', href: page.preloadImage, as: 'image', fetchpriority: 'high' }) : '',
    `<script>${gtmBootstrap()}</script>`,
    `<style>${siteCss()}</style>`,
    meta('name', 'theme-color', THEME_COLOR),
    `<title>${esc(page.title)}</title>`,
    meta('name', 'robots', page.robots),
    ...page.headTags,
    ...ICONS.map(({ rel, ...attrs }) => link({ rel, ...attrs })),
    `<script>${peddleBootstrap()}</script>`,
  ];
  const body = [
    `<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=${GTM_ID}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>`,
    readFragment('shell', 'sprite.svg'),
    readFragment('shell', 'header.html'),
    page.jsonLd ? jsonLd(page.jsonLd) : '',
    `<main class="main">${page.main}</main>`,
    readFragment('shell', 'footer.html'),
    ...SCRIPTS.map(src => `<script defer src="${src}"></script>`),
  ];
  return `<!DOCTYPE html><html lang="en-US"><head>${head.join('')}</head><body class="home" id="top" style="position:relative">${body.join('\n')}</body></html>`;
}

const html = (body: string, status = 200) => new Response(body, { status, headers: { 'content-type': 'text/html; charset=utf-8' } });

/** GET handler body for a content route; routes that are not public in this build get the 404 page. */
export function contentResponse(id: string, options: DocumentOptions = {}): Response {
  const route = findRoute(id);
  if (!route || !isPublic(route)) {
    return html(renderDocument({ title: 'Page not found', main: NOT_FOUND_MAIN, headTags: [], robots: 'noindex, nofollow' }), 404);
  }
  const url = `${CANONICAL_ORIGIN}${route.path}`;
  const image = `${CANONICAL_ORIGIN}${OG_IMAGE.url}`;
  return html(renderDocument({
    title: route.title,
    main: readFragment('pages', `${id}.html`),
    jsonLd: route.jsonLd,
    preloadImage: options.preloadImage,
    robots: buildEnv === 'production' ? 'index, follow, max-image-preview:large' : 'noindex, nofollow',
    headTags: [
      meta('name', 'description', route.description),
      meta('name', 'application-name', SITE_NAME),
      link({ rel: 'manifest', href: MANIFEST }),
      link({ rel: 'canonical', href: url }),
      meta('property', 'og:title', route.title),
      meta('property', 'og:description', route.description),
      meta('property', 'og:url', url),
      meta('property', 'og:site_name', SITE_NAME),
      meta('property', 'og:image', image),
      meta('property', 'og:image:width', OG_IMAGE.width),
      meta('property', 'og:image:height', OG_IMAGE.height),
      meta('property', 'og:image:alt', OG_IMAGE.alt),
      meta('property', 'og:type', 'website'),
      meta('name', 'twitter:card', 'summary_large_image'),
      meta('name', 'twitter:title', route.title),
      meta('name', 'twitter:description', route.description),
      meta('name', 'twitter:image', image),
    ],
  }));
}
