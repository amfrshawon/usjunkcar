import { ContentPage, pageMetadata } from '@/server/page';

export const dynamic = 'force-static';
export const metadata = pageMetadata('faq');

export default function Page() {
  return <ContentPage id="faq" />;
}
