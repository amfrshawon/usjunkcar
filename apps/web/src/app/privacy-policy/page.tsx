import { ContentPage, pageMetadata } from '@/server/page';

export const dynamic = 'force-static';
export const metadata = pageMetadata('privacy-policy');

export default function Page() {
  return <ContentPage id="privacy-policy" />;
}
