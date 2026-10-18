import { ContentPage, pageMetadata } from '@/server/page';

export const dynamic = 'force-static';
export const metadata = pageMetadata('blog');

export default function Page() {
  return <ContentPage id="blog" />;
}
