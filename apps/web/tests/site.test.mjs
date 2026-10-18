// Runs against an assembled standalone release (STAGE_DIR) built for EXPECT_ENV. Started by scripts/ci-check.mjs.
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import net from 'node:net';

const stage = process.env.STAGE_DIR;
const env = process.env.EXPECT_ENV;
const registry = JSON.parse(readFileSync(path.join(stage, 'content/publication.json'), 'utf8'));
const FORBIDDEN = ['usjunkcars.com', 'usjunkyards', '888-871-4488', '18888714488', 'LASE VIE', 'Oberbrunner', 'Based on 15823'];
let server, origin;

const freePort = () => new Promise(resolve => { const s = net.createServer(); s.listen(0, () => { const { port } = s.address(); s.close(() => resolve(port)); }); });

function start(appEnv, port) {
  return spawn(process.execPath, ['apps/web/server.js'], {
    cwd: stage, env: { ...process.env, APP_ENV: appEnv, PORT: String(port), HOSTNAME: '127.0.0.1', RELEASE_SHA: 'a'.repeat(40) }, stdio: 'pipe',
  });
}

before(async () => {
  const port = await freePort();
  origin = `http://127.0.0.1:${port}`;
  server = start(env, port);
  for (let i = 0; i < 100; i++) {
    try { if ((await fetch(`${origin}/api/v1/health`)).ok) return; } catch {}
    await new Promise(r => setTimeout(r, 100));
  }
  throw new Error('server did not start');
});
after(() => server?.kill());

const visible = registry.routes.filter(r => r.environments.includes(env) &&
  (env === 'production' ? r.status === 'published' && r.approval : ['review', 'approved', 'published'].includes(r.status)));

test('health reports the release and environment', async () => {
  const body = await (await fetch(`${origin}/api/v1/health`)).json();
  assert.deepEqual(body.data, { status: 'ok', commit: 'a'.repeat(40), environment: env });
});

test('a build refuses to start under a different environment', async () => {
  const child = start(env === 'production' ? 'development' : 'production', await freePort());
  const code = await new Promise(resolve => { child.on('exit', resolve); setTimeout(() => { child.kill(); resolve('running'); }, 8000); });
  assert.notEqual(code, 'running');
  assert.notEqual(code, 0);
});

test('only public routes render; everything else is a real 404', async () => {
  for (const route of registry.routes) {
    const res = await fetch(origin + route.path, { redirect: 'manual' });
    assert.equal(res.status, visible.includes(route) ? 200 : 404, route.path);
  }
  assert.equal((await fetch(`${origin}/not-a-page/`)).status, 404);
  // Encoded or query variants must never reveal a route that is not public here.
  for (const route of registry.routes.filter(r => !visible.includes(r) && r.path !== '/')) {
    const encoded = route.path.replace(/[a-z]/, c => `%${c.charCodeAt(0).toString(16)}`);
    assert.equal((await fetch(origin + encoded)).status, 404, encoded);
    assert.equal((await fetch(`${origin}${route.path}?preview=true`)).status, 404, `${route.path}?preview=true`);
  }
});

test('public pages carry canonical metadata and environment-appropriate robots', async () => {
  for (const route of visible) {
    const res = await fetch(origin + route.path);
    const page = await res.text();
    assert.match(page, new RegExp(`<link rel="canonical" href="https://usjunkcars.si${route.path.replace(/\//g, '\\/')}"`), route.path);
    assert.match(page, /application\/ld\+json/);
    if (env === 'production') {
      assert.equal(res.headers.get('x-robots-tag'), null);
      assert.doesNotMatch(page, /noindex/);
    } else {
      assert.equal(res.headers.get('x-robots-tag'), 'noindex, nofollow, noarchive');
      assert.match(page, /<meta name="robots" content="noindex, nofollow"/);
    }
  }
});

test('trailing-slash addresses redirect', async () => {
  const res = await fetch(`${origin}/about`, { redirect: 'manual' });
  assert.equal(res.status, 308);
  assert.equal(res.headers.get('location'), '/about/');
});

