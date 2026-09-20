import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { request, seal, sha256 } from './harness.mjs';
import { prepare } from './submission.mjs';
import { prepare as prepareReferenceBundle } from './seedance-references.mjs';
const checker = fileURLToPath(new URL('./check.mjs', import.meta.url));
async function fixture(t) {
  const scratch = await fs.realpath(process.env.JEV_QC_TEST_TMP ?? os.tmpdir());
  const root = await fs.mkdtemp(path.join(scratch, 'aside-preflight-'));
  t.after(() => fs.rm(root, {recursive:true,force:true}));
  const prompt = '성인 댄서가 한 공간에서 천천히 체중을 이동하고 안정된 자세로 끝난다.';
  await fs.writeFile(path.join(root,'prompt.txt'), prompt);
  await request({stage:'seedance_prompt',context:{session_id:'FIXTURE_ONLY',prompt_language_override:{language:'ko-KR',reason:'Explicit fixture-only Korean case',user_instruction:'Write this synthetic test prompt in Korean.'},model:{provider:'openai-codex',modelId:'gpt-6-astra',thinkingLevel:'high'}},root,prompt:'prompt.txt',out:'request.json'});
  const req = JSON.parse(await fs.readFile(path.join(root,'request.json'),'utf8'));
  const mock = {role:'assistant',model:'gpt-6-astra',provider:'openai-codex',api:'openai-codex-responses',responseId:'FIXTURE_NOT_LIVE',usage:{input:1,output:1},timestamp:req.created_at+1,stopReason:'stop',content:[{type:'text',text:prompt + `
Knowledge-SHA256: ${req.knowledge.sha256}`}]};
  await fs.writeFile(path.join(root,'messages.jsonl'), JSON.stringify(mock)+'\n');
  await seal({request:path.join(root,'request.json'),evidence:path.join(root,'messages.jsonl'),out:'receipt.json'});
  const receiptHash = sha256(await fs.readFile(path.join(root,'receipt.json')));
  const payloadPrepared = await prepare({stage:'seedance_prompt',receipt:path.join(root,'receipt.json'),sha256:receiptHash,out:path.join(root,'payload.json')});
  const p = {provider_payload:{path:'payload.json',sha256:payloadPrepared.payload_sha256},video_workspace:'Video',video_input_mode:'Reference',harness_policy_version:1,execution_model:'inherit_session',prompt_file:'prompt.txt',prompt_sha256:sha256(prompt),duration_sec:15,references:[],generation_mode:'no_i2v_reference_native',provider_model:'Seedance 2.0',aspect_ratio:'16:9',resolution:'720p',audio:true,author_handoffs:[{receipt:'receipt.json',sha256:receiptHash}]};
  const run = async (observationOverride = {}) => {
    p.observed_settings = {observed_at:new Date().toISOString(),provider_model:p.provider_model,duration_sec:p.duration_sec,aspect_ratio:p.aspect_ratio,resolution:p.resolution,audio:p.audio,reference_count:p.references.length,video_workspace:'Video',video_input_mode:'Reference',mode_selection_verified:true,keyframe_slots_visible:false,...observationOverride};
    await fs.writeFile(path.join(root,'package.json'),JSON.stringify(p));
    const r=spawnSync(process.execPath,[checker,'preflight',path.join(root,'package.json')],{encoding:'utf8'});
    return {status:r.status,...JSON.parse(r.stdout)};
  };
  return {root,p,run};
}
test('preflight accepts a hash-bound Astra fixture, not production proof',async t=>{const f=await fixture(t);const r=await f.run();assert.equal(r.ok,true,JSON.stringify(r));assert.equal(r.status,0);});
test('preflight rejects package without author receipts',async t=>{const f=await fixture(t);f.p.author_handoffs=[];const r=await f.run();assert.equal(r.ok,false);assert.ok(r.errors.includes('ASTRA_HANDOFFS_REQUIRED'));});
test('preflight rejects forced Luna execution',async t=>{const f=await fixture(t);f.p.execution_model='gpt-5.6-luna';const r=await f.run();assert.ok(r.errors.includes('HARNESS_POLICY_REQUIRED'));});
test('preflight rejects prompt edited after Astra handoff even with updated package hash',async t=>{const f=await fixture(t);const s='Changed after handoff';await fs.writeFile(path.join(f.root,'prompt.txt'),s);f.p.prompt_sha256=sha256(s);const r=await f.run();assert.equal(r.ok,false);assert.ok(r.errors.some(e=>e.startsWith('AUTHOR_HANDOFF_FAILED')));});
test('preflight rejects different current prompt from valid author receipt',async t=>{const f=await fixture(t);await fs.writeFile(path.join(f.root,'other.txt'),'Different prompt');f.p.prompt_file='other.txt';f.p.prompt_sha256=sha256('Different prompt');const r=await f.run();assert.ok(r.errors.includes('SEEDANCE_AUTHOR_PROMPT_MISMATCH'));});

