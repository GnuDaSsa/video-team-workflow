import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';
import { main, DEFAULT_KEY_FILE, REASONS } from './jev-video.mjs';
import { MODEL, CATEGORIES, buildRequest, validateInput } from './jev-qc.mjs';

// No live network, credential reads, or production task roots. An explicit scratch parent is required.
const TMP = process.env.JEV_QC_TEST_TMP;
if (!TMP || !fs.statSync(TMP).isDirectory()) throw new Error('Set JEV_QC_TEST_TMP to an existing scratch directory');
const SECRET = 'SYNTHETIC_NEVER_PRINT_ME';
function fixture(t) {
  const root = fs.mkdtempSync(path.join(fs.realpathSync(TMP), 'jev-video-test-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const input = path.join(root, 'note.json');
  fs.writeFileSync(input, JSON.stringify({ qc_note: '관찰한 손가락 수가 비정상이다.' }));
  return { root, input, dir: path.join(root, '.jev') };
}
function recordFor(input, unavailable = false) {
  const state = validateInput(JSON.parse(fs.readFileSync(input, 'utf8')));
  const answers = Object.fromEntries(Object.entries(buildRequest(state).questions).map(([id, q]) => [id, q.type === 'choice'
    ? { type: 'choice', choice: 'ANATOMY', confidence: 1, probabilities: Object.fromEntries(CATEGORIES.map(c => [c, c === 'ANATOMY' ? 1 : 0])) }
    : { type: 'noul', noul: 0 }]));
  return { schema_version: 1, question_version: 'jev-qc-1', timestamp: new Date().toISOString(),
    input_sha256: crypto.createHash('sha256').update(JSON.stringify(state)).digest('hex'),
    input_hash_format: 'canonical_whitelisted_json_utf8_v1', observation_scope: state.observation_scope,
    model_requested: MODEL, model_actual: unavailable ? null : MODEL, answers: unavailable ? null : answers,
    usage: unavailable ? null : { input_tokens: 12, output_tokens: 3 }, status: unavailable ? 'UNAVAILABLE' : 'CLASSIFIED',
    reason: unavailable ? 'HTTP_ERROR' : null, advisory: true, execution_authorized: false, visual_qc: 'NOT_ASSESSED_BY_JEV' };
}
function mock({ present = true, unavailable = false, throws = false, hook } = {}) {
  const seen = { calls: 0, status: 0, keyFiles: [] };
  return { seen, status: async ({ keyFile }) => { seen.status++; seen.keyFiles.push(keyFile); return { key_present: present, secret: SECRET }; },
    classify: async options => {
      seen.calls++; seen.keyFiles.push(options.keyFile);
      if (hook) await hook(options);
      if (throws) throw new Error(SECRET);
      const r = recordFor(options.input, unavailable);
      fs.writeFileSync(options.out, JSON.stringify(r), { flag: 'wx', mode: 0o600 });
      return r;
    } };
}
const invoke = (f, deps, extra = []) => main(['classify', '--root', f.root, '--input', f.input, '--reason', 'mixed_findings', ...extra], deps);
const ledger = f => JSON.parse(fs.readFileSync(path.join(f.dir, 'ledger.json'), 'utf8'));
function safe(r) { assert.equal(r.advisory, true); assert.equal(r.execution_authorized, false); assert.ok(!JSON.stringify(r).includes(SECRET)); }

test('status is sanitized metadata only with stable default, not live access', async () => {
  const d = mock(); const r = await main(['status'], d);
  assert.equal(DEFAULT_KEY_FILE, fileURLToPath(new URL('../../../../secrets/typesafe-video-team.key', import.meta.url)));
  assert.deepEqual(r, { code: 0, result: { status: 'METADATA_ONLY', key_present: true, advisory: true, execution_authorized: false } });
  assert.deepEqual(d.seen.keyFiles, [DEFAULT_KEY_FILE]); assert.equal(d.seen.calls, 0);
});
test('status explicit key override passed without reading or printing it', async t => {
  const f = fixture(t), d = mock(), key = path.join(f.root, 'nonexistent.key');
  const r = await main(['status', '--key-file', key], d);
  assert.deepEqual(d.seen.keyFiles, [key]); safe(r.result); assert.ok(!JSON.stringify(r).includes(key));
});
for (const reason of REASONS) test('allowlisted reason: ' + reason, async t => {
  const f = fixture(t), d = mock();
  const r = await main(['classify', '--root', f.root, '--input', f.input, '--reason', reason], d);
  assert.equal(r.result.status, 'CLASSIFIED'); assert.equal(d.seen.calls, 1); safe(r.result);
});
for (const reason of ['generate', 'retry', SECRET]) test('reason rejected: ' + reason, async t => {
  const f = fixture(t), d = mock();
  const r = await main(['classify', '--root', f.root, '--input', f.input, '--reason', reason], d);
  assert.equal(r.result.status, 'INVALID_REASON'); assert.equal(d.seen.calls, 0); assert.equal(d.seen.status, 0); safe(r.result);
});
for (const args of [[], ['generate'], ['status', '--root', 'x'], ['status', '--key-file'], ['status', '--key-file', 'x', '--key-file', 'y'], ['classify', '--root', 'x']])
  test('strict CLI arguments ' + JSON.stringify(args), async () => { const d = mock(); assert.equal((await main(args, d)).code, 2); assert.equal(d.seen.calls, 0); });
test('canonical cache avoids re-request even without credentials; record and ledger immutable on cache', async t => {
  const f = fixture(t), d = mock(); const first = await invoke(f, d);
  const original = fs.readFileSync(first.result.path, 'utf8'), oldLedger = fs.readFileSync(path.join(f.dir, 'ledger.json'), 'utf8');
  const state = JSON.parse(fs.readFileSync(f.input));
  fs.writeFileSync(f.input, JSON.stringify({ observation_scope: 'text_only', qc_note: state.qc_note }, null, 2));
  const missing = mock({ present: false }); const second = await invoke(f, missing);
  assert.equal(second.result.status, 'CACHED'); assert.equal(second.result.path, first.result.path);
  assert.equal(missing.seen.calls, 0); assert.equal(missing.seen.status, 0);
  assert.equal(fs.readFileSync(first.result.path, 'utf8'), original); assert.equal(fs.readFileSync(path.join(f.dir, 'ledger.json'), 'utf8'), oldLedger);
  assert.equal(fs.statSync(f.dir).mode & 0o777, 0o700); assert.equal(fs.statSync(first.result.path).mode & 0o777, 0o600);
  assert.deepEqual(Object.keys(first.result).sort(), ['advisory', 'category', 'confidence', 'execution_authorized', 'path', 'status']);
  safe(JSON.parse(original)); safe(first.result);
});
test('five successful distinct attempts cap; cached result still accessible at cap', async t => {
  const f = fixture(t), d = mock(); const paths = new Set();
  for (let i = 0; i < 5; i++) { fs.writeFileSync(f.input, JSON.stringify({ qc_note: 'note ' + i })); const r = await invoke(f, d); paths.add(r.result.path); }
  assert.equal(paths.size, 5); assert.equal(ledger(f).attempts.length, 5);
  assert.equal((await invoke(f, d)).result.status, 'CACHED');
  fs.writeFileSync(f.input, JSON.stringify({ qc_note: 'sixth' })); assert.equal((await invoke(f, d)).result.status, 'LIMIT_REACHED'); assert.equal(d.seen.calls, 5);
});
for (const throws of [false, true]) test('unavailable fallback counts each explicit attempt, never internally retries: throws=' + throws, async t => {
  const f = fixture(t), d = mock({ unavailable: true, throws });
  for (let i = 0; i < 5; i++) { const r = await invoke(f, d); assert.equal(r.result.status, 'UNAVAILABLE'); assert.equal(d.seen.calls, i + 1); safe(r.result); }
  assert.equal((await invoke(f, d)).result.status, 'LIMIT_REACHED'); assert.equal(d.seen.calls, 5); assert.equal(ledger(f).attempts.length, 5);
});
test('missing key skips classifier and does not spend an attempt', async t => {
  const f = fixture(t), d = mock({ present: false }); const r = await invoke(f, d);
  assert.equal(r.result.status, 'SKIPPED_NO_KEY'); assert.equal(d.seen.calls, 0); assert.deepEqual(fs.readdirSync(f.dir), []); safe(r.result);
});
test('injected metadata exception is sanitized; no API', async t => {
  const f = fixture(t), d = mock(); d.status = () => { throw new Error(SECRET); };
  const r = await invoke(f, d); assert.equal(r.code, 2); safe(r.result); assert.equal(d.seen.calls, 0);
});
for (const value of [null, {}, { qc_note: '' }, { qc_note: 'ok', extra: SECRET }, { qc_note: 'ok', observation_scope: 'PASS' }, { qc_note: 'a'.repeat(6001) }])
  test('invalid input rejected: ' + (value?.observation_scope ?? Object.keys(value ?? {}).join(',')), async t => {
    const f = fixture(t), d = mock(); fs.writeFileSync(f.input, JSON.stringify(value));
    assert.equal((await invoke(f, d)).result.status, 'INVALID_INPUT'); assert.equal(d.seen.calls, 0); assert.equal(d.seen.status, 0);
  });
for (const kind of ['malformed', 'oversized', 'symlink', 'directory', 'missing']) test('bad input path/content: ' + kind, async t => {
  const f = fixture(t), d = mock();
  if (kind === 'malformed') fs.writeFileSync(f.input, SECRET);
  if (kind === 'oversized') fs.writeFileSync(f.input, ' '.repeat(65537));
  if (['symlink', 'directory', 'missing'].includes(kind)) fs.unlinkSync(f.input);
  if (kind === 'symlink') { const target = path.join(f.root, 'target'); fs.writeFileSync(target, '{"qc_note":"ok"}'); fs.symlinkSync(target, f.input); }
  if (kind === 'directory') fs.mkdirSync(f.input);
  const r = await invoke(f, d); assert.equal(r.result.status, 'INVALID_INPUT'); safe(r.result); assert.equal(d.seen.calls, 0);
});
for (const kind of ['missing', 'file', 'symlink']) test('bad root: ' + kind, async t => {
  const f = fixture(t), d = mock(), bad = path.join(f.root, 'bad');
  if (kind === 'file') fs.writeFileSync(bad, 'x'); if (kind === 'symlink') fs.symlinkSync(f.root, bad);
  assert.equal((await invoke({ ...f, root: bad }, d)).result.status, 'INVALID_ROOT'); assert.equal(d.seen.calls, 0);
});
for (const kind of ['symlink', 'file', 'unsafe-mode']) test('unsafe state directory: ' + kind, async t => {
  const f = fixture(t), d = mock();
  if (kind === 'symlink') fs.symlinkSync(f.root, f.dir);
  if (kind === 'file') fs.writeFileSync(f.dir, 'x');
  if (kind === 'unsafe-mode') fs.mkdirSync(f.dir, { mode: 0o755 });
  assert.equal((await invoke(f, d)).result.status, 'INVALID_STATE_DIR'); assert.equal(d.seen.calls, 0);
});
for (const kind of ['file', 'symlink']) test('existing lock retained, no API: ' + kind, async t => {
  const f = fixture(t), d = mock(); fs.mkdirSync(f.dir, { mode: 0o700 }); const lock = path.join(f.dir, 'lock');
  if (kind === 'file') fs.writeFileSync(lock, SECRET); else fs.symlinkSync(f.input, lock);
  assert.equal((await invoke(f, d)).result.status, 'LOCKED_OR_UNWRITABLE'); assert.ok(fs.lstatSync(lock)); assert.equal(d.seen.calls, 0);
});
test('concurrent call is blocked by exclusive lock; durable reservation precedes API', async t => {
  const f = fixture(t); let unblock, entered; const waiting = new Promise(r => { unblock = r; }); const ready = new Promise(r => { entered = r; });
  const d = mock({ hook: async () => { assert.equal(ledger(f).attempts.length, 1); entered(); await waiting; } });
  const first = invoke(f, d); await ready;
  assert.equal((await invoke(f, d)).result.status, 'LOCKED_OR_UNWRITABLE'); assert.equal(d.seen.calls, 1);
  unblock(); assert.equal((await first).result.status, 'CLASSIFIED'); assert.equal(fs.existsSync(path.join(f.dir, 'lock')), false);
});
for (const kind of ['malformed', 'symlink', 'extra', 'over-cap', 'orphan']) test('corrupt ledger fails closed: ' + kind, async t => {
  const f = fixture(t), d = mock(); fs.mkdirSync(f.dir, { mode: 0o700 }); const file = path.join(f.dir, 'ledger.json');
  if (kind === 'malformed') fs.writeFileSync(file, SECRET);
  if (kind === 'symlink') fs.symlinkSync(f.input, file);
  if (kind === 'extra') fs.writeFileSync(file, JSON.stringify({ schema_version: 1, attempts: [], extra: 1 }));
  if (kind === 'over-cap') fs.writeFileSync(file, JSON.stringify({ schema_version: 1, attempts: Array(6).fill({}) }));
  if (kind === 'orphan') fs.writeFileSync(path.join(f.dir, 'old.json'), '{}');
  assert.equal((await invoke(f, d)).result.status, 'CORRUPT_LEDGER'); assert.equal(d.seen.calls, 0); assert.equal(d.seen.status, 0);
});
for (const [name, change] of [
  ['hash', r => r.input_sha256 = '0'.repeat(64)], ['model', r => r.model_actual = 'wrong'],
  ['requested-model', r => r.model_requested = 'wrong'], ['version', r => r.question_version = 'wrong'],
  ['advisory', r => r.advisory = false], ['execution', r => r.execution_authorized = true],
  ['response', r => r.answers.category.confidence = 2], ['category', r => r.answers.category.choice = SECRET]
]) test('corrupt cached record never reused or resubmitted: ' + name, async t => {
  const f = fixture(t), d = mock(), first = await invoke(f, d), file = first.result.path;
  const r = JSON.parse(fs.readFileSync(file)); change(r); fs.writeFileSync(file, JSON.stringify(r));
  const second = await invoke(f, d); assert.equal(second.result.status, 'INVALID_RECORD'); assert.equal(d.seen.calls, 1); safe(second.result);
});
test('cached result symlink rejected', async t => {
  const f = fixture(t), d = mock(), first = await invoke(f, d); fs.unlinkSync(first.result.path); fs.symlinkSync(f.input, first.result.path);
  assert.equal((await invoke(f, d)).result.status, 'INVALID_RECORD'); assert.equal(d.seen.calls, 1);
});
test('caller input changes cannot alter staged classifier input', async t => {
  const f = fixture(t), original = fs.readFileSync(f.input, 'utf8');
  const d = mock({ hook: async ({ input }) => { fs.writeFileSync(f.input, '{"qc_note":"changed"}'); assert.equal(JSON.parse(fs.readFileSync(input)).qc_note, JSON.parse(original).qc_note); } });
  const r = await invoke(f, d); assert.equal(r.result.status, 'CLASSIFIED'); assert.ok(!fs.readdirSync(f.dir).some(s => s.startsWith('.input-')));
});

test('missing successful record is corruption, never a reason to resubmit', async t => {
  const f = fixture(t), d = mock(), first = await invoke(f, d);
  assert.equal(ledger(f).attempts[0].status, 'CLASSIFIED'); fs.unlinkSync(first.result.path);
  assert.equal((await invoke(f, d)).result.status, 'INVALID_RECORD'); assert.equal(d.seen.calls, 1);
});
test('deleted ledger with existing records fails closed instead of resetting cap', async t => {
  const f = fixture(t), d = mock(); await invoke(f, d); fs.unlinkSync(path.join(f.dir, 'ledger.json'));
  assert.equal((await invoke(f, d)).result.status, 'CORRUPT_LEDGER'); assert.equal(d.seen.calls, 1);
});
test('atomic ledger failure blocks classifier and cleans staging/lock', async t => {
  const f = fixture(t), d = mock(); d.status = () => { fs.mkdirSync(path.join(f.dir, 'ledger.json')); return { key_present: true }; };
  const r = await invoke(f, d); assert.equal(r.result.status, 'LOCAL_ERROR'); assert.equal(d.seen.calls, 0);
  assert.deepEqual(fs.readdirSync(f.dir), ['ledger.json']);
});
test('classifier receives explicit key-file without runner opening it', async t => {
  const f = fixture(t), d = mock(), keyFile = path.join(f.root, 'never-created.key');
  assert.equal((await invoke(f, d, ['--key-file', keyFile])).result.status, 'CLASSIFIED');
  assert.deepEqual(d.seen.keyFiles, [keyFile, keyFile]); assert.equal(fs.existsSync(keyFile), false);
});
test('distinct results never overwrite previous record', async t => {
  const f = fixture(t), d = mock(), first = await invoke(f, d), bytes = fs.readFileSync(first.result.path);
  fs.writeFileSync(f.input, JSON.stringify({ qc_note: 'different observation' })); const second = await invoke(f, d);
  assert.notEqual(first.result.path, second.result.path); assert.deepEqual(fs.readFileSync(first.result.path), bytes);
});
test('cleanup does not unlink replacement lock', async t => {
  const f = fixture(t), d = mock({ hook: async () => { const lock = path.join(f.dir, 'lock'); fs.unlinkSync(lock); fs.symlinkSync(f.input, lock); } });
  await invoke(f, d); assert.equal(fs.lstatSync(path.join(f.dir, 'lock')).isSymbolicLink(), true);
});
test('corrupt cache key cannot cause resubmission of a successful note', async t => {
  const f = fixture(t), d = mock(); await invoke(f, d); const l = ledger(f); l.attempts[0].cache_key = '0'.repeat(64);
  fs.writeFileSync(path.join(f.dir, 'ledger.json'), JSON.stringify(l));
  assert.equal((await invoke(f, d)).result.status, 'CORRUPT_LEDGER'); assert.equal(d.seen.calls, 1);
});
