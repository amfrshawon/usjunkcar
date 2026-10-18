import { contentResponse } from '@/server/document';

export const dynamic = 'force-static';

export function GET() {
  return contentResponse('privacy-policy');
}
