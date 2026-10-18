// Runs against an assembled standalone release (STAGE_DIR) built for EXPECT_ENV. Started by scripts/ci-check.mjs.
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
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

test('sitemap lists only public routes and robots match the environment', async () => {
  const sitemap = await (await fetch(`${origin}/sitemap.xml`)).text();
  const listed = [...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map(m => m[1]).sort();
  assert.deepEqual(listed, visible.map(r => `https://usjunkcars.si${r.path}`).sort());
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
    for (const bad of FORBIDDEN) assert.ok(!text.includes(bad), `${bad} found in ${where}`);
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
