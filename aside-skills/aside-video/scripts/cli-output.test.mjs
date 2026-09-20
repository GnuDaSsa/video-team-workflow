// Synthetic file/provenance fixtures, never evidence of actual model/provider execution.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import * as harness from './harness.mjs';
import * as submission from './submission.mjs';

const scripts = path.dirname(fileURLToPath(import.meta.url));
const context = { model: { modelId: 'other' }, modelCategories: { deep: { modelId: 'gpt-6-astra', provider: 'synthetic' } }, user_instruction: 'Create a portrait image prompt.', session_id: 'SYNTHETIC-requester', task_id: 'SYNTHETIC-task' };
const prompt = 'Synthetic portrait fixture, warm natural light and a clear background.\n'.repeat(60);
async function fixture(t) {
  const root = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'aside-cli-output-')));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const env = { ...process.env, ASIDE_VIDEO_WIKI_ROOT: path.join(root, 'absent-wiki') };
  const old = process.env.ASIDE_VIDEO_WIKI_ROOT;
  process.env.ASIDE_VIDEO_WIKI_ROOT = env.ASIDE_VIDEO_WIKI_ROOT;
  t.after(() => { if (old === undefined) delete process.env.ASIDE_VIDEO_WIKI_ROOT; else process.env.ASIDE_VIDEO_WIKI_ROOT = old; });
  const run = (script, args, ok = true) => {
    const result = spawnSync(process.execPath, [path.join(scripts, script + '.mjs'), ...args], { env, encoding: 'utf8', timeout: 30000 });
    assert.ifError(result.error);
    if (ok) assert.equal(result.status, 0, result.stderr);
    else { assert.notEqual(result.status, 0); assert.equal(result.stdout, ''); }
    return { ...result, value: ok ? JSON.parse(result.stdout) : undefined };
  };
  const requestArgs = (out = 'request.json') => ['request', 'image_prompt', '--context', JSON.stringify(context), '--root', root, '--prompt', 'prompt.txt', '--out', out];
  return { root, run, requestArgs };
}
const read = async file => JSON.parse(await fs.readFile(file, 'utf8'));
async function fileHashes(root) {
  return Object.fromEntries(await Promise.all((await fs.readdir(root)).sort().map(async name => [name, harness.sha256(await fs.readFile(path.join(root, name)))])));
}
async function writeEvidence(f, req) {
  await fs.writeFile(path.join(f.root, 'prompt.txt'), prompt);
  const evidence = path.join(f.root, 'messages.jsonl');
  await fs.writeFile(evidence, JSON.stringify({ role: 'assistant', model: 'gpt-6-astra', provider: 'SYNTHETIC-provider', api: 'SYNTHETIC-api', responseId: 'SYNTHETIC-response', session_id: 'SYNTHETIC-author', task_id: 'SYNTHETIC-author-task', usage: { input: 1, output: 1 }, timestamp: req.created_at + 1, stopReason: 'stop', content: [{ type: 'text', text: `Prompt-SHA256: ${harness.sha256(prompt)}\nKnowledge-SHA256: ${req.knowledge.sha256}` }] }) + '\n');
  return evidence;
}
function measurements(t, name, compact, full) {
  const a = Buffer.byteLength(compact.stdout), b = Buffer.byteLength(full.stdout);
  assert.ok(a < b, `${name}: expected stdout reduction`);
  t.diagnostic(`${name}: default=${a} bytes; full=${b} bytes; reduction=${((1 - a / b) * 100).toFixed(1)}%`);
}
function knowledgeSummary(result, req) {
  assert.equal(result.knowledge_status, 'CURRENT_KNOWLEDGE_VALIDATED');
  assert.equal(result.knowledge_sha256, req.knowledge.sha256);
  assert.deepEqual(result.knowledge, { selected_ids: req.knowledge.selected_ids, source_mode: 'reviewed_snapshot' });
  assert.equal(result.route.mode, 'functions.subagent');
  assert.equal(result.route.category, 'deep');
  assert.equal(result.route.required_model, 'gpt-6-astra');
}

