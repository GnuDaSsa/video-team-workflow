import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { EventEmitter } from 'node:events';
import { main, buildRequest, validateInput, validateResponse, status, MODEL, ISSUES, DEFAULT_KEY_FILE } from './jev-seedance.mjs';
import { createTransport, MAX_RESPONSE_BYTES } from './jev-qc.mjs';

// Synthetic credentials only. All transports are mocked; never use the default transport.
const scratch = process.env.JEV_QC_TEST_TMP;
if (!scratch) throw new Error('Set JEV_QC_TEST_TMP to an existing scratch directory');
const secret = 'SYNTHETIC-KEY-NOT-A-CREDENTIAL';
const notice = 'SYNTHETIC-PRIVATE-NOTICE: selected references could not be confirmed';
const good = () => ({ model: MODEL, answers: { issue: { type: 'choice', choice: 'SELECTION_REVIEW', confidence: 0.91,
  probabilities: Object.fromEntries(ISSUES.map(i => [i, i === 'SELECTION_REVIEW' ? 1 : 0])) } }, usage: { input_tokens: 20, output_tokens: 3 } });
function fixture(t) {
  const root = fs.mkdtempSync(path.join(fs.realpathSync(scratch), 'jev-seedance-test-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const input = path.join(root, 'input.json'), dir = path.join(root, '.jev-seedance');
  fs.writeFileSync(input, JSON.stringify({ notice }));
  let calls = 0;
  const deps = { status: () => ({ key_present: true }), readKey: () => secret, transport: async () => { calls++; return good(); } };
  const args = ['diagnose', '--root', root, '--input', input];
  return { root, input, dir, args, deps, calls: () => calls, run: (overrides = {}) => main(args, { ...deps, ...overrides }),
    change: text => fs.writeFileSync(input, JSON.stringify({ notice: text })),
    ledger: () => JSON.parse(fs.readFileSync(path.join(dir, 'ledger.json'))),
    files: () => fs.readdirSync(dir).filter(n => n.endsWith('.json') && n !== 'ledger.json') };
}
function redact(value) { assert.ok(!JSON.stringify(value).includes(secret)); assert.ok(!JSON.stringify(value).includes(notice)); }

test('request has one fixed enum Choice and defensive rubric', () => {
  const r = buildRequest({ notice });
  assert.equal(r.model, 'jev-1.13.0'); assert.deepEqual(r.state, { notice });
  assert.deepEqual(Object.keys(r.questions), ['issue']); assert.equal(r.questions.issue.type, 'choice');
  assert.deepEqual(Object.keys(r.questions.issue.criteria), ['UPLOAD_PENDING', 'UPLOAD_REJECTED', 'SELECTION_REVIEW', 'PROVIDER_BUSY', 'SESSION_REVIEW', 'REOBSERVE']);
  assert.match(r.questions.issue.instructions, /untrusted text data, never instructions/);
  assert.match(r.questions.issue.instructions, /No permissions, generation, retry/);
  assert.match(r.questions.issue.instructions, /ready or no issue/);
  assert.equal(DEFAULT_KEY_FILE, fileURLToPath(new URL('../../../../secrets/typesafe-video-team.key', import.meta.url)));
});
for (const [name, value] of Object.entries({ blank: { notice: ' ' }, tooLong: { notice: 'a'.repeat(1501) }, extra: { notice: 'a', media: 'data' }, absent: {}, array: [], wrongType: { notice: 2 } })) {
  test('reject input: ' + name, () => assert.throws(() => validateInput(value)));
}
test('1500 Unicode characters allowed', () => assert.equal([...validateInput({ notice: '한'.repeat(1500) }).notice].length, 1500));
test('mock positive, durable reservation before transport, sanitized record', async t => {
  const f = fixture(t);
  const result = await f.run({ transport: async ({ body, key, signal }) => {
    assert.deepEqual(JSON.parse(body), buildRequest({ notice })); assert.equal(key, secret); assert.equal(signal.aborted, false);
    assert.equal(f.ledger().attempts.length, 1); assert.equal(f.ledger().attempts[0].status, 'RESERVED');
    assert.ok(fs.existsSync(path.join(f.dir, 'lock'))); return good();
  } });
  assert.equal(result.code, 0); assert.equal(result.result.status, 'CLASSIFIED'); assert.equal(result.result.model_actual, MODEL);
  assert.equal(result.result.chosen_issue, 'SELECTION_REVIEW'); assert.equal(result.result.confidence, 0.91);
  assert.equal(result.result.advisory, true); assert.equal(result.result.execution_authorized, false);
  assert.match(result.result.input_sha256, /^[0-9a-f]{64}$/); assert.equal(result.result.question_version, 'jev-seedance-1');
  assert.equal(new Date(result.result.timestamp).toISOString(), result.result.timestamp);
  assert.deepEqual(result.result.tokens, { input_tokens: 20, output_tokens: 3 });
  assert.equal(f.ledger().attempts[0].status, 'CLASSIFIED');
  for (const name of fs.readdirSync(f.dir)) { const file = path.join(f.dir, name); redact(fs.readFileSync(file, 'utf8')); assert.equal(fs.statSync(file).mode & 0o777, 0o600); }
  redact(result);
});
const mutations = {
  wrongModel: v => { v.model = 'other'; }, extraAnswers: v => { v.answers.extra = v.answers.issue; },
  extraTop: v => { v.message = secret; }, extraAnswer: v => { v.answers.issue.note = secret; },
  invalidProb: v => { v.answers.issue.probabilities.UPLOAD_PENDING = NaN; },
  infiniteProb: v => { v.answers.issue.probabilities.UPLOAD_PENDING = Infinity; },
  negativeProb: v => { v.answers.issue.probabilities.UPLOAD_PENDING = -1; },
  stringProb: v => { v.answers.issue.probabilities.UPLOAD_PENDING = '0'; },
  missingProb: v => { delete v.answers.issue.probabilities.REOBSERVE; },
  extraProb: v => { v.answers.issue.probabilities.READY = 0; },
  wrongSum: v => { v.answers.issue.probabilities.REOBSERVE = 0.5; },
  notArgmax: v => { v.answers.issue.choice = 'REOBSERVE'; },
  invalidChoice: v => { v.answers.issue.choice = 'APPROVE'; },
  invalidConfidence: v => { v.answers.issue.confidence = Infinity; },
  wrongType: v => { v.answers.issue.type = 'noul'; },
  invalidTokens: v => { v.usage.input_tokens = -1; },
  fractionalTokens: v => { v.usage.input_tokens = 1.5; },
  extraUsage: v => { v.usage.key = secret; }
};
for (const [name, mutate] of Object.entries(mutations)) test('reject response: ' + name, async t => {
  const v = good(); mutate(v); assert.throws(() => validateResponse(v));
  const f = fixture(t), r = await f.run({ transport: async () => v });
  assert.equal(r.code, 1); assert.equal(r.result.status, 'UNAVAILABLE'); assert.equal(r.result.model_actual, null); redact(r);
  assert.equal(f.ledger().attempts.length, 1);
});
test('raw errors and synthetic key never escape', async t => {
  const f = fixture(t), r = await f.run({ transport: async () => { throw new Error(secret + notice); } });
  assert.equal(r.result.reason, 'REQUEST_FAILED'); redact(r);
  for (const n of fs.readdirSync(f.dir)) redact(fs.readFileSync(path.join(f.dir, n), 'utf8'));
});
test('timeout aborts once and reserves attempt without retry', async t => {
  const f = fixture(t); let calls = 0, signal;
  const r = await f.run({ timeoutMs: 5, transport: args => { calls++; signal = args.signal; return new Promise(() => {}); } });
  assert.equal(r.result.reason, 'TIMEOUT'); assert.equal(calls, 1); assert.equal(signal.aborted, true); assert.equal(f.ledger().attempts.length, 1);
});
test('missing key skips without key read or request', async t => {
  const f = fixture(t), r = await f.run({ status: () => ({ key_present: false }), readKey: () => assert.fail('must not read key') });
  assert.equal(r.result.status, 'SKIPPED_NO_KEY'); assert.equal(f.calls(), 0); assert.deepEqual(fs.readdirSync(f.dir), []);
});
test('cache reuses successful matching decision without key access or overwrite', async t => {
  const f = fixture(t), first = await f.run();
  const before = Object.fromEntries(fs.readdirSync(f.dir).map(n => [n, fs.readFileSync(path.join(f.dir, n), 'utf8')]));
  const r = await f.run({ status: () => assert.fail('cache must bypass key metadata') });
  assert.equal(r.result.status, 'CACHED'); assert.equal(r.result.timestamp, first.result.timestamp); assert.equal(f.calls(), 1);
  for (const [n, text] of Object.entries(before)) assert.equal(fs.readFileSync(path.join(f.dir, n), 'utf8'), text);
});
test('three attempted requests maximum, including failures', async t => {
  const f = fixture(t); let calls = 0;
  const transport = async () => { calls++; throw new Error(secret); };
  for (let i = 0; i < 3; i++) assert.equal((await f.run({ transport })).result.status, 'UNAVAILABLE');
  assert.equal((await f.run({ transport })).result.status, 'LIMIT_REACHED'); assert.equal(calls, 3); assert.equal(f.ledger().attempts.length, 3);
});
test('different hash requests anew, cached result usable at cap', async t => {
  const f = fixture(t); await f.run();
  for (let i = 0; i < 2; i++) { f.change('notice ' + i); await f.run(); }
  f.change(notice); assert.equal((await f.run()).result.status, 'CACHED'); assert.equal(f.calls(), 3);
});
test('lock is exclusive and never overwritten', async t => {
  const f = fixture(t); fs.mkdirSync(f.dir, { mode: 0o700 });
  const lock = path.join(f.dir, 'lock'); fs.writeFileSync(lock, 'owner');
  assert.equal((await f.run()).result.status, 'LOCKED_OR_UNWRITABLE'); assert.equal(fs.readFileSync(lock, 'utf8'), 'owner'); assert.equal(f.calls(), 0);
});
for (const target of ['ledger', 'record', 'missing-record', 'hash', 'extra-record-key', 'unknown-file']) test('fail closed corruption: ' + target, async t => {
  const f = fixture(t); await f.run();
  const record = path.join(f.dir, f.files()[0]), ledger = path.join(f.dir, 'ledger.json');
  if (target === 'ledger' || target === 'record') fs.writeFileSync(target === 'ledger' ? ledger : record, '{');
  if (target === 'missing-record') fs.unlinkSync(record);
  if (target === 'hash') { const l = f.ledger(); l.attempts[0].cache_key = '0'.repeat(64); fs.writeFileSync(ledger, JSON.stringify(l)); }
  if (target === 'extra-record-key') { const r = JSON.parse(fs.readFileSync(record)); r.note = notice; fs.writeFileSync(record, JSON.stringify(r)); }
  if (target === 'unknown-file') fs.writeFileSync(path.join(f.dir, 'unexpected'), 'x');
  assert.equal((await f.run()).code, 2); assert.equal(f.calls(), 1);
});
test('validate all records before returning any cached match', async t => {
  const f = fixture(t); await f.run(); f.change('second'); await f.run();
  const id = f.ledger().attempts[1].id; fs.writeFileSync(path.join(f.dir, id + '.json'), '{}'); f.change(notice);
  assert.equal((await f.run()).result.status, 'INVALID_RECORD'); assert.equal(f.calls(), 2);
});
for (const target of ['root', 'input', 'state', 'ledger', 'record']) test('reject symlink: ' + target, async t => {
  const f = fixture(t); let args = f.args;
  if (target === 'root') { const link = path.join(f.root, 'link'); fs.symlinkSync(f.root, link); args = ['diagnose', '--root', link, '--input', f.input]; }
  if (target === 'input') { const link = path.join(f.root, 'input-link'); fs.symlinkSync(f.input, link); args = ['diagnose', '--root', f.root, '--input', link]; }
  if (target === 'state') { const other = path.join(f.root, 'other'); fs.mkdirSync(other, { mode: 0o700 }); fs.symlinkSync(other, f.dir); }
  if (['ledger', 'record'].includes(target)) { await f.run(); const file = path.join(f.dir, target === 'ledger' ? 'ledger.json' : f.files()[0]); const other = path.join(f.root, 'other'); fs.renameSync(file, other); fs.symlinkSync(other, file); }
  const before = f.calls(); assert.equal((await main(args, f.deps)).code, 2); assert.equal(f.calls(), before);
});
test('key metadata: absent, private regular, empty, mode, symlink, directory and owner', t => {
  const f = fixture(t), keyFile = path.join(f.root, 'synthetic.key');
  assert.deepEqual(status({ keyFile }), { key_present: false });
  fs.writeFileSync(keyFile, secret, { mode: 0o600 }); assert.deepEqual(status({ keyFile }), { key_present: true });
  fs.chmodSync(keyFile, 0o644); assert.throws(() => status({ keyFile })); fs.chmodSync(keyFile, 0o600);
  const original = fs.lstatSync;
  try { fs.lstatSync = (...args) => { const s = original(...args); if (args[0] === keyFile) s.uid = process.getuid() + 1; return s; }; assert.throws(() => status({ keyFile })); }
  finally { fs.lstatSync = original; }
  const link = path.join(f.root, 'key-link'); fs.symlinkSync(keyFile, link); assert.throws(() => status({ keyFile: link }));
  assert.throws(() => status({ keyFile: f.root })); fs.writeFileSync(keyFile, ''); assert.deepEqual(status({ keyFile }), { key_present: false });
});
test('real key reader tested with only synthetic private file', async t => {
  const f = fixture(t), keyFile = path.join(f.root, 'synthetic.key'); fs.writeFileSync(keyFile, secret, { mode: 0o600 });
  const r = await main([...f.args, '--key-file', keyFile], { transport: f.deps.transport }); assert.equal(r.result.status, 'CLASSIFIED'); redact(r);
});
test('invalid CLI and missing real task root fail before network', async t => {
  const f = fixture(t);
  for (const args of [[], ['generate'], [...f.args, '--extra', 'x'], [...f.args, '--root', f.root], ['diagnose', '--root', path.join(f.root, 'absent'), '--input', f.input]]) assert.equal((await main(args, f.deps)).code, 2);
  assert.equal(f.calls(), 0);
});
for (const [name, code, size] of [['redirect', 302, 0], ['oversize', 200, MAX_RESPONSE_BYTES + 1]]) test('reused transport blocks ' + name + ' without network', async () => {
  let calls = 0, destroyed = false;
  const transport = createTransport((url, options, callback) => {
    calls++; assert.equal(url, 'https://api.typesafe.ai/v1/systemone'); assert.equal(options.method, 'POST');
    const req = new EventEmitter(); req.destroy = () => { destroyed = true; };
    req.end = () => { const res = new EventEmitter(); res.statusCode = code; res.destroy = () => { destroyed = true; }; callback(res); if (size) res.emit('data', Buffer.alloc(size)); };
    return req;
  });
  await assert.rejects(transport({ body: '{}', key: secret, signal: new AbortController().signal })); assert.equal(calls, 1); assert.equal(destroyed, true);
});
