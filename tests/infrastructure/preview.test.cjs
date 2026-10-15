const {test,after,before}=require('node:test');
const assert=require('node:assert/strict');
const server=require('../../infra/vps/preview-server.cjs');
let origin;
before(async()=>{process.env.APP_ENV='development';process.env.RELEASE_SHA='a'.repeat(40);await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));origin=`http://127.0.0.1:${server.address().port}`;});
after(()=>new Promise(resolve=>server.close(resolve)));
test('health identifies the dev release',async()=>{const r=await fetch(origin+'/api/v1/health');assert.equal(r.status,200);assert.equal((await r.json()).data.commit,'a'.repeat(40));});
test('preview cannot receive leads',async()=>{assert.equal((await fetch(origin+'/api/v1/leads',{method:'POST',body:'test'})).status,405);});
test('repository and traversal paths are unavailable',async()=>{for(const p of ['/.git/config','/server.js','/%2e%2e%2fserver.js','/AGENTS.md']) assert.equal((await fetch(origin+p)).status,404);});
