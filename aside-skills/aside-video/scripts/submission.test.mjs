// Synthetic, isolated file-binding tests only. These fixtures are NOT evidence
// of actual Astra authorship, real provider execution, or production quality.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { request, seal, sha256 } from './harness.mjs';
import { prepare, verify, main, PROVIDERS } from './submission.mjs';

async function fixture(t, stage = 'image_prompt', prompt = 'Synthetic fixture only.\nComplete prompt text.\n  Keep whitespace.\n') {
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'aside-submission-unit-'));
  t.after(() => fs.rm(temporary, { recursive: true, force: true }));
  const root = await fs.realpath(temporary);
  const promptFile = path.join(root, 'prompt.txt');
  await fs.writeFile(promptFile, prompt, { mode: 0o600 });
  const requested = await request({ stage, root, prompt: 'prompt.txt', out: 'request.json', context: {
    model: { modelId: 'gpt-6-astra' }, user_instruction: 'Create the requested provider prompt.', session_id: 'SYNTHETIC-requester-not-production',
  } });
  const evidence = path.join(root, 'messages.jsonl');
  await fs.writeFile(evidence, JSON.stringify({
    role: 'assistant', model: 'gpt-6-astra', provider: 'synthetic-test-provider', api: 'synthetic-test-api',
    responseId: 'SYNTHETIC-response-not-production', session_id: 'SYNTHETIC-author-not-production',
    usage: { input: 1, output: 1 }, timestamp: requested.created_at + 1,
    stopReason: 'stop', content: [{ type: 'text', text: `Prompt-SHA256: ${sha256(Buffer.from(prompt))}` }],
  }) + '\n', { mode: 0o600 });
  const receipt = await seal({ request: requested.file, evidence, out: 'receipt.json' });
  const out = path.join(root, 'payload.json');
  const options = { stage, receipt: receipt.file, sha256: receipt.receipt_sha256, out };
  return { root, prompt, promptFile, evidence, receipt, out, options };
}
async function readJSON(file) { return JSON.parse(await fs.readFile(file, 'utf8')); }
async function rewrite(file, value) {
  await fs.chmod(file, 0o600);
  const raw = typeof value === 'string' ? value : JSON.stringify(value);
  await fs.writeFile(file, raw);
  return sha256(Buffer.from(raw));
}
async function referencesFixture(f) {
  const references = [];
  for (const [index, role] of ['identity-front', 'identity-back'].entries()) {
    const file = path.join(f.root, `reference-${index}.bin`);
    const content = Buffer.from([0, 255, index, 42]);
    await fs.writeFile(file, content, { mode: 0o600 });
    references.push({ path: file, sha256: sha256(content), role });
  }
  const file = path.join(f.root, 'references.json');
  await fs.writeFile(file, JSON.stringify(references), { mode: 0o600 });
  return { file, references };
}
for (const [stage, provider] of Object.entries(PROVIDERS)) {
  test(`${stage}: prepare/verify binds full prompt, actual fixture author record, receipt and fixed provider`, async t => {
    const f = await fixture(t, stage);
    const result = await main(['prepare', '--stage', stage, '--receipt', f.receipt.file, '--sha256', f.options.sha256, '--out', f.out]);
    const payload = await readJSON(f.out);
    assert.equal(payload.prompt, f.prompt);
    assert.equal(payload.prompt_sha256, sha256(Buffer.from(f.prompt)));
    assert.equal(payload.stage, stage);
    assert.equal(payload.provider, provider);
    assert.equal(payload.required_author, 'gpt-6-astra');
    assert.equal(payload.author_session_id, 'SYNTHETIC-author-not-production');
    assert.deepEqual(payload.author_record, f.receipt.author_record);
    assert.equal(payload.author_record.response_id, 'SYNTHETIC-response-not-production');
    assert.deepEqual(payload.receipt, { path: f.receipt.file, sha256: f.options.sha256 });
    assert.deepEqual(payload.references, []);
    assert.equal(payload.state, 'READY_FOR_PROVIDER_INPUT');
    assert.equal(new Date(payload.created_at).toISOString(), payload.created_at);
    assert.equal((await fs.stat(f.out)).mode & 0o777, 0o600);
    assert.equal(result.payload_sha256, sha256(await fs.readFile(f.out)));
    const checked = await main(['verify', f.out, '--sha256', result.payload_sha256]);
    assert.deepEqual(checked.payload, payload);
    assert.equal(checked.state, 'READY_FOR_PROVIDER_INPUT');
  });
}
test('preserves BOM, multiline text, trailing newline and Unicode as exact UTF-8 bytes', async t => {
  const f = await fixture(t, 'image_prompt', '\uFEFFRésumé\nSynthetic fixture\r\n  final\n');
  const result = await prepare(f.options);
  assert.equal((await verify(f.out, result.payload_sha256)).payload.prompt, f.prompt);
});
test('requires independently accepted receipt and payload hashes', async t => {
  const f = await fixture(t);
  for (const accepted of [undefined, '', 'invalid', '0'.repeat(64)]) {
    await assert.rejects(prepare({ ...f.options, sha256: accepted }));
  }
  const result = await prepare(f.options);
  for (const accepted of [undefined, '', result.payload_sha256.toUpperCase(), f.options.sha256, '0'.repeat(64)]) {
    await assert.rejects(verify(f.out, accepted));
  }
});
test('rejects wrong receipt stage, unknown stage and output relative path', async t => {
  const f = await fixture(t);
  await assert.rejects(prepare({ ...f.options, stage: 'music_prompt' }), /stage mismatch/);
  for (const stage of ['image_generate', 'toString', '__proto__', 'unknown']) {
    await assert.rejects(prepare({ ...f.options, stage }), /Unsupported author stage/);
  }
  await assert.rejects(prepare({ ...f.options, out: 'payload.json' }), /absolute/);
  await assert.rejects(prepare({ ...f.options, receipt: 'receipt.json' }), /absolute/);
  await assert.rejects(fs.stat(f.out), { code: 'ENOENT' });
});
test('wx never overwrites existing outputs or follows output symlinks', async t => {
  const f = await fixture(t);
  await prepare(f.options);
  const before = await fs.readFile(f.out);
  await assert.rejects(prepare(f.options), { code: 'EEXIST' });
  assert.deepEqual(await fs.readFile(f.out), before);
  const link = path.join(f.root, 'output-link.json');
  await fs.symlink(f.out, link);
  await assert.rejects(prepare({ ...f.options, out: link }), { code: 'EEXIST' });
  assert.deepEqual(await fs.readFile(f.out), before);
});
test('ordered reference bytes and roles are bound, with no universal minimum', async t => {
  const f = await fixture(t, 'seedance_prompt');
  const refs = await referencesFixture(f);
  const result = await prepare({ ...f.options, references: refs.file });
  assert.deepEqual((await verify(f.out, result.payload_sha256)).payload.references, refs.references);
  // The manifest is input only: payload entries are self-contained.
  await fs.unlink(refs.file);
  await verify(f.out, result.payload_sha256);
});
test('reference reordering and role changes fail the accepted payload hash', async t => {
  const f = await fixture(t);
  const refs = await referencesFixture(f);
  const result = await prepare({ ...f.options, references: refs.file });
  const original = await fs.readFile(f.out, 'utf8');
  const reordered = JSON.parse(original);
  reordered.references.reverse();
  await rewrite(f.out, reordered);
  await assert.rejects(verify(f.out, result.payload_sha256), /Payload hash mismatch/);
  const roleChanged = JSON.parse(original);
  roleChanged.references[0].role = 'different-role';
  await rewrite(f.out, roleChanged);
  await assert.rejects(verify(f.out, result.payload_sha256), /Payload hash mismatch/);
});
for (const change of ['changed', 'missing']) {
  test(`${change} reference bytes are rejected`, async t => {
    const f = await fixture(t);
    const refs = await referencesFixture(f);
    const result = await prepare({ ...f.options, references: refs.file });
    if (change === 'changed') await fs.writeFile(refs.references[0].path, 'changed bytes');
    else await fs.unlink(refs.references[0].path);
    await assert.rejects(verify(f.out, result.payload_sha256));
    await assert.rejects(prepare({ ...f.options, out: path.join(f.root, 'another.json'), references: refs.file }));
  });
}
test('malformed reference manifests, roles, hashes and paths are rejected before output', async t => {
  const f = await fixture(t);
  const refs = await referencesFixture(f);
  const good = refs.references[0];
  for (const malformed of [{}, [null], [{ ...good, path: 'relative.png' }], [{ ...good, sha256: '0'.repeat(64) }], [{ ...good, role: '' }], [{ ...good, role: 1 }], [{ ...good, extra: true }], [{ path: good.path, sha256: good.sha256 }]]) {
    await rewrite(refs.file, malformed);
    await assert.rejects(prepare({ ...f.options, references: refs.file }));
    await assert.rejects(fs.stat(f.out), { code: 'ENOENT' });
  }
});
for (const target of ['receipt', 'prompt', 'request', 'snapshot', 'evidence']) {
  for (const change of ['changed', 'missing']) {
    test(`${change} ${target} invalidates prepared payload`, async t => {
      const f = await fixture(t);
      const result = await prepare(f.options);
      const filename = { receipt: f.receipt.file, prompt: f.promptFile, request: path.join(f.root, f.receipt.request), snapshot: path.join(f.root, f.receipt.evidence.path), evidence: f.evidence }[target];
      if (change === 'missing') await fs.unlink(filename);
      else await rewrite(filename, 'tampered fixture');
      await assert.rejects(verify(f.out, result.payload_sha256));
    });
  }
}
test('rejects changed or missing payload metadata even with a newly supplied hash when invariant is invalid', async t => {
  const f = await fixture(t);
  const result = await prepare(f.options);
  const original = await readJSON(f.out);
  const mutations = [
    p => { p.provider = 'imagegen'; }, p => { p.provider = 'grok'; },
    p => { p.stage = 'music_prompt'; p.provider = 'suno_web'; },
    p => { p.required_author = 'luna'; }, p => { p.state = 'GENERATED'; },
    p => { p.prompt = p.prompt.trim(); }, p => { p.prompt_sha256 = '0'.repeat(64); },
    p => { p.language_contract.language = 'ko-KR'; },
    p => { p.author_session_id = 'SYNTHETIC-other'; },
    p => { p.author_record.response_id = 'SYNTHETIC-other'; },
    p => { p.author_record.model = 'luna'; },
    p => { p.receipt.sha256 = '0'.repeat(64); },
    p => { p.receipt.path = 'relative.json'; },
    p => { p.created_at = 'invalid'; }, p => { p.schema_version = 1; },
    p => { p.kind = 'generated'; }, p => { p.references = null; },
    p => { p.extra = 'unbound'; }, p => { delete p.author_record; },
    p => { delete p.created_at; }, p => { delete p.receipt; },
  ];
  for (const mutate of mutations) {
    const changed = structuredClone(original);
    mutate(changed);
    const newlyAccepted = await rewrite(f.out, changed);
    await assert.rejects(verify(f.out, result.payload_sha256), /Payload hash mismatch/);
    await assert.rejects(verify(f.out, newlyAccepted));
  }
});
test('valid-looking metadata edits still fail original independent payload acceptance', async t => {
  const f = await fixture(t);
  const result = await prepare(f.options);
  const payload = await readJSON(f.out);
  payload.created_at = new Date(Date.parse(payload.created_at) + 1000).toISOString();
  await rewrite(f.out, payload);
  await assert.rejects(verify(f.out, result.payload_sha256), /Payload hash mismatch/);
});
test('appending later evidence messages does not invalidate the original bound record', async t => {
  const f = await fixture(t);
  const result = await prepare(f.options);
  await fs.appendFile(f.evidence, JSON.stringify({ role: 'user', content: 'Synthetic later fixture message' }) + '\n');
  await verify(f.out, result.payload_sha256);
});
test('schema1 historical payload is read-only verifiable and cannot be freshly prepared', async t => {
  const f = await fixture(t), current = await prepare(f.options);
  const reqFile = path.join(f.root, f.receipt.request);
  const req = await readJSON(reqFile);
  req.schema_version = 1; delete req.language_contract;
  const reqHash = await rewrite(reqFile, req);
  const receipt = await readJSON(f.receipt.file);
  receipt.schema_version = 1; delete receipt.language_contract; receipt.request_sha256 = reqHash;
  const receiptHash = await rewrite(f.receipt.file, receipt);
  const payload = await readJSON(f.out);
  payload.schema_version = 1; delete payload.language_contract; payload.receipt.sha256 = receiptHash;
  const payloadHash = await rewrite(f.out, payload);
  assert.equal((await verify(f.out, payloadHash)).language_status, 'LEGACY_UNSPECIFIED_READ_ONLY');
  await assert.rejects(prepare({ ...f.options, out: path.join(f.root, 'fresh.json'), sha256: receiptHash }), /LEGACY_UNSPECIFIED_READ_ONLY/);
});
test('CLI rejects missing independent hash, duplicate/unknown options, fallback and extra arguments', async t => {
  const f = await fixture(t);
  for (const args of [[], ['generate'], ['verify', f.out], ['verify', f.out, '--sha256'], ['verify', f.out, '--sha256', f.options.sha256, '--sha256', f.options.sha256], ['verify', f.out, '--sha256', f.options.sha256, '--provider', 'chatgpt_web'], ['prepare', '--stage', 'image_prompt'], ['prepare', '--fallback', 'imagegen'], ['verify', f.out, 'extra', '--sha256', f.options.sha256]]) {
    await assert.rejects(main(args));
  }
});

test('reference manifest may be relative while every bound entry remains absolute', async t => {
  const f = await fixture(t);
  const refs = await referencesFixture(f);
  const result = await main(['prepare', '--stage', f.options.stage, '--receipt', f.options.receipt,
    '--sha256', f.options.sha256, '--out', f.out, '--references', path.relative(process.cwd(), refs.file)]);
  assert.deepEqual((await verify(f.out, result.payload_sha256)).payload.references, refs.references);
});
