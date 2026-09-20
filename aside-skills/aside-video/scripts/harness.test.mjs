import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { DEFAULT_POLICY as policy, route, status, request, seal, verify, sha256, main } from './harness.mjs';

const astra = { provider: 'openai-codex', modelId: 'gpt-6-astra', thinkingLevel: 'medium' };
const other = { provider: 'example', modelId: 'other', thinkingLevel: 'high' };
const context = { session_id: 'session-test', task_id: 'task-test', user_instruction: 'Create an image prompt for a portrait.', model: astra };
const finalPrompt = 'Photorealistic portrait in natural light.\n';
async function fixture(t) {
  const root = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'aside-harness-test-')));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.writeFile(path.join(root, 'prompt.txt'), 'Initial brief\n');
  const req = await request({ stage: 'image_prompt', context, root, prompt: 'prompt.txt', out: 'request.json' });
  await fs.writeFile(path.join(root, 'prompt.txt'), finalPrompt);
  const message = {
    role: 'assistant', content: [{ type: 'text', text: finalPrompt + `\nKnowledge-SHA256: ${req.knowledge.sha256}` }],
    api: 'openai-codex-responses', provider: 'openai-codex', model: 'gpt-6-astra',
    usage: { input: 50, output: 30 }, stopReason: 'stop', rawStopReason: 'completed',
    timestamp: req.created_at + 1, responseId: 'resp_test_generated',
  };
  const transcriptRoot = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'aside-harness-transcript-')));
  t.after(() => fs.rm(transcriptRoot, { recursive: true, force: true }));
  const evidence = path.join(transcriptRoot, 'messages.jsonl');
  const write = async (m = message) => { const copy = structuredClone(m); if (Array.isArray(copy.content)) for (const c of copy.content) if (c.type === 'text' && !c.text.includes('Knowledge-SHA256:')) c.text += `\nKnowledge-SHA256: ${req.knowledge.sha256}`; return fs.writeFile(evidence, `${JSON.stringify(copy)}\n`); };
  await write();
  const sealIt = (out = 'receipt.json') => seal({ request: req.file, evidence, out });
  return { root, req, evidence, message, write, sealIt };
}
async function replaceJson(file, mutate) {
  const obj = JSON.parse(await fs.readFile(file, 'utf8'));
  mutate(obj);
  const bytes = `${JSON.stringify(obj, null, 2)}\n`;
  await fs.chmod(file, 0o644);
  await fs.writeFile(file, bytes);
  return sha256(bytes);
}

