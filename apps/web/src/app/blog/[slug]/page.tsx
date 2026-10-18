import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { HtmlFragment } from '@/components/Fragment';
import { buildEnv, CANONICAL_ORIGIN } from '@/server/config';
import { findRoute, isPublic, readFragment } from '@/server/publication';

type BlogSection = { heading: string; body: string };
type BlogReference = { label: string; url: string };
type BlogPost = {
  slug: string;
  title: string;
  metaTitle?: string;
  metaDescription?: string;
  category: string;
  categorySlug: string;
  date: string;
  dateIso: string;
  readTime: string;
  icon: string;
  iconAlt: string;
  heroImage?: string;
  summary: string;
  aiOverview?: string;
  keyTakeaways: string[];
  targetKeywords?: string[];
  sections: BlogSection[];
  references?: BlogReference[];
};

const OG_IMAGE = {
  url: '/images/brand/og-image.png',
  width: 1200,
  height: 630,
  alt: 'US Junk Cars, powered by Super Intelligent',
};

function loadPosts(): BlogPost[] {
  const raw = readFragment('blog', 'posts.json');
  return JSON.parse(raw) as BlogPost[];
}

function stripHtml(html: string): string {
  return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function extractFaqEntities(sections: BlogSection[]): Array<{ '@type': 'Question'; name: string; acceptedAnswer: { '@type': 'Answer'; text: string } }> {
  const entities: Array<{ '@type': 'Question'; name: string; acceptedAnswer: { '@type': 'Answer'; text: string } }> = [];
  for (const sec of sections) {
    if (!/frequently asked questions|people also ask|faq/i.test(sec.heading)) continue;
    const regex = /<h[34][^>]*>(.*?)<\/h[34]>\s*<p[^>]*>(.*?)<\/p>/gis;
    let match: RegExpExecArray | null;
    while ((match = regex.exec(sec.body)) !== null) {
      const q = stripHtml(match[1]);
      const a = stripHtml(match[2]);
      if (q && a) {
        entities.push({
          '@type': 'Question',
          name: q,
          acceptedAnswer: { '@type': 'Answer', text: a },
        });
      }
    }
  }
  return entities;
}

export const dynamic = 'force-static';
export const dynamicParams = false;

export function generateStaticParams() {
  return loadPosts().map(post => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const blogRoute = findRoute('blog');
  if (!blogRoute || !isPublic(blogRoute)) {
    return { title: 'Page not found', robots: { index: false, follow: false } };
  }
  const post = loadPosts().find(p => p.slug === slug);
  if (!post) {
    return { title: 'Page not found', robots: { index: false, follow: false } };
  }
  const url = `${CANONICAL_ORIGIN}/blog/${post.slug}/`;
  const metaTitle = post.metaTitle || (post.title.length <= 48 ? `${post.title} | USJunkCars` : post.title);
  const metaDescription = post.metaDescription || (post.summary.length > 160 ? `${post.summary.slice(0, 157)}...` : post.summary);
  return {
    title: { absolute: metaTitle },
    description: metaDescription,
    keywords: post.targetKeywords,
    alternates: { canonical: url },
    openGraph: {
      type: 'article',
      siteName: 'USJunkCars',
      url,
      title: metaTitle,
      description: metaDescription,
      images: [post.heroImage ? { url: post.heroImage, width: 1200, height: 630, alt: post.title } : OG_IMAGE],
    },
    twitter: {
      card: 'summary_large_image',
      title: metaTitle,
      description: metaDescription,
      images: [post.heroImage || OG_IMAGE.url],
    },
    robots:
      buildEnv === 'production'
        ? { index: true, follow: true, 'max-image-preview': 'large' }
        : { index: false, follow: false },
  };
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const blogRoute = findRoute('blog');
  if (!blogRoute || !isPublic(blogRoute)) notFound();

  const posts = loadPosts().sort((a, b) => (b.dateIso || '').localeCompare(a.dateIso || ''));
  const post = posts.find(p => p.slug === slug);
  if (!post) notFound();

  const related = posts.filter(p => p.categorySlug === post.categorySlug && p.slug !== post.slug).slice(0, 2);
  const otherTopics = posts.filter(p => p.categorySlug !== post.categorySlug).slice(0, 2);
  const recommendedCards = [...related, ...otherTopics].slice(0, 2);
  const url = `${CANONICAL_ORIGIN}/blog/${post.slug}/`;
  const faqEntities = extractFaqEntities(post.sections);

  const jsonLd: Record<string, unknown>[] = [
    {
      '@context': 'https://schema.org',
      '@type': 'BlogPosting',
      headline: post.title,
      description: post.summary,
      abstract: post.aiOverview || post.summary,
      image: post.heroImage ? [`${CANONICAL_ORIGIN}${post.heroImage}`] : [`${CANONICAL_ORIGIN}${OG_IMAGE.url}`],
      keywords: (post.targetKeywords || []).join(', '),
      datePublished: post.dateIso.slice(0, 10),
      dateModified: post.dateIso.slice(0, 10),
      url,
      author: { '@type': 'Organization', name: 'US Junk Cars Editorial Team', url: `${CANONICAL_ORIGIN}/` },
      publisher: {
        '@type': 'Organization',
        name: 'US Junk Cars',
        legalName: 'USJunkCars',
        url: `${CANONICAL_ORIGIN}/`,
        logo: `${CANONICAL_ORIGIN}/images/brand/logo-stacked.svg`,
      },
      citation: (post.references || []).map(r => r.url),
    },
    {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: `${CANONICAL_ORIGIN}/` },
        { '@type': 'ListItem', position: 2, name: 'Blog', item: `${CANONICAL_ORIGIN}/blog/` },
        { '@type': 'ListItem', position: 3, name: post.category, item: `${CANONICAL_ORIGIN}/blog/#topic-${post.categorySlug}` },
        { '@type': 'ListItem', position: 4, name: post.title, item: url },
      ],
    },
  ];

  if (faqEntities.length > 0) {
    jsonLd.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqEntities,
    });
  }

  const aiOverviewHtml = post.aiOverview
    ? `<div class="blog-ai-overview" role="region" aria-label="Quick Answer Overview">
    <div class="blog-ai-overview__header">
      <span class="blog-ai-overview__badge">Quick Answer &bull; Seller Overview</span>
      <span class="blog-ai-overview__sub">Direct answer verified against 2026 market &amp; state DMV rules</span>
    </div>
    <p class="blog-ai-overview__text">${post.aiOverview}</p>
  </div>`
    : '';

  const heroImageHtml = post.heroImage
    ? `<figure class="blog-hero-figure">
    <img src="${post.heroImage}" alt="${post.iconAlt || post.title}" class="blog-hero-image" width="895" height="438" loading="eager" decoding="async" />
  </figure>`
    : '';

  const takeawaysHtml = post.keyTakeaways.map(item => `<li>${item}</li>`).join('');
  const tocHtml = post.sections
    .map((s, idx) => `<li><a href="#section-${idx + 1}">${idx + 1}. ${s.heading}</a></li>`)
    .join('');

  const sectionsHtml = post.sections
    .map((s, idx) => `<section class="blog-article__section" id="section-${idx + 1}">\n<h2>${s.heading}</h2>\n${s.body}\n</section>`)
    .join('\n');

  const referencesHtml =
    post.references && post.references.length > 0
      ? `<div class="blog-references" id="official-references">
    <h2 class="blog-references__title">Official State DMV, Federal &amp; Industry References</h2>
    <p class="blog-references__desc">Every rule, form number, and valuation benchmark in this guide is cross-checked against official government agencies and automotive recycling standards:</p>
    <ul class="blog-references__list">
      ${post.references
        .map(
          ref =>
            `<li><a href="${ref.url}" target="_blank" rel="noopener noreferrer">${ref.label} <span aria-hidden="true">&#8599;</span></a></li>`,
        )
        .join('')}
    </ul>
  </div>`
      : '';

  const keywordsHtml =
    post.targetKeywords && post.targetKeywords.length > 0
      ? `<div class="blog-keywords">
    <span class="blog-keywords__label">Related Seller Topics:</span>
    <div class="blog-keywords__pills">
      ${post.targetKeywords.map(kw => `<span class="blog-keyword-pill">${kw}</span>`).join('')}
    </div>
  </div>`
      : '';

  const relatedHtml = recommendedCards
    .map(
      r => `<article class="blog-card" data-category="${r.categorySlug}">
