/** Renders reviewed, repository-controlled HTML without adding a layout box. */
export function HtmlFragment({ html, as: Tag = 'div' }: { html: string; as?: 'div' | 'main' }) {
  if (Tag === 'main') return <main className="main" dangerouslySetInnerHTML={{ __html: html }} />;
  return <div style={{ display: 'contents' }} dangerouslySetInnerHTML={{ __html: html }} />;
}