test('real CLI summaries, explicit full output, byte hashes and unchanged JS results', async t => {
  const f = await fixture(t);
  const requested = f.run('harness', f.requestArgs());
  const req = await read(requested.value.file);
  assert.equal(requested.value.sha256, harness.sha256(await fs.readFile(requested.value.file)));
  assert.equal(requested.value.file_sha256, requested.value.sha256);
  assert.equal(requested.value.author_task, undefined);
  assert.equal(requested.value.author_model, null);
  assert.equal(requested.value.language_status, 'PENDING_PROMPT_VALIDATION');
  knowledgeSummary(requested.value, req);
  const handoff = f.run('harness', ['author-task', requested.value.file]);
  assert.deepEqual(handoff.value, { stage: req.stage, prompt_file: path.join(f.root, 'prompt.txt'), author_task: req.author_task });
  await assert.rejects(fs.stat(handoff.value.prompt_file), { code: 'ENOENT' });
  const emptyBefore = await fileHashes(f.root);
  f.run('harness', ['seal', '--request', requested.value.file, '--evidence', path.join(f.root, 'messages.jsonl'), '--out', 'premature-receipt.json'], false);
  assert.deepEqual(await fileHashes(f.root), emptyBefore);
  const fullRequest = f.run('harness', [...f.requestArgs('full-request.json'), '--full']);
  const onDisk = await read(fullRequest.value.file);
  assert.deepEqual(fullRequest.value, { ...onDisk, file: fullRequest.value.file, file_sha256: fullRequest.value.sha256, sha256: fullRequest.value.sha256 });
  assert.equal(fullRequest.value.sha256, harness.sha256(await fs.readFile(fullRequest.value.file)));
  measurements(t, 'request', requested, fullRequest);
  const jsRequest = await harness.main([...f.requestArgs('js-request.json'), '--full']);
  assert.equal(jsRequest.author_task, req.author_task);
  assert.deepEqual(jsRequest.knowledge, req.knowledge);
  const evidence = await writeEvidence(f, req);
  const sealArgs = out => ['seal', '--request', requested.value.file, '--evidence', evidence, '--out', out];
  const sealed = f.run('harness', sealArgs('receipt.json'));
  const fullSealed = f.run('harness', [...sealArgs('full-receipt.json'), '--full']);
  const receipt = await read(sealed.value.file);
  assert.equal(sealed.value.receipt_sha256, harness.sha256(await fs.readFile(sealed.value.file)));
  assert.equal(sealed.value.sha256, sealed.value.receipt_sha256);
  assert.equal(sealed.value.author_model, 'gpt-6-astra');
  assert.deepEqual(sealed.value.author_record, receipt.author_record);
  knowledgeSummary(sealed.value, req);
  assert.deepEqual(fullSealed.value.author_record, receipt.author_record);
  const jsSeal = await harness.main(sealArgs('js-receipt.json'));
  assert.equal(jsSeal.kind, 'astra_author_receipt');
  assert.deepEqual(jsSeal.author_record, receipt.author_record);
  const verifyArgs = ['verify', sealed.value.file, '--sha256', sealed.value.receipt_sha256];
  const verified = f.run('harness', verifyArgs);
  const fullVerified = f.run('harness', [...verifyArgs, '--full']);
  assert.deepEqual(fullVerified.value, await harness.verify(sealed.value.file, sealed.value.receipt_sha256));
  assert.deepEqual(fullVerified.value, await harness.main(verifyArgs));
  assert.equal(verified.value.language_status, fullVerified.value.language_status);
  const prepareArgs = out => ['prepare', '--stage', 'image_prompt', '--receipt', sealed.value.file, '--sha256', sealed.value.receipt_sha256, '--out', path.join(f.root, out)];
  const prepared = f.run('submission', prepareArgs('payload.json'));
  const fullPrepared = f.run('submission', [...prepareArgs('full-payload.json'), '--full']);
  assert.equal(fullPrepared.value.payload_sha256, harness.sha256(await fs.readFile(fullPrepared.value.file)));
  assert.equal(prepared.value.payload_sha256, harness.sha256(await fs.readFile(prepared.value.file)));
  const payload = await read(prepared.value.file);
  assert.equal(payload.prompt, prompt);
  assert.equal(payload.prompt_sha256, harness.sha256(prompt));
  const payloadArgs = ['verify', prepared.value.file, '--sha256', prepared.value.payload_sha256];
  const before = await fileHashes(f.root);
  const payloadCheck = f.run('submission', payloadArgs);
  const fullPayloadCheck = f.run('submission', [...payloadArgs, '--full']);
  assert.deepEqual(fullPayloadCheck.value, await submission.verify(prepared.value.file, prepared.value.payload_sha256));
  assert.deepEqual(fullPayloadCheck.value, await submission.main(payloadArgs));
  assert.deepEqual(fullPayloadCheck.value, await submission.main([...payloadArgs, '--full']));
  assert.deepEqual(await fileHashes(f.root), before);
  assert.equal(payloadCheck.value.payload, undefined);
  assert.equal(payloadCheck.value.prompt.bytes, Buffer.byteLength(prompt));
  assert.equal(payloadCheck.value.prompt.sha256, payload.prompt_sha256);
  assert.deepEqual(payloadCheck.value.author_record, payload.author_record);
  assert.equal(payloadCheck.value.author_session_id, payload.author_session_id);
  assert.equal(payloadCheck.value.author_model, 'gpt-6-astra');
  knowledgeSummary(payloadCheck.value, req);
  // check.mjs's existing consumer contract: status stdout, then independent file read.
  assert.equal(payloadCheck.value.language_status, 'CURRENT_POLICY_VALIDATED');
  assert.equal(payloadCheck.value.knowledge_status, 'CURRENT_KNOWLEDGE_VALIDATED');
  assert.equal((await read(payloadCheck.value.file)).prompt, prompt);
  measurements(t, 'submission verify', payloadCheck, fullPayloadCheck);
});

