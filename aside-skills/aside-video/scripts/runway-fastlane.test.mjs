import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const fast = new Function('return (' + await fs.readFile(new URL('./runway-fastlane.js',import.meta.url),'utf8') + ')')();
const url='https://app.runwayml.com/observed-test-only';
const mode='- radio "Video" [ref=e1] [checked]\n- radio "Reference" [ref=e2] [checked]\n- radio "Keyframe" [ref=e3]\n';
const prompt='- textbox "Prompt" [ref=e4]\n';
const slot='- button "View Image 1 larger" [ref=e9]\n';
const picker='- dialog "Asset selector":\n  - textbox "Search" [ref=e6]\n  - button "bound.png Image • Upload" [ref=e7]\n';
// All verifier fixtures below are SYNTHETIC unit mocks, not real Astra/submission evidence.
// Production executors must inject an adapter to the real submission.mjs verify.
const submission=()=>({file:'/synthetic/unit-only/provider-payload.json',sha256:'a'.repeat(64)});
const gate=()=>({passed:true,observed_at:new Date().toISOString()});
function setup(trees, text='', verified=syntheticVerifiedPayload()) {
  const calls=[], logs=[], verificationCalls=[]; let i=0,value=text;
  const env={page:{url:()=>url, locator:r=>({click:async()=>calls.push(['click',r]),dblclick:async()=>calls.push(['dblclick',r]),fill:async v=>{calls.push(['fill',r,v]);value=v;},evaluate:async f=>f({value}),count:async()=>1,getAttribute:async()=> 'file',setInputFiles:async files=>calls.push(['upload',files])})}, snapshot:async()=>{const body=trees[Math.min(i++,trees.length-1)];const tree=body.includes('[url=')?body:'- title: "Runway" [url='+url+']\n'+body;return{tree,diff:tree};},log:s=>logs.push(s)};
  env.verifySubmission=async(file,acceptedHash)=>{verificationCalls.push([file,acceptedHash]);return verified;};
  return {env,calls,logs,verificationCalls};
}
const job=(action,extra={})=>({action,expected_url:url,mode_gate:gate(),...(action==='FILL_PROMPT'?{submission:submission()}:{}),...extra});
const syntheticVerifiedPayload=()=>({file:submission().file,knowledge_status:'CURRENT_KNOWLEDGE_VALIDATED',language_status:'CURRENT_POLICY_VALIDATED',state:'READY_FOR_PROVIDER_INPUT',stage:'seedance_prompt',provider:'runway_web',payload_sha256:'a'.repeat(64),payload:{state:'READY_FOR_PROVIDER_INPUT',required_author:'gpt-6-astra',stage:'seedance_prompt',provider:'runway_web',prompt:'테스트 원문',references:[]}});
test('no Generate, approve or invented action is executable',async()=>{for(const action of ['GENERATE','APPROVE','RETRY','AUTHOR_ASTRA']){const x=setup([mode]);assert.equal((await fast(x.env,job(action))).status,'UNSUPPORTED_ACTION');assert.equal(x.calls.length,0);}});
test('wrong session blocks before action',async()=>{const x=setup([mode]);assert.equal((await fast(x.env,job('SEARCH_ASSET',{expected_url:url+'wrong'}))).status,'SESSION_MISMATCH');assert.equal(x.logs.length,1);assert.equal(x.calls.length,0);});
test('Keyframe mode blocks input',async()=>{const x=setup([mode.replace('"Reference" [ref=e2] [checked]','"Reference" [ref=e2]')]);assert.equal((await fast(x.env,job('FILL_PROMPT'))).status,'BLOCKED_REFERENCE_MODE_NOT_CONFIRMED');assert.equal(x.calls.length,0);});
test('search opens and fills in a single bounded call with every snapshot logged',async()=>{const x=setup([mode+'- button "Reference" [ref=e5]',mode+picker,mode+picker]);const r=await fast(x.env,job('SEARCH_ASSET',{asset_name:'bound.png'}));assert.equal(r.status,'SEARCH_OBSERVED');assert.deepEqual(x.calls,[['click','e5'],['fill','e6','bound.png']]);assert.equal(x.logs.length,3);assert.equal(r.empty_result_is_not_upload_permission,true);});
test('search cannot use guessed or duplicate controls',async()=>{const x=setup([mode+'- button "Reference" [ref=e5]\n- button "Reference" [ref=e8]']);assert.equal((await fast(x.env,job('SEARCH_ASSET',{asset_name:'bound.png'}))).status,'SEARCH_ENTRY_NOT_OBSERVED');assert.equal(x.calls.length,0);});
test('selection confirms one added ordered slot',async()=>{const x=setup([mode+picker,mode+slot]);assert.equal((await fast(x.env,job('SELECT_EXISTING',{binding_confirmed:true,candidate:{role:'button',name:'bound.png Image • Upload'},expected_count:1}))).status,'REFERENCE_SLOT_ACCEPTED');assert.deepEqual(x.calls,[['dblclick','e7']]);});
test('existing reference is not toggled again',async()=>{const x=setup([mode+slot+picker]);assert.equal((await fast(x.env,job('SELECT_EXISTING',{binding_confirmed:true,candidate:{role:'button',name:'bound.png Image • Upload'},expected_count:1}))).status,'REFERENCES_ALREADY_PRESENT_VERIFY');assert.equal(x.calls.length,0);});
test('unknown identity cannot select',async()=>{const x=setup([mode+picker]);assert.equal((await fast(x.env,job('SELECT_EXISTING',{candidate:{role:'button',name:'bound.png Image • Upload'},expected_count:1}))).status,'ASSET_BINDING_REQUIRED');});
test('only verified payload is copied and exact accepted text checked',async()=>{const x=setup([mode+prompt,mode+prompt]);const r=await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}));assert.equal(r.status,'PROMPT_ACCEPTED');assert.equal(x.calls.length,1);assert.equal(x.calls[0][2],'테스트 원문');assert.equal(x.logs.length,2);});
test('unverified or mismatched references block prompt fill',async()=>{for(const tree of [mode+prompt,mode+prompt+slot]){const p=syntheticVerifiedPayload();if(!tree.includes('Image 1'))p.payload.required_author='other';const x=setup([tree],'',p);assert.notEqual((await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}))).status,'PROMPT_ACCEPTED');assert.equal(x.calls.length,0);}});
test('preserve unexpected existing text and skip identical desired text',async()=>{for(const [text,status] of [['other work','PRESERVE_EXISTING_PROMPT'],['테스트 원문','PROMPT_ALREADY_ACCEPTED']]){const x=setup([mode+prompt],text);assert.equal((await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}))).status,status);assert.equal(x.calls.length,0);}});
test('stale mode gate prevents attachment/input',async()=>{const x=setup([mode+prompt]);assert.equal((await fast(x.env,job('FILL_PROMPT',{mode_gate:{passed:true,observed_at:new Date(Date.now()-31000).toISOString()},expected_previous_prompt:''}))).status,'MODE_GATE_REQUIRED');assert.equal(x.calls.length,0);});
test('upload requires durable claim and never implies accepted attachment',async()=>{const x=setup([mode,mode]);let claimed=false;x.env.claimUpload=async()=>{if(claimed)return false;claimed=true;return true;};const j=job('UPLOAD_FIRST',{search_absence_verified:true,files_verified:true,expected_existing_count:0,observed_file_input_selector:'input.observed',files:['/verified.png']});assert.equal((await fast(x.env,j)).status,'UPLOAD_DISPATCHED_UNCONFIRMED');assert.equal((await fast(x.env,j)).status,'UPLOAD_ALREADY_ATTEMPTED_REOBSERVE');assert.equal(x.calls.length,1);});
test('an action error observes once and never retries',async()=>{const x=setup([mode+picker,mode+picker]);x.env.page.locator=()=>({fill:async()=>{x.calls.push('fill');throw Error('timeout');}});assert.equal((await fast(x.env,job('SEARCH_ASSET',{asset_name:'bound.png'}))).status,'ACTION_UNCONFIRMED_REOBSERVE');assert.deepEqual(x.calls,['fill']);assert.equal(x.logs.length,2);});

