import { ContentPage, pageMetadata } from '@/server/page';

export const dynamic = 'force-static';
export const metadata = pageMetadata('home');

export default function HomePage() {
  return <ContentPage id="home" />;
}
