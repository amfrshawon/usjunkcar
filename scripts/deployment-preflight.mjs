import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const config = JSON.parse(readFileSync('infra/deployment.json', 'utf8'));
const env = process.env;
const branch = env.GITHUB_REF_NAME;
const target = config.environments[branch];
assert.ok(target?.enabled, 'This branch is not enabled for deployment');
assert.equal(env.GITHUB_EVENT_NAME, 'push', 'Only branch pushes can deploy');
assert.equal(env.GITHUB_REPOSITORY, config.repository);
assert.equal(env.GITHUB_REF, `refs/heads/${branch}`);
assert.equal(env.VERCEL_ORG_ID, config.teamId);
assert.equal(env.VERCEL_PROJECT_ID, target.projectId);
assert.equal(env.APP_ENV, target.environment);
assert.equal(env.SITE_URL, target.origin);
assert.ok(env.VERCEL_TOKEN, 'Set VERCEL_TOKEN in the GitHub environment');

async function get(url, token) {
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' },
    signal: AbortSignal.timeout(20000),
  });
  assert.ok(response.ok, `Preflight request failed: HTTP ${response.status} at ${new URL(url).pathname}`);
  return response.json();
}
const gh = (path) => get(`https://api.github.com/repos/${config.repository}/${path}`, env.GH_TOKEN);
const head = await gh(`git/ref/heads/${branch}`);
assert.equal(head.object.sha, env.GITHUB_SHA, 'Refusing a stale commit');
const protection = await gh(`environments/${target.environment}`);
assert.equal(protection.deployment_branch_policy?.custom_branch_policies, true);
const policies = await gh(`environments/${target.environment}/deployment-branch-policies`);
assert.equal(policies.branch_policies.length, 1);
assert.equal(policies.branch_policies[0].name, branch);
assert.equal(policies.branch_policies[0].type, 'branch');
if (branch === 'main') {
  assert.equal(protection.can_admins_bypass, false);
  assert.ok(protection.protection_rules.some(rule => rule.type === 'required_reviewers' &&
    rule.reviewers?.some(item => item.reviewer?.login === 'amfrshawon')), 'Owner review must remain required');
}
const project = await get(`https://api.vercel.com/v9/projects/${target.projectId}?teamId=${config.teamId}`, env.VERCEL_TOKEN);
assert.equal(project.id, target.projectId);
assert.equal(project.accountId, config.teamId);
assert.equal(project.rootDirectory, config.rootDirectory);
assert.equal(project.framework, 'nextjs');
assert.ok(!project.link, 'Automatic Git deployments must remain disconnected');
assert.equal(project.ssoProtection?.deploymentType, branch === 'dev' ? 'all' : 'prod_deployment_urls_and_all_previews');
console.log(`Verified ${branch} → ${target.projectName} → ${target.origin} at ${env.GITHUB_SHA}`);