test('status expresses exact model, preferred not mandatory effort and image policy', () => {
  const s = status();
  assert.equal(s.author_model, 'gpt-6-astra');
  assert.equal(s.prompt_language_default, 'en-US');
  assert.equal(s.handoff_schema_version, 2);
  assert.equal(s.legacy_language_policy, 'read_only');
  assert.equal(s.author_effort_required, false);
  assert.equal(s.image_product, 'ChatGPT Images 2.5');
  assert.equal(s.image_provider, 'chatgpt_web');
});
test('Astra author uses direct plan even below xhigh', () => {
  for (const stage of policy.author_stages) {
    const p = route(stage, context);
    assert.equal(p.mode, 'direct');
    assert.equal(p.effort_required, false);
    assert.equal(p.actual_execution_proven, false);
    assert.equal(p.settings_writes, false);
  }
});
test('every executor always inherits current session without model override', () => {
  for (const stage of policy.executor_stages) {
    for (const model of [astra, other, undefined]) {
      const p = route(stage, { model });
      assert.equal(p.role, 'executor');
      assert.equal(p.mode, 'inherit_session');
      assert.equal(p.execution_model, 'inherit_session');
      assert.equal(p.planned_model, undefined);
    }
  }
});
test('other model chooses first exact Astra category, bounded plan only', () => {
  const p = route('music_prompt', { model: other, modelCategories: { standard: other, deep: astra, visual: astra, fast: astra } });
  assert.equal(p.mode, 'functions.subagent');
  assert.equal(p.category, 'deep');
  assert.equal(p.max_tasks, 1);
  assert.equal(p.max_minutes, 10);
  assert.equal(p.scope, 'prompt_content_only');
});
test('category preference is standard/deep/visual/fast', () => {
  for (const category of ['standard', 'deep', 'visual', 'fast']) {
    assert.equal(route('seedance_prompt', { model: other, modelCategories: { [category]: astra } }).category, category);
  }
  assert.equal(route('music_prompt', { modelCategories: { fast: astra, deep: astra, standard: astra } }).category, 'standard');
});
test('missing and approximate author models HOLD', () => {
  for (const ctx of [{}, { model: other }, { model: { modelId: 'gpt-6-astra-latest' }, modelCategories: { standard: { modelId: 'astra' } } }]) {
    assert.equal(route('image_prompt', ctx).state, 'HOLD_ASTRA_AUTHOR_REQUIRED');
  }
});
test('unknown stages and policy drift fail', () => {
  assert.throws(() => route('secret_stage', context), /Unknown stage/);
  assert.throws(() => route('planning', context, { ...policy, execution_model: 'luna' }), /Invalid policy/);
});
test('request is immutable and records initial hash and role boundary', async t => {
  const f = await fixture(t);
  assert.equal(f.req.initial_prompt_sha256, sha256('Initial brief\n'));
  assert.equal(f.req.schema_version, 2);
  assert.deepEqual(f.req.language_contract, { language: 'en-US', user_instruction: 'Create an image prompt for a portrait.', preserved_literals: [], override_reason: null });
  assert.match(f.req.author_task, /English prose by default/);
  assert.match(f.req.author_task, /prompt content only/);
  assert.match(f.req.author_task, /No execution is authorized/);
  await assert.rejects(request({ stage: 'image_prompt', context, root: f.root, prompt: 'prompt.txt', out: 'request.json' }), /EEXIST/);
  await assert.rejects(request({ stage: 'image_prompt', context: {}, root: f.root, prompt: 'prompt.txt', out: 'hold.json' }), /HOLD_ASTRA_AUTHOR_REQUIRED/);
  await assert.rejects(request({ stage: 'video_qc', context, root: f.root, prompt: 'prompt.txt', out: 'exec.json' }), /only for author stages/);
});
test('seal and verify exact assistant prompt with provenance and immutable receipt', async t => {
  const f = await fixture(t);
  const result = await f.sealIt();
  assert.equal(result.state, 'READY_FOR_EXECUTION');
  assert.equal(result.author_record.binding, 'exact_final_prompt');
  assert.equal(result.author_record.model, 'gpt-6-astra');
  assert.equal(result.session_id, null);
  assert.equal(result.task_id, null);
  assert.equal(result.requester_session_id, 'session-test');
  assert.equal(result.requester_task_id, 'task-test');
  assert.equal(result.request_sha256, f.req.sha256);
  assert.equal(result.evidence.source.path, f.evidence);
  assert.equal(result.prompt.sha256, sha256(finalPrompt));
  assert.equal(result.receipt_sha256, result.file_sha256);
  const serialized = JSON.parse(await fs.readFile(result.file, 'utf8'));
  assert.equal(serialized.receipt_sha256, undefined);
  assert.equal(serialized.file_sha256, undefined);
  assert.equal(serialized.sha256, undefined);
  assert.equal(result.evidence.sha256, sha256(await fs.readFile(path.join(f.root, result.evidence.path))));
  const verified = await verify(result.file, result.sha256);
  assert.equal(verified.execution_model, 'inherit_session');
  assert.equal(verified.language_status, 'CURRENT_POLICY_VALIDATED');
  assert.match(verified.limitations, /do not prove quality/);
  await assert.rejects(f.sealIt(), /EEXIST/);
  await assert.rejects(verify(result.file), /independently accepted/);
});
test('default English contract rejects Korean prose, while an explicit override is bound', async t => {
  const f = await fixture(t);
  const korean = '한국어 프롬프트 설명.\n';
  await fs.writeFile(path.join(f.root, 'prompt.txt'), korean);
  await f.write({ ...f.message, content: [{ type: 'text', text: korean }] });
  await assert.rejects(f.sealIt(), /non-Latin/);
  const override = { ...context, prompt_language_override: { language: 'ko-KR', user_instruction: '한국어 프롬프트를 작성해 주세요.', reason: 'Korean provider prompt required by project.' } };
  const req = await request({ stage: 'image_prompt', context: override, root: f.root, prompt: 'prompt.txt', out: 'override-request.json' });
  await f.write({ ...f.message, timestamp: req.created_at + 1, content: [{ type: 'text', text: korean }] });
  const receipt = await seal({ request: req.file, evidence: f.evidence, out: 'override-receipt.json' });
  assert.equal((await verify(receipt.file, receipt.sha256)).language_contract.language, 'ko-KR');
});
test('explicit final prompt SHA256 and fenced prompt are accepted', async t => {
  const f = await fixture(t);
  await f.write({ ...f.message, content: [{ type: 'text', text: `Prompt-SHA256: ${sha256(finalPrompt)}` }], sessionId: 'author-session', taskId: 'author-task' });
  const r = await f.sealIt();
  assert.equal(r.author_record.binding, 'explicit_prompt_sha256');
  assert.equal(r.session_id, 'author-session');
  assert.equal((await verify(r.file, r.sha256)).state, 'READY_FOR_EXECUTION');
  await f.write({ ...f.message, content: [{ type: 'text', text: `\`\`\`text\n${finalPrompt}\n\`\`\`` }] });
  assert.equal((await f.sealIt('receipt2.json')).author_record.binding, 'exact_final_prompt');
});
for (const [name, change] of [
  ['wrong model', m => ({ ...m, model: 'gpt-6-luna' })],
  ['user task echo', m => ({ ...m, role: 'user' })],
  ['tool result echo', m => ({ ...m, role: 'toolResult' })],
  ['tool call arguments without generated text', m => ({ ...m, stopReason: 'toolUse', content: [{ type: 'toolCall', name: 'write', arguments: { text: finalPrompt } }] })],
  ['unrelated transcript', m => ({ ...m, content: [{ type: 'text', text: 'Some other unrelated prompt.' }] })],
  ['assistant task quotation', m => ({ ...m, content: [{ type: 'text', text: `Please write this prompt: ${finalPrompt}` }] })],
  ['self-declared bare model JSON', () => ({ model: 'gpt-6-astra', prompt: finalPrompt })],
  ['missing generation response ID', m => ({ ...m, responseId: undefined })],
  ['missing generation usage', m => ({ ...m, usage: {} })],
  ['thinking-only content', m => ({ ...m, content: [{ type: 'thinking', text: finalPrompt }] })],
  ['incorrect hash', m => ({ ...m, content: [{ type: 'text', text: `Prompt-SHA256: ${'0'.repeat(64)}` }] })],
]) test(`seal rejects ${name}`, async t => {
  const f = await fixture(t);
  await f.write(change(f.message));
  await assert.rejects(f.sealIt(), /No post-request Astra assistant generation/);
});
test('evidence strictly after request timestamp, not before or equal', async t => {
  const f = await fixture(t);
  for (const timestamp of [f.req.created_at - 1, f.req.created_at]) {
    await f.write({ ...f.message, timestamp });
    await assert.rejects(f.sealIt(), /No post-request/);
  }
});
test('schema1 historical receipt remains verifiable but cannot be freshly sealed', async t => {
  const f = await fixture(t), current = await f.sealIt();
  const reqHash = await replaceJson(f.req.file, x => { x.schema_version = 1; delete x.language_contract; delete x.knowledge; });
  const receiptHash = await replaceJson(current.file, x => { x.schema_version = 1; delete x.language_contract; delete x.knowledge_sha256; delete x.author_record.knowledge_sha256; x.request_sha256 = reqHash; });
  const checked = await verify(current.file, receiptHash);
  assert.equal(checked.language_status, 'LEGACY_UNSPECIFIED_READ_ONLY');
  await assert.rejects(seal({ request: f.req.file, evidence: f.evidence, out: 'new-receipt.json' }), /LEGACY_UNSCOPED_REQUEST_READ_ONLY/);
});
test('receipt byte mutation fails independently accepted hash', async t => {
  const f = await fixture(t), r = await f.sealIt();
  await replaceJson(r.file, x => { x.stage = 'music_prompt'; });
  await assert.rejects(verify(r.file, r.sha256), /Receipt hash mismatch/);
});
test('receipt model mutation fails even with newly supplied hash', async t => {
  const f = await fixture(t), r = await f.sealIt();
  const h = await replaceJson(r.file, x => { x.required_model = 'gpt-6-luna'; });
  await assert.rejects(verify(r.file, h), /Invalid receipt/);
});
test('receipt language contract tampering fails its request binding', async t => {
  const f = await fixture(t), r = await f.sealIt();
  const h = await replaceJson(r.file, x => { x.language_contract.language = 'ko-KR'; x.language_contract.override_reason = 'tampered'; });
  await assert.rejects(verify(r.file, h), /Language contract binding mismatch/);
});
test('request mutation fails hash binding', async t => {
  const f = await fixture(t), r = await f.sealIt();
  await replaceJson(f.req.file, x => { x.session_id = 'changed'; });
  await assert.rejects(verify(r.file, r.sha256), /Request hash/);
});
test('prompt mutation fails hash binding', async t => {
  const f = await fixture(t), r = await f.sealIt();
  await fs.writeFile(path.join(f.root, 'prompt.txt'), 'Different prompt');
  await assert.rejects(verify(r.file, r.sha256), /Prompt hash mismatch/);
});
test('external transcript append is allowed but selected record mutation is rejected', async t => {
  const f = await fixture(t), r = await f.sealIt();
  assert.ok(!f.evidence.startsWith(f.root + path.sep));
  assert.equal(await fs.realpath(f.evidence), f.evidence);
  await fs.appendFile(f.evidence, JSON.stringify({ ...f.message, responseId: 'later-record' }) + '\n');
  assert.equal((await verify(r.file, r.receipt_sha256)).author_record.response_id, f.message.responseId);
  await f.write({ ...f.message, responseId: 'mutated-original' });
  await assert.rejects(verify(r.file, r.receipt_sha256), /Original evidence record changed/);
});
test('immutable evidence snapshot mutations fail hash binding', async t => {
  const f = await fixture(t), r = await f.sealIt();
  const snapshot = path.join(f.root, r.evidence.path);
  await replaceJson(snapshot, x => { x.raw_record += ' '; });
  await assert.rejects(verify(r.file, r.receipt_sha256), /Evidence snapshot hash mismatch/);
});
test('author record mutation fails revalidated binding', async t => {
  const f = await fixture(t), r = await f.sealIt();
  const h = await replaceJson(r.file, x => { x.author_record.response_id = 'unrelated'; });
  await assert.rejects(verify(r.file, h), /Author record binding/);
});
test('NFC and UTF-8 are mandatory', async t => {
  const f = await fixture(t);
  for (const bytes of ['e\u0301', Buffer.from([0xff]), '   ']) {
    await fs.writeFile(path.join(f.root, 'prompt.txt'), bytes);
    await assert.rejects(f.sealIt());
  }
});
test('evidence must be a messages.jsonl file not self-declared JSON', async t => {
  const f = await fixture(t);
  const wrong = path.join(f.root, 'evidence.json');
  await fs.copyFile(f.evidence, wrong);
  await assert.rejects(seal({ request: f.req.file, evidence: wrong, out: 'receipt.json' }), /messages.jsonl/);
  await fs.writeFile(f.evidence, '{broken json');
  await assert.rejects(f.sealIt(), /Malformed messages/);
});
test('root containment protects generated files and accepts external source evidence', async t => {
  const f = await fixture(t);
  const outside = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'aside-harness-outside-')));
  t.after(() => fs.rm(outside, { recursive: true, force: true }));
  await fs.writeFile(path.join(outside, 'prompt.txt'), finalPrompt);
  await fs.copyFile(f.evidence, path.join(outside, 'messages.jsonl'));
  await fs.symlink(outside, path.join(f.root, 'escape'));
  for (const prompt of ['../prompt.txt', path.join(outside, 'prompt.txt'), 'escape/prompt.txt']) {
    await assert.rejects(request({ stage: 'image_prompt', context, root: f.root, prompt, out: 'unsafe.json' }), /relative path|escapes root/);
  }
  for (const out of ['../receipt.json', path.join(outside, 'receipt.json'), 'escape/receipt.json']) {
    await assert.rejects(seal({ request: f.req.file, evidence: f.evidence, out }), /relative path|escapes root/);
  }
  const external = await seal({ request: f.req.file, evidence: path.join(outside, 'messages.jsonl'), out: 'external-receipt.json' });
  assert.equal((await verify(external.file, external.receipt_sha256)).state, 'READY_FOR_EXECUTION');
  const r = await f.sealIt();
  await fs.unlink(path.join(f.root, 'prompt.txt'));
  await fs.symlink(path.join(outside, 'prompt.txt'), path.join(f.root, 'prompt.txt'));
  await assert.rejects(verify(r.file, r.sha256), /escapes root/);
});
test('CLI rejects missing or unsupported options before loading policy', async () => {
  await assert.rejects(main(['route', 'image_prompt']), /Missing --context/);
  await assert.rejects(main(['status', '--model', 'gpt-6-luna']), /Invalid option/);
  await assert.rejects(main(['bogus']), /Usage/);
});


