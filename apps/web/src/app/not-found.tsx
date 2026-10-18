import { HtmlFragment } from '@/components/Fragment';
import { NOT_FOUND_MAIN } from '@/server/document';

export default function NotFound() {
  return <HtmlFragment as="main" html={NOT_FOUND_MAIN} />;
}