<div class="blog-card__top">
  <div class="blog-card__icon"><img alt="${r.iconAlt}" decoding="async" height="44" loading="lazy" src="${r.icon}" width="44"/></div>
  <div class="blog-card__badges">
    <span class="blog-badge blog-badge--${r.categorySlug}">${r.category}</span>
    <span class="blog-meta-pill">${r.readTime}</span>
  </div>
</div>
<h3 class="blog-card__title"><a href="/blog/${r.slug}/">${r.title}</a></h3>
<p class="blog-card__excerpt">${r.summary}</p>
<div class="blog-card__footer">
  <div class="blog-card__date-wrap"><time class="blog-card__date" datetime="${r.dateIso.slice(0, 10)}">${r.date}</time></div>
  <a class="blog-card__read" href="/blog/${r.slug}/">Read Full Guide <span aria-hidden="true">&rarr;</span></a>
</div>
</article>`,
    )
    .join('');

  const html = `<div class="breadcrumbs"><div class="container"><ul class="breadcrumbs-list"><li class="breadcrumbs-list__item"><a class="breadcrumbs-list__item-link" href="/">Home</a></li><li class="breadcrumbs-list__item"><a class="breadcrumbs-list__item-link" href="/blog/">Blog</a></li><li class="breadcrumbs-list__item"><a class="breadcrumbs-list__item-link" href="/blog/#topic-${post.categorySlug}">${post.category}</a></li><li class="breadcrumbs-list__item" aria-current="page">${post.title}</li></ul></div></div>
