import { ContentPage, pageMetadata } from '@/server/page';

export const dynamic = 'force-static';
export const metadata = pageMetadata('terms-and-conditions');

export default function Page() {
  return <ContentPage id="terms-and-conditions" />;
}