test('sitemap lists only public routes, plus blog posts when the blog is public, and robots match the environment', async () => {
  const sitemap = await (await fetch(`${origin}/sitemap.xml`)).text();
  const listed = [...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map(m => m[1]).sort();
  const blog = visible.find(r => r.id === 'blog');
  const posts = blog ? JSON.parse(readFileSync(path.join(stage, 'content/blog/posts.json'), 'utf8')).map(p => `https://usjunkcars.si${blog.path}${p.slug}/`) : [];
  assert.deepEqual(listed, [...visible.map(r => `https://usjunkcars.si${r.path}`), ...posts].sort());
  const robots = await (await fetch(`${origin}/robots.txt`)).text();
  if (env === 'production') assert.match(robots, /Sitemap: https:\/\/usjunkcars\.si\/sitemap\.xml/);
  else assert.match(robots, /Disallow: \//);
});

test('no reference-business identity in pages or public assets', async () => {
  const texts = [];
  for (const route of visible) texts.push([route.path, await (await fetch(origin + route.path)).text()]);
  texts.push(['404', await (await fetch(`${origin}/missing/`)).text()]);
  const walk = dir => readdirSync(dir).flatMap(name => {
    const p = path.join(dir, name);
    return statSync(p).isDirectory() ? walk(p) : /\.(html|js|css|json|svg|txt|xml|webmanifest)$/.test(name) ? [p] : [];
  });
  for (const file of walk(path.join(stage, 'apps/web/public'))) texts.push([file, readFileSync(file, 'utf8')]);
  for (const [where, text] of texts) {
    for (const bad of FORBIDDEN) {
      assert.ok(!where.includes(bad), `${bad} found in path ${where}`);
      assert.ok(!text.includes(bad), `${bad} found in ${where}`);
    }
  }
});

test('every public page loads Google Tag Manager and the site event script', async () => {
  for (const route of visible) {
    const html = await (await fetch(`${origin}${route.path}`)).text();
    assert.match(html, /googletagmanager\.com\/gtm\.js\?id=/, `${route.path} is missing the GTM loader`);
    assert.match(html, /GTM-TNC9P49R/, `${route.path} uses the wrong container`);
    assert.match(html, /googletagmanager\.com\/ns\.html\?id=GTM-TNC9P49R/, `${route.path} is missing the GTM noscript frame`);
    assert.match(html, /src="\/analytics\.js\?v=\d+"/, `${route.path} is missing analytics.js`);
  }
  assert.equal((await fetch(`${origin}/analytics.js`)).status, 200);
});

test('content pages are lean static documents for fast mobile loads', async () => {
  for (const route of visible) {
    const html = await (await fetch(origin + route.path)).text();
    // No React flight payload or Next.js client runtime: the pages have no client components.
    assert.doesNotMatch(html, /self\.__next_f|\/_next\/static\//, `${route.path} ships the React client payload`);
    // Styles are inlined; render-blocking stylesheet requests would delay first paint.
    assert.doesNotMatch(html, /<link[^>]+rel="stylesheet"/, `${route.path} links a render-blocking stylesheet`);
    assert.match(html, /<style>[^<]*\.header\{/, `${route.path} is missing the inlined site stylesheet`);
  }
  const home = await (await fetch(`${origin}/`)).text();
  assert.match(home, /<link rel="preload" href="\/images\/backgrounds\/hero-board-red\.webp" as="image" fetchpriority="high"\/>/);
  assert.equal((await fetch(`${origin}/fragments/us-map.html`)).status, 200);
});

test('launch video files are fingerprinted, cached for a year and listed in the video sitemap', async () => {
  const home = await (await fetch(`${origin}/`)).text();
  const urls = [...new Set([...home.matchAll(/\/video\/[^"')\s]+/g)].map(m => m[0]))];
  // Teaser, film and vertical cut each in AV1 WebM and H.264 MP4, plus the poster in AVIF, WebP and JPEG.
  for (const attr of ['data-src', 'data-full', 'data-vertical']) {
    assert.match(home, new RegExp(`${attr}="/video/[^"]+\\.mp4"`), `${attr} needs an MP4`);
    assert.match(home, new RegExp(`${attr}-av1="/video/[^"]+\\.webm"`), `${attr} needs an AV1 WebM`);
  }
  for (const ext of ['avif', 'webp', 'jpg']) assert.ok(urls.some(u => u.endsWith(`.${ext}`)), `poster .${ext} missing`);
  for (const url of urls) {
    const [, hash] = /\.([0-9a-f]{8})\.[a-z0-9]+$/.exec(url) ?? [];
    assert.ok(hash, `${url} is not fingerprinted`);
    const file = readFileSync(path.join(stage, 'apps/web/public', url));
    assert.equal(createHash('sha256').update(file).digest('hex').slice(0, 8), hash, `${url} hash does not match its content`);
    const res = await fetch(origin + url, { headers: { Range: 'bytes=0-99' } });
    assert.equal(res.status, 206, `${url} must support range requests`);
    assert.equal(res.headers.get('cache-control'), 'public, max-age=31536000, immutable', url);
    await res.arrayBuffer();
  }
  const sitemap = await (await fetch(`${origin}/sitemap.xml`)).text();
  const blocks = [...home.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs)].flatMap(m => [JSON.parse(m[1])].flat());
  const video = blocks.find(b => b['@type'] === 'VideoObject');
  assert.match(video.uploadDate, /T\d\d:\d\d:\d\d[+-]\d\d:\d\d$/, 'uploadDate needs a time and timezone');
  for (const u of [video.contentUrl, video.thumbnailUrl]) assert.ok(urls.includes(new URL(u).pathname), `${u} is not used on the page`);
  if (visible.some(r => r.path === '/')) {
    assert.match(sitemap, /xmlns:video="http:\/\/www\.google\.com\/schemas\/sitemap-video\/1\.1"/);
    assert.ok(sitemap.includes(`<video:content_loc>${video.contentUrl}</video:content_loc>`));
    assert.ok(sitemap.includes(`<video:publication_date>${video.uploadDate}</video:publication_date>`));
    assert.ok(sitemap.includes('<video:duration>57</video:duration>'));
  }
});

test('no more than ten public content pages', () => {
  assert.ok(visible.length <= 10);
});

test('Peddle uses the live account only in production', async () => {
  const page = await (await fetch(`${origin}/api/v1/health`).then(() => fetch(`${origin}/not-a-page/`))).text();
  if (env === 'production') {
    assert.match(page, /publisherID:"5173226"/);
    assert.match(page, /https:\/\/publisher-embed\.peddle\.com\/api\/v1\/embed\//);
    assert.doesNotMatch(page, /staging-publisher-embed|329729/);
  } else {
    assert.match(page, /publisherID:"329729"/);
    assert.match(page, /staging-publisher-embed\.peddle\.com/);
  }
});

test('homepage names the site for search results', async () => {
  const html = await (await fetch(`${origin}/`)).text();
  const blocks = [...html.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs)].flatMap(m => [JSON.parse(m[1])].flat());
  const site = blocks.find(b => b['@type'] === 'WebSite');
  assert.ok(site, 'homepage needs WebSite structured data');
  assert.equal(site.name, 'USJunkCars');
  assert.equal(site.url, 'https://usjunkcars.si/');
  assert.match(html, /<meta property="og:site_name" content="USJunkCars"\/>/);
});

test('SEO quality: titles, descriptions, heading hierarchy, content depth, contextual links and CSS assets', () => {
  const inboundBodyLinks = new Map(visible.map(r => [r.path, 0]));
  for (const route of visible) {
    assert.ok(route.title.length >= 20 && route.title.length <= 65, `${route.id} title length ${route.title.length}`);
    assert.ok(route.description.length >= 110 && route.description.length <= 165, `${route.id} description length ${route.description.length}`);
    assert.match(route.lastModified ?? '', /^\d{4}-\d{2}-\d{2}$/, `${route.id} missing lastModified`);

    const html = readFileSync(path.join(stage, `content/pages/${route.id}.html`), 'utf8');
    const headings = [...html.matchAll(/<h([1-6])\b/gi)].map(m => Number(m[1]));
    assert.equal(headings.filter(h => h === 1).length, 1, `${route.id} must have exactly one h1`);
    for (let i = 1; i < headings.length; i++) {
      assert.ok(headings[i] <= headings[i - 1] + 1, `${route.id} skips heading level h${headings[i - 1]} -> h${headings[i]}`);
    }

    const words = html.replace(/<svg[\s\S]*?<\/svg>/gi, ' ').replace(/<[^>]+>/g, ' ').trim().split(/\s+/).filter(Boolean);
    assert.ok(words.length >= 500, `${route.id} body has only ${words.length} words (< 500)`);

    for (const [, href] of html.matchAll(/href="(\/[^"#?]*)/g)) {
      if (/\.[a-z0-9]+$/i.test(href)) continue;
      const target = href.endsWith('/') ? href : `${href}/`;
      if (target !== route.path && inboundBodyLinks.has(target)) {
        inboundBodyLinks.set(target, inboundBodyLinks.get(target) + 1);
      }
    }
  }
  for (const [routePath, count] of inboundBodyLinks) {
    assert.ok(count >= 1, `${routePath} has 0 contextual inbound body links`);
  }

  // Every CSS url(...) in public stylesheets must resolve to an existing file.
  const publicDir = path.join(stage, 'apps/web/public');
  const cssFiles = ['clone.css', 'frontend/css/style.min.css', 'css/style_blocks.css', 'css/pages.css', 'css/fixes.css', 'css/inline.css'];
  for (const rel of cssFiles) {
    const css = readFileSync(path.join(publicDir, rel), 'utf8');
    for (const [, raw] of css.matchAll(/url\(([^)]+)\)/g)) {
      const clean = raw.replace(/['"\s]/g, '').split('?')[0].split('#')[0];
      if (!clean || clean.startsWith('data:')) continue;
      const resolved = clean.startsWith('/') ? path.join(publicDir, clean) : path.resolve(path.dirname(path.join(publicDir, rel)), clean);
      assert.ok(statSync(resolved).isFile(), `Missing CSS asset ${clean} in ${rel}`);
    }
  }
});
