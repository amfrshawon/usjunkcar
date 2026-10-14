import assert from 'node:assert/strict';
import { readFileSync, existsSync, appendFileSync } from 'node:fs';

const json = (path) => JSON.parse(readFileSync(path, 'utf8'));
const config = json('infra/deployment.json');
assert.equal(config.repository, 'amfrshawon/usjunkcar');
assert.equal(config.rootDirectory, 'apps/web');
assert.match(config.vercelCliVersion, /^\d+\.\d+\.\d+$/);
assert.deepEqual(Object.keys(config.environments).sort(), ['dev', 'main']);
assert.notEqual(config.environments.dev.projectId, config.environments.main.projectId);
for (const [branch, origin] of [['dev', 'https://dev.usjunkcars.si'], ['main', 'https://usjunkcars.si']]) {
  const target = config.environments[branch];
  assert.equal(target.origin, origin);
  assert.equal(target.environment, branch === 'main' ? 'production' : 'development');
  assert.equal(typeof target.enabled, 'boolean');
  assert.match(target.projectId, /^prj_[a-zA-Z0-9]+$/);
}
const launch = json('docs/launch-pages.json');
assert.equal(launch.maxPublicContentPages, 10);
assert.ok(launch.pages.length <= 10);
assert.equal(new Set(launch.pages.map(p => p.path)).size, launch.pages.length);
assert.equal(launch.productionOrigin, config.environments.main.origin);
assert.equal(launch.developmentOrigin, config.environments.dev.origin);

const hasApp = existsSync('apps/web/package.json');
const root = json('package.json');
if (hasApp || Object.values(config.environments).some(e => e.enabled)) {
  assert.ok(hasApp, 'Cannot enable deployment before apps/web exists');
  assert.match(root.packageManager ?? '', /^pnpm@\d+\.\d+\.\d+(\+sha\d+\..+)?$/, 'Pin pnpm in packageManager');
  assert.ok(existsSync('pnpm-lock.yaml'), 'Commit a frozen pnpm lockfile');
  for (const name of ['ci:check', 'ci:predeploy', 'ci:smoke']) {
    assert.ok(root.scripts?.[name], `Implement the ${name} contract before adding the app`);
  }
}
const target = config.environments[process.env.GITHUB_REF_NAME];
if (process.env.GITHUB_OUTPUT) {
  const values = {
    has_app: hasApp,
    deploy: Boolean(hasApp && target?.enabled),
    environment: target?.environment ?? '',
    origin: target?.origin ?? '',
    project_id: target?.projectId ?? '',
    team_id: config.teamId,
    cli_version: config.vercelCliVersion,
  };
  appendFileSync(process.env.GITHUB_OUTPUT, Object.entries(values).map(([k,v]) => `${k}=${v}\n`).join(''));
}
console.log(hasApp ? 'Infrastructure validated; application checks are required.' : 'Infrastructure validated. No Next.js app: deployments remain disabled.');