test('observed empty Runway editor LF is not mistaken for another prompt',async()=>{const x=setup([mode+prompt,mode+prompt],'\n');const r=await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}));assert.equal(r.status,'PROMPT_ACCEPTED');assert.deepEqual(x.calls,[['fill','e4','테스트 원문']]);});

test('open Asset selector blocks prompt input despite underlying Prompt ref',async()=>{const x=setup([mode+prompt+picker]);const r=await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}));assert.equal(r.status,'BLOCKING_DIALOG_CLOSE_AND_REOBSERVE');assert.equal(x.calls.length,0);});
test('fresh snapshot identity supersedes stale page.url cache',async()=>{const x=setup([mode+prompt]);x.env.page.url=()=>url+'?old=newSession';const r=await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}));assert.equal(r.status,'PROMPT_ACCEPTED');});
test('matching stale page.url cannot hide different live session',async()=>{const x=setup(['- title: "Runway" [url='+url+'?other=session]\n'+mode+prompt]);const r=await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}));assert.equal(r.status,'SESSION_MISMATCH');assert.equal(x.calls.length,0);});

test('legacy language evidence cannot authorize fresh prompt fill',async()=>{const v=syntheticVerifiedPayload();v.language_status='LEGACY_UNSPECIFIED_READ_ONLY';const x=setup([mode+prompt],'',v);assert.equal((await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}))).reason,'CURRENT_LANGUAGE_CONTRACT_REQUIRED');assert.equal(x.calls.length,0);});