test('malformed/repeated options are rejected before request, evidence or payload writes', async t => {
  const f = await fixture(t);
  const requested = f.run('harness', f.requestArgs());
  const req = await read(requested.value.file);
  const evidence = await writeEvidence(f, req);
  const receipt = await harness.seal({ request: requested.value.file, evidence, out: 'receipt.json' });
  const cases = [
    ['harness', f.requestArgs('must-not-write-request.json')],
    ['harness', ['seal', '--request', requested.value.file, '--evidence', evidence, '--out', 'must-not-write-receipt.json']],
    ['submission', ['prepare', '--stage', 'image_prompt', '--receipt', receipt.file, '--sha256', receipt.receipt_sha256, '--out', path.join(f.root, 'must-not-write-payload.json')]],
  ];
  const before = await fileHashes(f.root);
  for (const [script, args] of cases) {
    for (const malformed of [['--full', '--full'], ['--full=true'], ['--full', 'true'], ['--full', '--unknown'], ['-full'], ['--out', '--full']]) f.run(script, [...args, ...malformed], false);
    await assert.rejects((script === 'harness' ? harness : submission).main([...args, '--full', '--full']));
    assert.deepEqual(await fileHashes(f.root), before);
  }
  f.run('harness', ['toString'], false);
});

test('author-task validates current knowledge, route, root containment and legacy read-only', async t => {
  const f = await fixture(t);
  const requested = f.run('harness', f.requestArgs());
  const original = await read(requested.value.file);
  await fs.chmod(requested.value.file, 0o600);
  for (const mutate of [r => { r.schema_version = 1; }, r => { r.knowledge = null; }, r => { r.knowledge.text += 'tamper'; }, r => { r.author_task += 'tamper'; }, r => { r.route.planned_model.modelId = 'other'; }, r => { r.prompt = '../escape.txt'; }]) {
    const r = structuredClone(original); mutate(r);
    await fs.writeFile(requested.value.file, JSON.stringify(r));
    f.run('harness', ['author-task', requested.value.file], false);
  }
  await fs.writeFile(requested.value.file, JSON.stringify(original));
  await fs.symlink(path.join(f.root, '..', 'absent-outside-prompt'), path.join(f.root, 'prompt.txt'));
  f.run('harness', ['author-task', requested.value.file], false);
  await fs.unlink(path.join(f.root, 'prompt.txt'));
  const before = await fileHashes(f.root);
  f.run('harness', ['author-task', requested.value.file, '--full', '--full'], false);
  assert.deepEqual(await fileHashes(f.root), before);
  assert.deepEqual((await harness.main(['author-task', requested.value.file])), { stage: original.stage, prompt_file: path.join(f.root, 'prompt.txt'), author_task: original.author_task });
});

test('legacy CLI verify remains read-only with truthful statuses and full opt-in', async t => {
  const f = await fixture(t);
  const requested = f.run('harness', f.requestArgs());
  const req = await read(requested.value.file);
  const evidence = await writeEvidence(f, req);
  const receipt = await harness.seal({ request: requested.value.file, evidence, out: 'receipt.json' });
  const prepared = await submission.prepare({ stage: 'image_prompt', receipt: receipt.file, sha256: receipt.receipt_sha256, out: path.join(f.root, 'payload.json') });
  const rewrite = async (file, mutate) => {
    const value = await read(file); mutate(value);
    await fs.chmod(file, 0o600);
    const raw = JSON.stringify(value);
    await fs.writeFile(file, raw);
    return harness.sha256(raw);
  };
  const requestHash = await rewrite(requested.value.file, r => { r.schema_version = 1; delete r.language_contract; delete r.knowledge; });
  const receiptHash = await rewrite(receipt.file, r => { r.schema_version = 1; delete r.language_contract; delete r.knowledge_sha256; delete r.author_record.knowledge_sha256; r.request_sha256 = requestHash; });
  const payloadHash = await rewrite(prepared.file, p => { p.schema_version = 1; delete p.language_contract; delete p.knowledge_sha256; delete p.author_record.knowledge_sha256; p.receipt.sha256 = receiptHash; });
  const before = await fileHashes(f.root);
  for (const [script, file, hash] of [['harness', receipt.file, receiptHash], ['submission', prepared.file, payloadHash]]) {
    const args = ['verify', file, '--sha256', hash];
    const compact = f.run(script, args).value;
    const full = f.run(script, [...args, '--full']).value;
    assert.equal(compact.language_status, 'LEGACY_UNSPECIFIED_READ_ONLY');
    assert.equal(compact.knowledge_status, 'LEGACY_KNOWLEDGE_UNSPECIFIED_READ_ONLY');
    assert.equal(compact.knowledge_sha256, null);
    assert.deepEqual(full, JSON.parse(JSON.stringify(await (script === 'harness' ? harness : submission).main(args))));
  }
  f.run('harness', ['author-task', requested.value.file], false);
  f.run('harness', ['seal', '--request', requested.value.file, '--evidence', evidence, '--out', 'fresh-receipt.json'], false);
  f.run('submission', ['prepare', '--stage', 'image_prompt', '--receipt', receipt.file, '--sha256', receiptHash, '--out', path.join(f.root, 'fresh-payload.json')], false);
  assert.deepEqual(await fileHashes(f.root), before);
});
