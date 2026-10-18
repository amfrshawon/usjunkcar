// Publication and data gate run by the deploy job before a release reaches the VPS.
// Production fails closed unless the owner approved each published route and every internal link resolves.
import assert from 'node:assert/strict';
import { existsSync, readdirSync, readFileSync } from 'node:fs';

const env = process.env.APP_ENV;
assert.ok(['development', 'production'].includes(env), 'APP_ENV must be development or production');
const registry = JSON.parse(readFileSync('content/publication.json', 'utf8'));
const routes = registry.routes;

const visible = routes.filter(r => r.environments.includes(env) &&
  (env === 'production' ? r.status === 'published' && r.approval : ['review', 'approved', 'published'].includes(r.status)));

if (env === 'production') {
  assert.ok(visible.length > 0, 'No owner-approved published routes: production would serve only 404s');
  assert.ok(visible.some(r => r.path === '/'), 'The homepage must be approved before production release');
}
assert.ok(visible.length <= registry.maxPublicContentPages, `More than ${registry.maxPublicContentPages} public content pages`);

// Every internal page link on visible content must point to a visible route.
const paths = new Set(visible.map(r => r.path));
const blogPostsPath = 'content/blog/posts.json';
if (paths.has('/blog/') && existsSync(blogPostsPath)) {
  const posts = JSON.parse(readFileSync(blogPostsPath, 'utf8'));
  for (const post of posts) paths.add(`/blog/${post.slug}/`);
}
const sources = ['content/shell/header.html', 'content/shell/footer.html', ...visible.map(r => `content/pages/${r.id}.html`)];
const broken = new Set();
for (const file of sources) {
  for (const [, href] of readFileSync(file, 'utf8').matchAll(/href="(\/[^"#?]*)/g)) {
    if (/\.[a-z0-9]+$/i.test(href)) continue; // static asset
    const page = href.endsWith('/') ? href : `${href}/`;
    if (!paths.has(page === '//' ? '/' : page)) broken.add(`${href} (in ${file})`);
  }
}
assert.equal(broken.size, 0, `Links to routes that are not public in ${env}:\n  ${[...broken].join('\n  ')}`);

// Database migrations are an application phase that has not started; refuse rather than silently skip.
const migrations = existsSync('supabase/migrations') ? readdirSync('supabase/migrations').filter(f => f.endsWith('.sql')) : [];
assert.equal(migrations.length, 0, 'Migrations exist but no migration runner is implemented yet');

console.log(`Publication gate passed for ${env}: ${visible.length} public route(s); no database migrations in this release.`);