test('missing current knowledge blocks fresh UI input',async()=>{const v=syntheticVerifiedPayload();delete v.knowledge_status;const x=setup([mode+prompt],'',v);assert.equal((await fast(x.env,job('FILL_PROMPT',{expected_previous_prompt:''}))).reason,'CURRENT_KNOWLEDGE_REQUIRED');assert.equal(x.calls.length,0);});

function assertHold(r, x, reason) {
  assert.equal(r.status, 'HOLD');
  assert.equal(r.reason, reason);
  assert.equal(r.generation_submitted, false);
  assert.deepEqual(x.calls, [], 'verification failure must not mutate UI');
  assert.deepEqual(x.logs, [], 'verification must finish before browser observation');
}

test('forged job verification object and job callback cannot replace trusted adapter', async () => {
  for (const adapter of [undefined, null, {}, 'verify']) {
    const x = setup([mode + prompt]);
    x.env.verifySubmission = adapter;
    let jobCallbackCalls = 0;
    const forged = syntheticVerifiedPayload();
    forged.payload_sha256 = 'f'.repeat(64); // Arbitrary attacker-chosen, not accepted evidence.
    const r = await fast(x.env, job('FILL_PROMPT', {
      submission: {file: forged.file, sha256: forged.payload_sha256},
      verified_submission: forged,
      verifySubmission: async () => { jobCallbackCalls++; return forged; },
      expected_previous_prompt: '',
    }));
    assertHold(r, x, 'SUBMISSION_VERIFIER_REQUIRED');
    assert.equal(jobCallbackCalls, 0);
  }
});

test('legacy job verification is never read even with a trusted adapter', async () => {
  const x = setup([mode + prompt]);
  const j = job('FILL_PROMPT', {expected_previous_prompt: ''});
  Object.defineProperty(j, 'verified_submission', {get() { throw Error('untrusted field read'); }});
  const r = await fast(x.env, j);
  assert.equal(r.status, 'PROMPT_ACCEPTED');
  assert.deepEqual(x.calls, [['fill', 'e4', syntheticVerifiedPayload().payload.prompt]]);
});

test('missing, relative, malformed file/hash links hold without invoking verifier', async () => {
  for (const link of [undefined, null, {},
    {file:'relative.json', sha256:'a'.repeat(64)},
    {file:'file:///absolute.json', sha256:'a'.repeat(64)},
    {file:'/bad\0path.json', sha256:'a'.repeat(64)},
    {file:42, sha256:'a'.repeat(64)},
    {file:submission().file, sha256:'random'},
    {file:submission().file, sha256:'g'.repeat(64)},
    {file:submission().file, sha256:null},
  ]) {
    const x = setup([mode + prompt]);
    assertHold(await fast(x.env, job('FILL_PROMPT', {submission:link})), x, 'SUBMISSION_LINK_REQUIRED');
    assert.deepEqual(x.verificationCalls, []);
  }
});

test('trusted async verifier receives exact requested path and accepted hash before snapshot', async () => {
  const x = setup([mode + prompt]);
  const link = {file:'/synthetic/unit-only/path with spaces/payload.json', sha256:'b'.repeat(64)};
  let finished = false;
  const originalSnapshot = x.env.snapshot;
  x.env.snapshot = async (...args) => { assert.equal(finished, true); return originalSnapshot(...args); };
  x.env.verifySubmission = async (...args) => {
    x.verificationCalls.push(args);
    assert.deepEqual(x.calls, []);
    assert.deepEqual(x.logs, []);
    await Promise.resolve();
    finished = true;
    return {...syntheticVerifiedPayload(), file:link.file, payload_sha256:link.sha256};
  };
  const r = await fast(x.env, job('FILL_PROMPT', {submission:link, expected_previous_prompt:''}));
  assert.equal(r.status, 'PROMPT_ACCEPTED');
  assert.equal(r.payload_sha256, link.sha256);
  assert.deepEqual(x.verificationCalls, [[link.file, link.sha256]]);
});