<section class="page-section page-section--tint"><div class="container">
<article class="blog-article blog-article--single">
  <div class="blog-article__meta">
    <a class="blog-badge blog-badge--${post.categorySlug}" href="/blog/#topic-${post.categorySlug}" style="text-decoration:none;">${post.category}</a>
    <time datetime="${post.dateIso.slice(0, 10)}">Updated ${post.date}</time>
    <span>&bull; ${post.readTime}</span>
    <span>&bull; Fact-Checked with ${(post.references || []).length} Official Sources</span>
  </div>
  <h1 class="section-title">${post.title}</h1>
  <p class="blog-article__lead">${post.summary}</p>
  ${heroImageHtml}
  ${aiOverviewHtml}
  <div class="blog-takeaways">
    <p class="blog-takeaways__title">Key Takeaways at a Glance</p>
    <ul class="checklist">${takeawaysHtml}</ul>
  </div>
  <nav class="blog-toc" aria-label="Table of contents">
    <p class="blog-toc__title">In This Seller Guide</p>
    <ol class="blog-toc__list">
      ${tocHtml}
      ${post.references && post.references.length > 0 ? '<li><a href="#official-references">Official State DMV &amp; Regulatory References</a></li>' : ''}
    </ol>
  </nav>
  <div class="blog-article__body page-content">
    ${sectionsHtml}
  </div>
  ${referencesHtml}
  ${keywordsHtml}
  <div class="blog-article__cta">
    <div class="blog-article__cta-text">
      <strong>Ready to see what your vehicle is worth today?</strong>
      <span>Get a guaranteed cash offer in minutes with $0 flatbed towing across all 50 states.</span>
    </div>
    <div class="blog-article__cta-actions">
      <a class="button button--default" data-peddle-offer="" href="tel:+18445120697"><span class="button__inner">Get My Instant Offer <svg class="icon icon--arrow-left" height="20" width="11"><use xlink:href="#icon-arrow-left"></use></svg></span></a>
      <a class="blog-back-top" href="/blog/#topic-${post.categorySlug}">&larr; More in ${post.category}</a>
    </div>
  </div>
</article>
${
  relatedHtml
    ? `<div class="blog-related">
  <h2 class="section-title">Related Seller Guides</h2>
  <div class="blog-grid">${relatedHtml}</div>
</div>`
    : ''
}
</div></section>`;

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <HtmlFragment as="main" html={html} />
    </>
  );
}