test('preflight rejects selected Keyframe even with a valid Astra receipt',async t=>{const f=await fixture(t);const r=await f.run({video_input_mode:'Keyframe',keyframe_slots_visible:true});assert.equal(r.ok,false);assert.ok(r.errors.includes('BLOCKED_REFERENCE_MODE_NOT_CONFIRMED'));});
test('preflight rejects an unverified Reference label',async t=>{const f=await fixture(t);const r=await f.run({mode_selection_verified:false});assert.equal(r.ok,false);assert.ok(r.errors.includes('BLOCKED_MODE_SELECTION_UNVERIFIED'));});

test('preflight rejects missing provider payload even with an Astra receipt',async t=>{const f=await fixture(t);delete f.p.provider_payload;const r=await f.run();assert.equal(r.ok,false);assert.ok(r.errors.includes('VERIFIED_PROVIDER_PAYLOAD_REQUIRED'));});

async function bindFixtureReferences(f, includePayload = true) {
  const image = path.join(f.root, 'fixture.png');
  // Signature-only fixture; not visual-QC or valid image decoding evidence.
  await fs.writeFile(image, Buffer.from('89504e470d0a1a0a01020304', 'hex'));
  const manifest = path.join(f.root, 'reference-manifest.json');
  await fs.writeFile(manifest, JSON.stringify([{path:image,sha256:sha256(await fs.readFile(image)),role:'FIXTURE_ONLY'}]));
  const bundle = await prepareReferenceBundle({references:manifest,outDir:path.join(f.root,'reference-bundle')});
  f.p.reference_bundle={path:bundle.plan,sha256:bundle.plan_sha256};
  f.p.references=JSON.parse(await fs.readFile(bundle.files.references.path,'utf8'));
  if(includePayload){
    const result=await prepare({stage:'seedance_prompt',receipt:path.join(f.root,'receipt.json'),sha256:f.p.author_handoffs[0].sha256,out:path.join(f.root,'bound-payload.json'),references:bundle.files.references.path});
    f.p.provider_payload={path:'bound-payload.json',sha256:result.payload_sha256};
  }
  return {bundle,image};
}
test('preflight binds frozen reference bundle to package and provider payload',async t=>{const f=await fixture(t);await bindFixtureReferences(f);const r=await f.run();assert.equal(r.ok,true,JSON.stringify(r));});
test('preflight rejects package references differing from frozen bundle',async t=>{const f=await fixture(t);await bindFixtureReferences(f);f.p.references=[];const r=await f.run();assert.ok(r.errors.includes('REFERENCE_BUNDLE_PACKAGE_MISMATCH'));});
test('preflight rejects provider payload references differing from frozen bundle',async t=>{const f=await fixture(t);await bindFixtureReferences(f,false);const r=await f.run();assert.ok(r.errors.includes('REFERENCE_BUNDLE_PAYLOAD_MISMATCH'));});
test('preflight rejects reference source changed after bundle preparation',async t=>{const f=await fixture(t);const {image}=await bindFixtureReferences(f);await fs.writeFile(image,'changed');const r=await f.run();assert.ok(r.errors.includes('REFERENCE_BUNDLE_VERIFICATION_FAILED'));});
test('preflight rejects wrong independently accepted bundle hash',async t=>{const f=await fixture(t);await bindFixtureReferences(f);f.p.reference_bundle.sha256='0'.repeat(64);const r=await f.run();assert.ok(r.errors.includes('REFERENCE_BUNDLE_VERIFICATION_FAILED'));});
test('preflight rejects invalid optional bundle link',async t=>{const f=await fixture(t);f.p.reference_bundle=null;const r=await f.run();assert.ok(r.errors.includes('INVALID_REFERENCE_BUNDLE_LINK'));});