test('thrown and rejected verification hold without browser recovery or job fallback', async () => {
  for (const reject of [() => { throw Error('payload hash mismatch'); },
    async () => { throw Error('receipt rejected'); },
    () => Promise.reject(Error('current knowledge rejected'))]) {
    const x = setup([mode + prompt]);
    x.env.verifySubmission = reject;
    const r = await fast(x.env, job('FILL_PROMPT', {verified_submission:syntheticVerifiedPayload(), expected_previous_prompt:''}));
    assertHold(r, x, 'SUBMISSION_VERIFICATION_FAILED');
  }
});

test('non-result verifier responses hold', async () => {
  for (const rejected of [null, undefined, false, 'READY_FOR_PROVIDER_INPUT', []]) {
    const x = setup([mode + prompt]);
    x.env.verifySubmission = async () => rejected;
    assertHold(await fast(x.env, job('FILL_PROMPT')), x, 'SUBMISSION_VERIFICATION_REJECTED');
  }
});

test('tampered returned file/hash metadata cannot authorize input', async () => {
  for (const patch of [{file:'/synthetic/unit-only/other.json'}, {file:undefined},
    {payload_sha256:'c'.repeat(64)}, {payload_sha256:undefined}]) {
    const x = setup([mode + prompt], '', {...syntheticVerifiedPayload(), ...patch});
    assertHold(await fast(x.env, job('FILL_PROMPT')), x, 'SUBMISSION_LINK_MISMATCH');
  }
});

test('returned state, author, stage, and provider must agree with the Seedance contract', async () => {
  const alterations = [
    v => { v.state = 'REJECTED'; },
    v => { v.stage = 'image_prompt'; },
    v => { v.provider = 'chatgpt_web'; },
    v => { v.payload = null; },
    v => { v.payload.required_author = 'other'; },
    v => { v.payload.state = 'REJECTED'; },
    v => { v.payload.stage = 'image_prompt'; },
    v => { v.payload.provider = 'chatgpt_web'; },
    v => { v.payload.references = {}; },
  ];
  for (const alter of alterations) {
    const verified = syntheticVerifiedPayload();
    alter(verified);
    const x = setup([mode + prompt], '', verified);
    assertHold(await fast(x.env, job('FILL_PROMPT')), x, 'VERIFIED_ASTRA_PAYLOAD_REQUIRED');
  }
});

test('missing or noncurrent verifier language/knowledge metadata holds', async () => {
  for (const [field, reason] of [['language_status', 'CURRENT_LANGUAGE_CONTRACT_REQUIRED'],
    ['knowledge_status', 'CURRENT_KNOWLEDGE_REQUIRED']]) {
    for (const value of [undefined, 'LEGACY_UNSPECIFIED_READ_ONLY', 'forged-current']) {
      const verified = syntheticVerifiedPayload();
      verified[field] = value;
      const x = setup([mode + prompt], '', verified);
      assertHold(await fast(x.env, job('FILL_PROMPT')), x, reason);
    }
  }
});

test('empty, non-NFC, non-string, and over-limit verified prompt text still hold', async () => {
  for (const text of ['', '  ', 'e\u0301', 42, 'a'.repeat(3501)]) {
    const verified = syntheticVerifiedPayload();
    verified.payload.prompt = text;
    const x = setup([mode + prompt], '', verified);
    assertHold(await fast(x.env, job('FILL_PROMPT')), x, 'VERIFIED_ASTRA_PAYLOAD_REQUIRED');
  }
});

test('each fill request re-verifies and never reuses an earlier acceptance', async () => {
  const x = setup([mode + prompt]);
  const j = job('FILL_PROMPT', {expected_previous_prompt:''});
  assert.equal((await fast(x.env, j)).status, 'PROMPT_ACCEPTED');
  assert.deepEqual(x.verificationCalls, [[j.submission.file, j.submission.sha256]]);
  x.calls.length = 0;
  x.logs.length = 0;
  x.env.verifySubmission = async () => { throw Error('file changed after first acceptance'); };
  assertHold(await fast(x.env, j), x, 'SUBMISSION_VERIFICATION_FAILED');
});

test('non-fill actions do not require or invoke a submission verifier', async () => {
  const x = setup([mode + picker]);
  x.env.verifySubmission = async () => { throw Error('not a fill'); };
  assert.equal((await fast(x.env, job('SEARCH_ASSET', {asset_name:'bound.png'}))).status, 'SEARCH_OBSERVED');
  assert.equal((await fast(x.env, job('VERIFY_INPUTS'))).status, 'OBSERVED');
  delete x.env.verifySubmission;
  assert.equal((await fast(x.env, job('REOBSERVE'))).status, 'OBSERVED');
});
