import type { Metadata, Viewport } from 'next';
import { HtmlFragment } from '@/components/Fragment';
import { CANONICAL_ORIGIN, GTM_ID, gtmBootstrap, peddleBootstrap } from '@/server/config';
import { ICONS, MANIFEST, SCRIPTS, SITE_NAME, siteCss, THEME_COLOR } from '@/server/document';
import { readFragment } from '@/server/publication';

// Content pages are rendered by route handlers (src/server/document.ts); this layout only wraps the 404 page.
export const metadata: Metadata = {
  metadataBase: new URL(CANONICAL_ORIGIN),
  applicationName: SITE_NAME,
  icons: {
    icon: ICONS.filter(i => i.rel === 'icon').map(({ href, sizes, type }) => ({ url: href, sizes, type })),
    apple: ICONS.filter(i => i.rel === 'apple-touch-icon').map(({ href, sizes }) => ({ url: href, sizes })),
  },
  manifest: MANIFEST,
};

export const viewport: Viewport = { width: 'device-width', initialScale: 1, themeColor: THEME_COLOR };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-US">
      <head>
        <script dangerouslySetInnerHTML={{ __html: gtmBootstrap() }} />
        <style dangerouslySetInnerHTML={{ __html: siteCss() }} />
        <script dangerouslySetInnerHTML={{ __html: peddleBootstrap() }} />
      </head>
      <body className="home" id="top" style={{ position: 'relative' }}>
        <noscript><iframe src={`https://www.googletagmanager.com/ns.html?id=${GTM_ID}`} height="0" width="0" style={{ display: 'none', visibility: 'hidden' }} /></noscript>
        <HtmlFragment html={readFragment('shell', 'sprite.svg')} />
        <HtmlFragment html={readFragment('shell', 'header.html')} />
        {children}
        <HtmlFragment html={readFragment('shell', 'footer.html')} />
        {SCRIPTS.map(src => <script key={src} defer src={src} />)}
      </body>
    </html>
  );
}
