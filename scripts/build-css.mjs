// Builds the single stylesheet every page inlines in <head> (content/generated/site.css).
// The six source stylesheets in apps/web/public stay the editable originals; this keeps only the rules
// whose selectors can match something in the site's HTML, page shells, React components or browser
// scripts, so first paint needs no extra request. Runs before `next build` and `next dev`.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PurgeCSS } from 'purgecss';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pub = path.join(root, 'apps/web/public');

// Same order the layout used to link them in; later files override earlier ones.
const SOURCE_STYLES = ['frontend/css/style.min.css', 'css/fixes.css', 'css/style_blocks.css', 'css/pages.css', 'css/inline.css', 'clone.css'];

const results = await new PurgeCSS().purge({
  content: [
    path.join(root, 'content/**/*.html'),
    path.join(root, 'content/shell/*.svg'),
    path.join(pub, 'fragments/*.html'),
    path.join(pub, '*.js'),
    path.join(root, 'apps/web/src/**/*.tsx'),
  ],
  css: SOURCE_STYLES.map(file => ({ raw: readFileSync(path.join(pub, file), 'utf8') })),
  // PurgeCSS cannot see attribute values such as href^="mailto:" in the content, so selectors on these
  // attributes (every attribute the source stylesheets use) are always kept.
  dynamicAttributes: ['aria-hidden', 'class', 'data-image-fit', 'dir', 'disabled', 'hidden', 'href', 'name', 'open', 'type'],
  fontFace: true,
  keyframes: true,
  // Classes the browser scripts add at runtime are found in their source; these are belt and braces.
  safelist: { standard: ['active', 'menu-active', 'scrolling', 'lv-lock', /^is-/, /^swiper-pagination-bullet/] },
});

const css = results.map(r => r.css.trim()).join('\n');
// Inlined in a <style> element, so a stray closing tag must never end it early.
if (/<\/style/i.test(css)) throw new Error('Stylesheet contains </style');
const out = path.join(root, 'content/generated/site.css');
mkdirSync(path.dirname(out), { recursive: true });
writeFileSync(out, css);
const before = SOURCE_STYLES.reduce((n, f) => n + readFileSync(path.join(pub, f)).length, 0);
console.log(`site.css: ${(css.length / 1024).toFixed(1)} KiB (from ${(before / 1024).toFixed(1)} KiB)`);