test('ongoing toolUse commentary generated text binds exact hash or prompt, not arguments', async t => {
  const f = await fixture(t);
  for (const [i, text] of [finalPrompt, 'Prompt-SHA256: ' + sha256(finalPrompt)].entries()) {
    await f.write({ ...f.message, stopReason: 'toolUse', content: [
      { type: 'text', text, channel: 'commentary' },
      { type: 'toolCall', name: 'inspect', arguments: { prompt: 'unrelated' } },
    ] });
    const r = await f.sealIt('ongoing-' + i + '.json');
    assert.equal((await verify(r.file, r.receipt_sha256)).state, 'READY_FOR_EXECUTION');
  }
});
test('request permits missing prompt and later seal requires the newly created file', async t => {
  const f = await fixture(t);
  const req = await request({ stage: 'music_prompt', context, root: f.root, prompt: 'new-prompt.txt', out: 'new-request.json' });
  assert.equal(req.initial_prompt_sha256, null);
  assert.equal(req.file_sha256, sha256(await fs.readFile(req.file)));
  await assert.rejects(seal({ request: req.file, evidence: f.evidence, out: 'new-receipt.json' }), /ENOENT/);
  await fs.writeFile(path.join(f.root, 'new-prompt.txt'), finalPrompt);
  await f.write({ ...f.message, timestamp: req.created_at + 1 });
  const r = await seal({ request: req.file, evidence: f.evidence, out: 'new-receipt.json' });
  assert.deepEqual(r.prompt, { path: 'new-prompt.txt', sha256: sha256(finalPrompt) });
  assert.equal((await verify(r.file, r.receipt_sha256)).state, 'READY_FOR_EXECUTION');
});
test('CLI accepts context JSON file paths and literals', async t => {
  const f = await fixture(t);
  const file = path.join(f.root, 'context.json');
  await fs.writeFile(file, JSON.stringify(context));
  assert.equal((await main(['route', 'image_prompt', '--context', file])).mode, 'direct');
  assert.equal((await main(['route', 'image_prompt', '--context', JSON.stringify(context)])).mode, 'direct');
  const r = await main(['request', 'image_prompt', '--context', file, '--root', f.root, '--prompt', 'cli-prompt.txt', '--out', 'cli-request.json']);
  assert.equal(r.initial_prompt_sha256, null);
  assert.equal(r.file_sha256, sha256(await fs.readFile(r.file)));
});
test('snapshot source binds the exact original line, even when not the first record', async t => {
  const f = await fixture(t);
  await fs.writeFile(f.evidence, JSON.stringify({ role: 'user', content: 'task' }) + '\n' + JSON.stringify(f.message) + '\n');
  const r = await f.sealIt();
  assert.equal(r.evidence.source.line, 2);
  assert.equal((await verify(r.file, r.receipt_sha256)).author_record.line, 2);
  await fs.writeFile(f.evidence, JSON.stringify(f.message) + '\n');
  await assert.rejects(verify(r.file, r.receipt_sha256), /Original evidence record changed or missing/);
});

