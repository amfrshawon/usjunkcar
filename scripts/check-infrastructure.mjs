import assert from 'node:assert/strict';
import { readFileSync, existsSync, appendFileSync } from 'node:fs';
const json = p => JSON.parse(readFileSync(p, 'utf8'));
const c = json('infra/deployment.json');
assert.equal(c.repository, 'amfrshawon/usjunkcar');
assert.equal(c.provider, 'hostinger-vps');
assert.equal(c.host, '69.62.69.84');
assert.equal(c.rootDirectory, 'apps/web');
assert.deepEqual(Object.keys(c.environments).sort(), ['dev', 'main']);
assert.notEqual(c.environments.dev.port, c.environments.main.port);
assert.notEqual(c.environments.dev.sshUser, c.environments.main.sshUser);
for (const [branch, origin] of [['dev','https://dev.usjunkcars.si'],['main','https://usjunkcars.si']]) {
  assert.equal(c.environments[branch].origin, origin);
  assert.equal(c.environments[branch].environment, branch === 'dev' ? 'development' : 'production');
  assert.equal(c.environments[branch].sshUser, `usjunkcars-${branch}`);
  assert.equal(c.environments[branch].port, branch === 'dev' ? 3401 : 3400);
  assert.equal(typeof c.environments[branch].enabled, 'boolean');
}
const launch = json('docs/launch-pages.json');
assert.equal(launch.maxPublicContentPages, 10);
assert.ok(launch.pages.length <= 10);
assert.equal(new Set(launch.pages.map(p => p.path)).size, launch.pages.length);
const hasApp = existsSync('apps/web/package.json');
if (hasApp || Object.values(c.environments).some(e => e.enabled)) {
  assert.ok(hasApp, 'Cannot deploy before apps/web exists');
  const root = json('package.json');
  assert.match(root.packageManager ?? '', /^pnpm@\d+\.\d+\.\d+(\+sha\d+\..+)?$/);
  assert.ok(existsSync('pnpm-lock.yaml'));
  for (const name of ['ci:check','ci:package','ci:predeploy']) assert.ok(root.scripts?.[name], `Implement ${name}`);
}
const target = c.environments[process.env.GITHUB_REF_NAME];
const outputs = {has_app:hasApp, deploy:Boolean(hasApp && target?.enabled), environment:target?.environment??'', origin:target?.origin??'', ssh_user:target?.sshUser??'', host:c.host, node_version:c.nodeVersion};
if(process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT,Object.entries(outputs).map(([k,v])=>`${k}=${v}\n`).join(''));
console.log(hasApp ? 'VPS configuration validated; application checks required.' : 'VPS configuration validated. No app: application deployment disabled.');
