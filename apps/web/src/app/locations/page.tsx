import { ContentPage, pageMetadata } from '@/server/page';

export const dynamic = 'force-static';
export const metadata = pageMetadata('locations');

export default function Page() {
  return <ContentPage id="locations" />;
}
