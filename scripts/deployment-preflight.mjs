import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const c=JSON.parse(readFileSync('infra/deployment.json','utf8'));
const e=process.env, t=c.environments[e.GITHUB_REF_NAME];
assert.ok(t?.enabled || (c.staticDevPreview && e.GITHUB_REF_NAME === 'dev') || (c.staticProduction && e.GITHUB_REF_NAME === 'main'));
assert.equal(e.GITHUB_EVENT_NAME,'push');
assert.equal(e.GITHUB_REPOSITORY,c.repository);
assert.equal(e.GITHUB_REF,`refs/heads/${e.GITHUB_REF_NAME}`);
async function get(path) {
  const r=await fetch(`https://api.github.com/repos/${c.repository}/${path}`,{headers:{Authorization:`Bearer ${e.GH_TOKEN}`},signal:AbortSignal.timeout(20000)});
  assert.ok(r.ok,`GitHub control check failed: ${r.status}`);return r.json();
}
assert.equal((await get(`git/ref/heads/${e.GITHUB_REF_NAME}`)).object.sha,e.GITHUB_SHA,'Stale commit');
const protection=await get(`environments/${t.environment}`);
assert.equal(protection.deployment_branch_policy?.custom_branch_policies,true);
const policies=(await get(`environments/${t.environment}/deployment-branch-policies`)).branch_policies;
assert.equal(policies.length,1);assert.equal(policies[0].name,e.GITHUB_REF_NAME);assert.equal(policies[0].type,'branch');
// Production needs no deployment reviewer (removed by the owner on 2026-10-18): the owner's approval is
// the reviewed dev → main merge. The main-only branch policy above and no admin bypass still apply.
if(e.GITHUB_REF_NAME==='main') assert.equal(protection.can_admins_bypass,false);
console.log(`Verified ${e.GITHUB_REF_NAME} → ${t.origin} at ${e.GITHUB_SHA}`);
