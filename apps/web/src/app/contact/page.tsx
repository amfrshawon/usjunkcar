import { ContentPage, pageMetadata } from '@/server/page';

export const dynamic = 'force-static';
export const metadata = pageMetadata('contact');

export default function Page() {
  return <ContentPage id="contact" />;
}
