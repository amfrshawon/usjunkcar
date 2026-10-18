import { contentResponse } from '@/server/document';

export const dynamic = 'force-static';

export function GET() {
  // The hero board background is the mobile LCP element; CSS backgrounds are otherwise found late.
  return contentResponse('home', { preloadImage: '/images/backgrounds/hero-board-red.webp' });
}
