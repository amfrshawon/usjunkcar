import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const checker = resolve('scripts/check-infrastructure.mjs');
function check(change) {
  const directory = mkdtempSync(join(tmpdir(), 'usjunkcar-ci-'));
  try {
    for (const path of ['infra', 'docs']) mkdirSync(join(directory, path));
    for (const path of ['infra/deployment.json', 'docs/launch-pages.json', 'package.json']) {
      writeFileSync(join(directory, path), readFileSync(path));
    }
    const config = JSON.parse(readFileSync(join(directory, 'infra/deployment.json')));
    for (const target of Object.values(config.environments)) target.enabled = false;
    change(config, directory);
    writeFileSync(join(directory, 'infra/deployment.json'), JSON.stringify(config));
    return spawnSync(process.execPath, [checker], { cwd: directory, encoding: 'utf8', env: { ...process.env, GITHUB_OUTPUT: '' } });
  } finally { rmSync(directory, { recursive: true, force: true }); }
}

test('planning repository validates without releasing the static fixture', () => {
  const result = check(() => {});
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /deployments remain disabled/);
});
test('enabling deployment before a real app exists fails closed', () => {
  const result = check(config => { config.environments.dev.enabled = true; });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Cannot enable deployment before apps\/web exists/);
});
test('development cannot target the production domain', () => {
  assert.notEqual(check(config => { config.environments.dev.origin = 'https://usjunkcars.si'; }).status, 0);
});
test('development cannot share the production hosting project', () => {
  assert.notEqual(check(config => { config.environments.dev.projectId = config.environments.main.projectId; }).status, 0);
});