// Knowledge acknowledgement is fixture metadata, not an assertion of semantic quality.
test('new image request embeds bounded current knowledge, sealed to actual generated acknowledgement', async t => {
  const f = await fixture(t); assert.ok(f.req.knowledge.text.length <= 9000);
  assert.ok(f.req.knowledge.selected_ids.length <= 6); assert.match(f.req.author_task, /Knowledge-SHA256:/);
  const r=await f.sealIt(); const v=await verify(r.file,r.sha256);
  assert.equal(v.knowledge_status,'CURRENT_KNOWLEDGE_VALIDATED');assert.equal(v.knowledge_sha256,f.req.knowledge.sha256);
});
test('missing or wrong generated knowledge acknowledgement cannot seal', async t => {
  const f=await fixture(t);
  for(const text of [finalPrompt, finalPrompt+'\nKnowledge-SHA256: '+'0'.repeat(64)]) {
    await fs.writeFile(f.evidence,JSON.stringify({...f.message,content:[{type:'text',text}]})+'\n');
    await assert.rejects(f.sealIt(),/No post-request Astra/);
  }
});
test('tampered request knowledge fails even before newly accepted receipt hashing', async t => {
  const f=await fixture(t);await replaceJson(f.req.file,x=>{x.knowledge.text+=' unwanted rule';});
  await assert.rejects(f.sealIt(),/knowledge|Knowledge|hash|Hash|packet|Packet/);
});
test('knowledge receipt digest cannot differ from the request', async t => {
  const f=await fixture(t),r=await f.sealIt();const h=await replaceJson(r.file,x=>{x.knowledge_sha256='0'.repeat(64);});
  await assert.rejects(verify(r.file,h),/Knowledge receipt.*request/);
});
test('schema2 language-only historical receipt is read-only for new authorship', async t => {
  const f=await fixture(t),r=await f.sealIt();
  const h=await replaceJson(f.req.file,x=>{delete x.knowledge;});
  const receiptHash=await replaceJson(r.file,x=>{delete x.knowledge_sha256;delete x.author_record.knowledge_sha256;x.request_sha256=h;});
  assert.equal((await verify(r.file,receiptHash)).knowledge_status,'LEGACY_KNOWLEDGE_UNSPECIFIED_READ_ONLY');
  await assert.rejects(seal({request:f.req.file,evidence:f.evidence,out:'new.json'}),/LEGACY_KNOWLEDGE_UNSPECIFIED_READ_ONLY/);
});

test('altered author_task cannot deliver a different source body than the bound packet',async t=>{const f=await fixture(t);await replaceJson(f.req.file,x=>{x.author_task='Use an unrelated old rule.';});await assert.rejects(f.sealIt(),/Author task knowledge/);});
