import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { EventEmitter } from 'node:events';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { MODEL, ENDPOINT, TIMEOUT_MS, MAX_RESPONSE_BYTES, CATEGORIES, SCOPES, buildRequest, validateInput, validateResponse, createTransport, classify, status, main } from './jev-qc.mjs';

// All credentials and responses below are synthetic. No live API invocation.
const SYNTHETIC_KEY = 'SYNTHETIC_TEST_SECRET_DO_NOT_SEND';
const TMP = process.env.JEV_QC_TEST_TMP || os.tmpdir();
const script = fileURLToPath(new URL('./jev-qc.mjs',import.meta.url));
const note = '프레임에서 왼손 손가락이 하나 더 보인다.';
function fixture(t) {
  const root = fs.mkdtempSync(path.join(TMP,'jev-qc-test-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const input = path.join(root,'input.json'), out = path.join(root,'shadow.json');
  fs.writeFileSync(input,JSON.stringify({qc_note:note}));
  return {root,input,out};
}
function goodResponse() {
  const request = buildRequest(validateInput({qc_note:note}));
  const answers = {};
  for (const [id,q] of Object.entries(request.questions)) answers[id] = q.type === 'choice'
    ? {type:'choice',choice:'ANATOMY',probabilities:Object.fromEntries(CATEGORIES.map(k=>[k,k==='ANATOMY'?1:0])),confidence:1}
    : {type:'noul',noul:id==='observed_anatomy'?1:0};
  return {model:MODEL,answers,usage:{input_tokens:321,output_tokens:45}};
}
const noNetwork = () => { throw new Error('TEST_MUST_NOT_CONTACT_NETWORK'); };
function deps(transport = async()=>goodResponse()) { return {env:{TYPESAFE_API_KEY:SYNTHETIC_KEY},transport}; }
function assertShadow(record) {
  assert.equal(record.advisory,true); assert.equal(record.execution_authorized,false);
  assert.equal(record.visual_qc,'NOT_ASSESSED_BY_JEV');
  assert.match(record.input_sha256,/^[0-9a-f]{64}$/); assert.equal(record.schema_version,1);
  assert.equal(record.question_version,'jev-qc-1'); assert.ok(Number.isFinite(Date.parse(record.timestamp)));
  assert.equal(record.model_requested,MODEL);
  const text = JSON.stringify(record); assert.ok(!text.includes(note)); assert.ok(!text.includes(SYNTHETIC_KEY));
}
function mockHttp({statusCode=200, chunks=[Buffer.from(JSON.stringify(goodResponse()))], error} = {}) {
  const seen = [];
  const request = (url,options,callback) => {
    const req = new EventEmitter(); req.destroy = () => { req.destroyed=true; };
    req.end = body => {
      seen.push({url,options,body});
      queueMicrotask(()=>{
        if (error) { req.emit('error',new Error(error)); return; }
        const res = new EventEmitter(); res.statusCode = statusCode; res.destroy = ()=>{res.destroyed=true;};
        callback(res);
        for (const chunk of chunks) { if (!res.destroyed) res.emit('data',chunk); }
        if (!res.destroyed) res.emit('end');
      });
    };
    return req;
  };
  return {seen,transport:createTransport(request)};
}

test('status reports only presence, never a key or a network call',async()=>{
  assert.deepEqual(status({env:{TYPESAFE_API_KEY:SYNTHETIC_KEY}}),{key_present:true});
  assert.deepEqual(status({env:{}}),{key_present:false});
  const result = await main(['status'],deps(noNetwork));
  assert.deepEqual(result,{code:0,result:{key_present:true}});
});
test('missing key creates UNAVAILABLE without request',async t=>{
  const f=fixture(t); let calls=0;
  const r=await classify(f,{env:{},transport:()=>{calls++;}});
  assert.equal(calls,0); assert.equal(r.status,'UNAVAILABLE'); assert.equal(r.reason,'MISSING_KEY');
  assert.equal(r.answers,null); assert.equal(r.model_actual,null); assertShadow(r);
  assert.deepEqual(JSON.parse(fs.readFileSync(f.out)),r); assert.equal(fs.statSync(f.out).mode & 0o777,0o600);
});
test('dry-run does not read key-file, call transport or fabricate classifications',async t=>{
  const f=fixture(t); const r=await classify({...f,dryRun:true,keyFile:path.join(f.root,'does-not-exist')},deps(noNetwork));
  assert.equal(r.status,'DRY_RUN'); assert.equal(r.reason,'NO_REQUEST_SENT');
  assert.equal(r.answers,null); assert.equal(r.usage,null); assert.equal(r.model_actual,null); assertShadow(r);
});
test('successful classification is advisory, hashed and whitelist-only',async t=>{
  const f=fixture(t); let calls=0;
  const r=await classify(f,deps(async({body,key})=>{
    calls++; assert.equal(key,SYNTHETIC_KEY); assert.equal(fs.statSync(f.out).mode & 0o777,0o600);
    const request=JSON.parse(body); assert.deepEqual(Object.keys(request),['model','state','questions']);
    assert.deepEqual(request.state,{qc_note:note,observation_scope:'text_only'});
    assert.equal(request.model,MODEL); assert.equal(Object.keys(request.questions).length,8);
    return goodResponse();
  }));
  assert.equal(calls,1); assert.equal(r.status,'CLASSIFIED'); assert.equal(r.model_actual,MODEL);
  assert.equal(r.answers.category.choice,'ANATOMY'); assertShadow(r);
});
for (const scope of SCOPES) test('accepts explicit scope '+scope,()=>{
  assert.equal(validateInput({qc_note:note,observation_scope:scope}).observation_scope,scope);
});
for (const [name,value] of [
  ['null',null],['array',[]],['string','note'],['empty object',{}],['empty note',{qc_note:''}],
  ['blank note',{qc_note:' \n'}],['non-string',{qc_note:4}],['too long',{qc_note:'a'.repeat(6001)}],
  ['unknown media',{qc_note:note,media:'/private/video.mp4'}],['package',{qc_note:note,package:{}}],
  ['unknown scope',{qc_note:note,observation_scope:'PASS'}],['null scope',{qc_note:note,observation_scope:null}],
  ['prototype key',JSON.parse('{"qc_note":"test","__proto__":{}}')]
]) test('rejects invalid input: '+name,async t=>{
  const f=fixture(t);fs.writeFileSync(f.input,JSON.stringify(value));
  await assert.rejects(classify(f,deps(noNetwork)),/INVALID_INPUT/); assert.equal(fs.existsSync(f.out),false);
});
test('6000 Unicode characters are allowed but 6001 are not',()=>{
  assert.equal([...validateInput({qc_note:'🎬'.repeat(6000)}).qc_note].length,6000);
  assert.throws(()=>validateInput({qc_note:'🎬'.repeat(6001)}),/INVALID_INPUT/);
});
test('malformed JSON is sanitized before output or transport',async t=>{
  const f=fixture(t);fs.writeFileSync(f.input,'{"qc_note":'+SYNTHETIC_KEY);
  const r=await main(['classify','--input',f.input,'--out',f.out],deps(noNetwork));
  assert.equal(r.code,2);assert.deepEqual(r.result,{ok:false,error:'INVALID_INPUT'});assert.equal(fs.existsSync(f.out),false);
});
test('oversized input file is bounded',async t=>{
  const f=fixture(t);fs.writeFileSync(f.input,' '.repeat(65537));
  await assert.rejects(classify(f,deps(noNetwork)),/INVALID_INPUT_FILE/);
});
test('existing output refused before key access and request',async t=>{
  const f=fixture(t);fs.writeFileSync(f.out,'PRESERVE');let calls=0;
  await assert.rejects(classify({...f,keyFile:'/nonexistent'},deps(()=>{calls++;})),/OUTPUT_NOT_NEW_OR_WRITABLE/);
  assert.equal(calls,0);assert.equal(fs.readFileSync(f.out,'utf8'),'PRESERVE');
});
test('output symlink and input/output alias are never overwritten',async t=>{
  const f=fixture(t);const original=fs.readFileSync(f.input,'utf8');fs.symlinkSync(f.input,f.out);
  await assert.rejects(classify(f,deps(noNetwork)),/OUTPUT_NOT_NEW_OR_WRITABLE/);
  await assert.rejects(classify({...f,out:f.input},deps(noNetwork)),/OUTPUT_NOT_NEW_OR_WRITABLE/);
  assert.equal(fs.readFileSync(f.input,'utf8'),original);
});
test('secure synthetic key-file overrides environment without revealing contents',async t=>{
  const f=fixture(t);const keyFile=path.join(f.root,'synthetic.key');fs.writeFileSync(keyFile,SYNTHETIC_KEY+'\n',{mode:0o600});
  assert.deepEqual(status({keyFile,env:{}}),{key_present:true});
  const r=await classify({...f,keyFile},{env:{TYPESAFE_API_KEY:'different'},transport:async({key})=>{assert.equal(key,SYNTHETIC_KEY);return goodResponse();}});
  assert.equal(r.status,'CLASSIFIED');assertShadow(r);
});
for(const mode of [0o644,0o400,0o700,0o1600]) test('key-file rejects mode '+mode.toString(8),async t=>{
  const f=fixture(t);const keyFile=path.join(f.root,'synthetic.key');fs.writeFileSync(keyFile,SYNTHETIC_KEY);fs.chmodSync(keyFile,mode);
  const r=await classify({...f,keyFile},deps(noNetwork));assert.equal(r.reason,'INVALID_KEY_FILE');assert.equal(r.status,'UNAVAILABLE');assertShadow(r);
});
for(const kind of ['symlink','directory','missing','oversize','empty']) test('key-file rejects '+kind,async t=>{
  const f=fixture(t);const keyFile=path.join(f.root,'key');
  if(kind==='symlink') {const target=path.join(f.root,'target');fs.writeFileSync(target,SYNTHETIC_KEY,{mode:0o600});fs.symlinkSync(target,keyFile);}
  if(kind==='directory') fs.mkdirSync(keyFile,{mode:0o600});
  if(kind==='oversize') fs.writeFileSync(keyFile,'k'.repeat(8193),{mode:0o600});
  if(kind==='empty') fs.writeFileSync(keyFile,'',{mode:0o600});
  const r=await classify({...f,keyFile},deps(noNetwork));assert.equal(r.status,'UNAVAILABLE');assert.equal(r.reason,kind==='empty'?'MISSING_KEY':'INVALID_KEY_FILE');
});
test('key with header injection is rejected and never echoed',async t=>{
  const f=fixture(t);const r=await classify(f,{env:{TYPESAFE_API_KEY:SYNTHETIC_KEY+'\nX-Injected:1'},transport:noNetwork});
  assert.equal(r.reason,'INVALID_KEY');assertShadow(r);
});
for(const [name,change,reason='INVALID_RESPONSE'] of [
  ['unsupported model',r=>r.model='jev-latest','UNSUPPORTED_MODEL'],
  ['model reflects secret',r=>r.model=SYNTHETIC_KEY,'UNSUPPORTED_MODEL'],
  ['missing model',r=>delete r.model],['unknown top key',r=>r.note=note],
  ['missing answer ID',r=>delete r.answers.observed_audio],['unknown answer ID',r=>r.answers.other={type:'noul',noul:1}],
  ['wrong choice type',r=>r.answers.category.type='score'],['unknown category',r=>r.answers.category.choice='PASS'],
  ['missing probability',r=>delete r.answers.category.probabilities.AUDIO],['unknown probability',r=>r.answers.category.probabilities.PASS=0],
  ['negative probability',r=>r.answers.category.probabilities.AUDIO=-1],['over-one probability',r=>r.answers.category.probabilities.AUDIO=2],
  ['NaN',r=>r.answers.category.probabilities.AUDIO=NaN],['infinity',r=>r.answers.observed_audio.noul=Infinity],
  ['string probability',r=>r.answers.observed_audio.noul='0.1'],['incorrect sum',r=>r.answers.category.probabilities.AUDIO=.1],
  ['not highest choice',r=>r.answers.category.choice='AUDIO'],['invalid confidence',r=>r.answers.category.confidence=-1],
  ['wrong noul type',r=>r.answers.observed_audio.type='choice'],['noul excess',r=>r.answers.observed_audio.noul=1.1],
  ['extra answer text',r=>r.answers.observed_audio.explanation=SYNTHETIC_KEY],
  ['negative tokens',r=>r.usage.input_tokens=-1],['fractional tokens',r=>r.usage.input_tokens=1.2],
  ['infinite tokens',r=>r.usage.input_tokens=Infinity],['missing usage',r=>delete r.usage],['extra usage',r=>r.usage.secret=SYNTHETIC_KEY]
]) test('response rejects '+name,async t=>{
  const f=fixture(t);const response=goodResponse();change(response);
  const r=await classify(f,deps(async()=>response));assert.equal(r.status,'UNAVAILABLE');assert.equal(r.reason,reason);
  assert.equal(r.answers,null);assert.equal(r.usage,null);assert.equal(r.model_actual,null);assertShadow(r);
});
test('documented schema fixture validates, not a semantic accuracy claim',()=>{
  const response=goodResponse();assert.deepEqual(validateResponse(response,buildRequest(validateInput({qc_note:note}))),response);
});
test('mock HTTP sends fixed endpoint, Bearer key and one bounded request',async t=>{
  const f=fixture(t), mock=mockHttp();
  const r=await classify(f,{env:{TYPESAFE_API_KEY:SYNTHETIC_KEY,TYPESAFE_API_URL:'https://evil.invalid',HTTPS_PROXY:'https://evil.invalid'},transport:mock.transport});
  assert.equal(r.status,'CLASSIFIED');assert.equal(mock.seen.length,1);const sent=mock.seen[0];
  assert.equal(sent.url,ENDPOINT);assert.equal(sent.options.method,'POST');assert.equal(sent.options.headers.Authorization,'Bearer '+SYNTHETIC_KEY);
  assert.equal(sent.options.headers['Content-Length'],Buffer.byteLength(sent.body));
});
for(const code of [301,302,307,401,422,429,500,529]) test('HTTP '+code+' sanitized with no redirect or retry',async t=>{
  const f=fixture(t), mock=mockHttp({statusCode:code,chunks:[Buffer.from(SYNTHETIC_KEY+note)]});
  const r=await classify(f,deps(mock.transport));assert.equal(r.reason,'HTTP_ERROR');assert.equal(r.status,'UNAVAILABLE');assert.equal(mock.seen.length,1);assertShadow(r);
});
test('network error redacts message and response body',async t=>{
  const f=fixture(t), mock=mockHttp({error:SYNTHETIC_KEY+' '+note});
  const r=await classify(f,deps(mock.transport));assert.equal(r.reason,'NETWORK_ERROR');assertShadow(r);
});
test('arbitrary mock rejection cannot leak error text',async t=>{
  const f=fixture(t);const r=await classify(f,deps(async()=>{throw new Error(SYNTHETIC_KEY+note);}));
  assert.equal(r.reason,'INTERNAL_ERROR');assertShadow(r);
});
test('HTTP malformed response body is not recorded',async t=>{
  const f=fixture(t), mock=mockHttp({chunks:[Buffer.from(SYNTHETIC_KEY+note)]});
  const r=await classify(f,deps(mock.transport));assert.equal(r.reason,'INVALID_RESPONSE');assertShadow(r);
});
test('HTTP response body cap stops oversized payload',async t=>{
  const f=fixture(t), mock=mockHttp({chunks:[Buffer.alloc(MAX_RESPONSE_BYTES),Buffer.from('x')]});
  const r=await classify(f,deps(mock.transport));assert.equal(r.reason,'RESPONSE_TOO_LARGE');assert.equal(mock.seen.length,1);
});
test('timeout aborts exactly one hung mock request in bounded time',async t=>{
  const f=fixture(t);let calls=0,signal;const start=Date.now();
  const r=await classify(f,{...deps(({signal:s})=>{calls++;signal=s;return new Promise(()=>{});}),timeoutMs:30});
  assert.equal(TIMEOUT_MS,15000);assert.equal(calls,1);assert.equal(signal.aborted,true);assert.equal(r.reason,'TIMEOUT');assert.equal(r.status,'UNAVAILABLE');
  assert.ok(Date.now()-start<1500);assertShadow(r);
});
test('timeout cannot be increased beyond 15 seconds',async t=>{
  const f=fixture(t);await assert.rejects(classify(f,{...deps(noNetwork),timeoutMs:15001}),/INVALID_TIMEOUT/);
});
test('hash is canonical across omitted/default scope, changes when note changes',async t=>{
  const f=fixture(t);const a=await classify({...f,dryRun:true},deps(noNetwork));
  fs.writeFileSync(f.input,JSON.stringify({observation_scope:'text_only',qc_note:note}));
  const b=await classify({...f,out:path.join(f.root,'second.json'),dryRun:true},deps(noNetwork));assert.equal(a.input_sha256,b.input_sha256);
  fs.writeFileSync(f.input,JSON.stringify({qc_note:note+'!'}));
  const c=await classify({...f,out:path.join(f.root,'third.json'),dryRun:true},deps(noNetwork));assert.notEqual(a.input_sha256,c.input_sha256);
});
for(const args of [[],['approve'],['status','--out','x'],['classify'],['classify','--input','x','--out'],['status','--key-file','x','--key-file','y'],['classify','--input','x','--out','y','--model','other']]) test('strict CLI rejects '+JSON.stringify(args),async()=>{
  const r=await main(args,deps(noNetwork));assert.equal(r.code,2);assert.deepEqual(r.result,{ok:false,error:'INVALID_ARGUMENTS'});
});
test('actual CLI dry-run and missing-key exit codes, no network',t=>{
  const f=fixture(t);const env={PATH:process.env.PATH,TYPESAFE_API_KEY:''};
  const dry=spawnSync(process.execPath,[script,'classify','--input',f.input,'--out',f.out,'--dry-run'],{encoding:'utf8',env,timeout:2000});
  assert.equal(dry.status,0);assert.equal(JSON.parse(dry.stdout).status,'DRY_RUN');assert.equal(dry.stderr,'');
  const missing=spawnSync(process.execPath,[script,'classify','--input',f.input,'--out',path.join(f.root,'missing.json')],{encoding:'utf8',env,timeout:2000});
  assert.equal(missing.status,1);assert.equal(JSON.parse(missing.stdout).status,'UNAVAILABLE');
});
