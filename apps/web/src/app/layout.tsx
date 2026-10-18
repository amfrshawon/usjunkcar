import type { Metadata, Viewport } from 'next';
import { HtmlFragment } from '@/components/Fragment';
import { CANONICAL_ORIGIN, peddleBootstrap } from '@/server/config';
import { readFragment } from '@/server/publication';

export const metadata: Metadata = {
  metadataBase: new URL(CANONICAL_ORIGIN),
  applicationName: 'US Junk Cars',
  icons: {
    icon: [
      { url: '/images/favicon/favicon.ico', sizes: '48x48' },
      { url: '/images/favicon/favicon.svg', type: 'image/svg+xml' },
      { url: '/images/favicon/favicon-32.png', sizes: '32x32', type: 'image/png' },
      { url: '/images/favicon/favicon-16.png', sizes: '16x16', type: 'image/png' },
    ],
    apple: { url: '/images/favicon/apple-touch-icon.png', sizes: '180x180' },
  },
  manifest: '/images/favicon/site.webmanifest',
};

export const viewport: Viewport = { width: 'device-width', initialScale: 1, themeColor: '#0A2B5E' };

const STYLES = ['/frontend/css/style.min.css?v=04b4da58b1', '/css/fixes.css?v=brand2', '/css/style_blocks.css', '/css/pages.css?v=5', '/css/inline.css?v=1', '/clone.css?v=copy1'];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-US">
      <head>
        {STYLES.map(href => <link key={href} rel="stylesheet" href={href} precedence="default" />)}
        <script dangerouslySetInnerHTML={{ __html: peddleBootstrap() }} />
      </head>
      <body className="home" id="top" style={{ position: 'relative' }}>
        <HtmlFragment html={readFragment('shell', 'sprite.svg')} />
        <HtmlFragment html={readFragment('shell', 'header.html')} />
        {children}
        <HtmlFragment html={readFragment('shell', 'footer.html')} />
        <script defer src="/clone.js?v=next1" />
        <script defer src="/peddle-offer.js?v=2" />
      </body>
    </html>
  );
}
