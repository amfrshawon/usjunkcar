// Full application check for CI and local runs: registry, types, both environment builds and the site tests.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, existsSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';

const run = (cmd, args, env = {}) => execFileSync(cmd, args, { stdio: 'inherit', env: { ...process.env, NEXT_TELEMETRY_DISABLED: '1', ...env } });

// Route registry: unique ids/paths, content present, cap respected.
const registry = JSON.parse(readFileSync('content/publication.json', 'utf8'));
const ids = registry.routes.map(r => r.id), paths = registry.routes.map(r => r.path);
assert.equal(new Set(ids).size, ids.length, 'Duplicate route id');
assert.equal(new Set(paths).size, paths.length, 'Duplicate route path');
assert.ok(registry.routes.length <= registry.maxPublicContentPages, 'Registry exceeds the public page cap');
for (const r of registry.routes) {
  assert.ok(existsSync(`content/pages/${r.id}.html`), `Missing content for ${r.id}`);
  assert.ok(['draft', 'review', 'approved', 'published', 'archived'].includes(r.status), `Bad status for ${r.id}`);
  assert.ok(r.status !== 'published' || r.approval, `${r.id} is published without an approval record`);
}

run('pnpm', ['--filter', '@usjunkcars/web', 'typecheck']);

for (const env of ['development', 'production']) {
  const stage = mkdtempSync(path.join(tmpdir(), `usjunkcars-${env}-`));
  try {
    run('python3', ['scripts/package-app.py', '--stage', stage, '--env', env]);
    run('node', ['--test', 'apps/web/tests/*.test.mjs'], { STAGE_DIR: stage, EXPECT_ENV: env });
  } finally {
    rmSync(stage, { recursive: true, force: true });
  }
}
console.log('ci:check passed');
