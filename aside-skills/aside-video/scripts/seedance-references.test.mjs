// Synthetic local file tests only. No browser, API, provider, Jev, or visual-QC evidence.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { prepare, verify, main } from './seedance-references.mjs';
import { request, seal, sha256 } from './harness.mjs';
import { prepare as submissionPrepare, verify as submissionVerify } from './submission.mjs';

const TMP = process.env.JEV_QC_TEST_TMP || os.tmpdir();
const SCRIPT = fileURLToPath(new URL('./seedance-references.mjs', import.meta.url));
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a6/8AAAAASUVORK5CYII=', 'base64');
const JPEG = Buffer.from('ffd8ffe000104a46494600010100000100010000ffd9', 'hex');
const WEBP = Buffer.concat([Buffer.from('RIFF'), Buffer.from([12, 0, 0, 0]), Buffer.from('WEBPVP8 '), Buffer.alloc(4)]);
async function fixture(t, count = 2) {
  const temporary = await fs.mkdtemp(path.join(TMP, 'seedance-reference-test-'));
  const root = await fs.realpath(temporary);
  // Cleanup is restricted to this test-created root, never production paths.
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const references = [];
  for (let i = 0; i < count; i++) {
    const directory = path.join(root, `source-${i}`);
    await fs.mkdir(directory);
    const file = path.join(directory, 'same.png');
    const raw = Buffer.concat([PNG, Buffer.from(String(i))]);
    await fs.writeFile(file, raw, { mode: 0o600 });
    references.push({ path: file, sha256: sha256(raw), role: `identity-${i}` });
  }
  const manifest = path.join(root, 'input.json'), outDir = path.join(root, 'bundle');
  await fs.writeFile(manifest, JSON.stringify(references));
  return { root, references, manifest, outDir, options: { references: manifest, outDir } };
}
const readJSON = async file => JSON.parse(await fs.readFile(file, 'utf8'));
async function rewrite(file, value) {
  await fs.chmod(file, 0o600);
  const raw = Buffer.isBuffer(value) ? value : Buffer.from(JSON.stringify(value, null, 2) + '\n');
  await fs.writeFile(file, raw);
  await fs.chmod(file, 0o400);
  return sha256(raw);
}
async function absent(file) { await assert.rejects(fs.lstat(file), { code: 'ENOENT' }); }

test('duplicate basenames get deterministic full-hash names; source bytes and metadata stay unchanged', async t => {
  const f = await fixture(t);
  const before = await Promise.all(f.references.map(async r => ({ raw: await fs.readFile(r.path), stat: await fs.stat(r.path) })));
  const result = await prepare(f.options), plan = await readJSON(result.plan);
  const paths = await verify(result.plan, result.plan_sha256);
  assert.equal(result.kind, 'seedance_reference_bundle');
  assert.equal(result.plan_sha256, sha256(await fs.readFile(result.plan)));
  assert.equal(result.reference_count, 2);
  assert.equal(Object.hasOwn(result, 'upload_paths'), false);
  assert.equal((await fs.stat(f.outDir)).mode & 0o777, 0o700);
  assert.equal(new Set(paths).size, 2);
  for (const [i, ref] of plan.references.entries()) {
    assert.equal(ref.index, i + 1); assert.equal(ref.slot, `Image${i + 1}`);
    assert.equal(ref.role, f.references[i].role);
    assert.equal(ref.upload_name, `ref-0${i + 1}-${f.references[i].sha256}.png`);
    assert.equal(ref.source_path, f.references[i].path);
    assert.equal(ref.upload_path, paths[i]);
    assert.deepEqual(await fs.readFile(paths[i]), before[i].raw);
    assert.deepEqual(await fs.readFile(ref.source_path), before[i].raw);
    const after = await fs.stat(ref.source_path);
    assert.equal(after.mode, before[i].stat.mode); assert.equal(after.mtimeMs, before[i].stat.mtimeMs);
    assert.notEqual((await fs.stat(paths[i])).ino, after.ino);
    assert.equal((await fs.stat(paths[i])).mode & 0o777, 0o400);
  }
  assert.deepEqual(await readJSON(result.files.upload_files.path), paths);
  for (const file of Object.values(result.files)) assert.equal(file.sha256, sha256(await fs.readFile(file.path)));
  // The input manifest is not re-searched or read after preparation.
  await fs.unlink(f.manifest);
  assert.deepEqual(await verify(result.plan, result.plan_sha256), paths);
});

test('explicit empty references succeed and absence does not', async t => {
  const f = await fixture(t, 0);
  await assert.rejects(prepare({ outDir: f.outDir }));
  const result = await main(['prepare', '--references', f.manifest, '--out-dir', f.outDir]);
  assert.deepEqual(await main(['verify', result.plan, '--sha256', result.plan_sha256]), []);
  assert.deepEqual(await readJSON(result.files.references.path), []);
});

test('duplicate hashes are rejected even at different source paths', async t => {
  const f = await fixture(t);
  await fs.writeFile(f.references[1].path, await fs.readFile(f.references[0].path));
  f.references[1].sha256 = f.references[0].sha256;
  await rewrite(f.manifest, f.references);
  await assert.rejects(prepare(f.options), /Duplicate reference hash/); await absent(f.outDir);
});

test('strict input metadata rejects missing, unexpected, credential, role, hash and path fields', async t => {
  const f = await fixture(t), good = f.references[0];
  const bad = [null, {}, [null], [{ ...good, role: '' }], [{ ...good, role: '  ' }],
    [{ ...good, role: 2 }], [{ ...good, role: 'password=synthetic' }], [{ ...good, password: 'synthetic' }],
    [{ ...good, extra: true }], [{ path: good.path, sha256: good.sha256 }],
    [{ ...good, path: 'relative.png' }], [{ ...good, path: `${f.root}/source-0/../source-0/same.png` }],
    [{ ...good, sha256: good.sha256.toUpperCase() }], [{ ...good, sha256: 'short' }]];
  for (const value of bad) {
    await rewrite(f.manifest, value); await assert.rejects(prepare(f.options)); await absent(f.outDir);
  }
});

test('PNG, JPEG and WebP magic determine coherent normalized staged suffixes', async t => {
  const f = await fixture(t, 0), references = [];
  for (const [i, [suffix, raw]] of [['.PNG', PNG], ['.jpeg', JPEG], ['.webp', WEBP]].entries()) {
    const file = path.join(f.root, `source${suffix}`); await fs.writeFile(file, raw);
    references.push({ path: file, sha256: sha256(raw), role: `role${i}` });
  }
  await rewrite(f.manifest, references);
  const result = await prepare(f.options), paths = await verify(result.plan, result.plan_sha256);
  assert.deepEqual(paths.map(p => path.extname(p)), ['.png', '.jpg', '.webp']);
});

for (const [label, raw, suffix] of [['mismatch', PNG, '.jpg'], ['unknown', Buffer.from('GIF89a'), '.png'], ['truncated', Buffer.from('RIFF'), '.webp']]) {
  test(`rejects ${label} image format and explicitly leaves failed directory`, async t => {
    const f = await fixture(t, 0), file = path.join(f.root, `image${suffix}`);
    await fs.writeFile(file, raw); await rewrite(f.manifest, [{ path: file, sha256: sha256(raw), role: 'identity' }]);
    await assert.rejects(prepare(f.options), /partial directory retained/);
    assert.equal((await fs.stat(f.outDir)).isDirectory(), true); await absent(path.join(f.outDir, 'plan.json'));
  });
}

for (const target of ['source', 'staged']) {
  for (const mutation of ['bytes', 'missing', 'symlink']) {
    test(`${target} ${mutation} invalidates verification`, async t => {
      const f = await fixture(t), result = await prepare(f.options), plan = await readJSON(result.plan);
      const file = plan.references[0][target === 'source' ? 'source_path' : 'upload_path'];
      if (mutation === 'bytes') await rewrite(file, Buffer.concat([PNG, Buffer.from('changed')]));
      else { const original = await fs.readFile(file); await fs.unlink(file);
        if (mutation === 'symlink') { const other = path.join(f.root, 'other.png'); await fs.writeFile(other, original); await fs.symlink(other, file); }
      }
      await assert.rejects(verify(result.plan, result.plan_sha256));
    });
  }
}

test('no overwrite of existing directory, files, or output symlink', async t => {
  const f = await fixture(t), result = await prepare(f.options), before = await fs.readFile(result.plan);
  await assert.rejects(prepare(f.options), { code: 'EEXIST' });
  assert.deepEqual(await fs.readFile(result.plan), before);
  const link = path.join(f.root, 'out-link'); await fs.symlink(f.outDir, link);
  await assert.rejects(prepare({ ...f.options, outDir: link }), { code: 'EEXIST' });
  const empty = path.join(f.root, 'existing-empty'); await fs.mkdir(empty);
  await assert.rejects(prepare({ ...f.options, outDir: empty }), { code: 'EEXIST' });
});

test('source, manifest, ancestor and output-parent symlinks are rejected', async t => {
  const f = await fixture(t), link = path.join(f.root, 'source-link.png');
  await fs.symlink(f.references[0].path, link);
  await rewrite(f.manifest, [{ ...f.references[0], path: link }]); await assert.rejects(prepare(f.options), /Symlink/);
  const manifestLink = path.join(f.root, 'manifest-link.json'); await fs.symlink(f.manifest, manifestLink);
  await assert.rejects(prepare({ ...f.options, references: manifestLink }), /Symlink/);
  const parentLink = path.join(f.root, 'parent-link'); await fs.symlink(path.dirname(f.references[0].path), parentLink);
  await rewrite(f.manifest, [{ ...f.references[0], path: path.join(parentLink, 'same.png') }]);
  await assert.rejects(prepare({ ...f.options, outDir: path.join(f.root, 'second') }), /Symlink/);
  await rewrite(f.manifest, []);
  await assert.rejects(prepare({ ...f.options, outDir: path.join(parentLink, 'bundle') }), /Symlink/);
});

test('nonregular sources and bad hashes are rejected', async t => {
  const f = await fixture(t);
  await rewrite(f.manifest, [{ ...f.references[0], path: path.dirname(f.references[0].path) }]);
  await assert.rejects(prepare(f.options), /regular/);
  await rewrite(f.manifest, [{ ...f.references[0], sha256: '0'.repeat(64) }]);
  await assert.rejects(prepare({ ...f.options, outDir: path.join(f.root, 'second') }), /hash mismatch/);
});

test('plan schema, missing metadata, swapped slots and paths fail even with newly accepted hash', async t => {
  const f = await fixture(t), result = await prepare(f.options), original = await readJSON(result.plan);
  const changes = [p => { delete p.files; }, p => { delete p.references[0].role; }, p => { delete p.references; },
    p => { p.kind = 'uploaded'; }, p => { p.schema_version = 2; }, p => { p.password = 'synthetic'; },
    p => { p.references.reverse(); }, p => { p.references[0].slot = 'Image2'; }, p => { p.references[0].index = 0; },
    p => { p.references[0].upload_path = p.references[1].upload_path; },
    p => { p.references[0].upload_path = f.references[0].path; },
    p => { p.references[0].upload_name = '../escape.png'; },
    p => { p.files.references.path = f.manifest; }, p => { p.files.upload_files.extra = true; },
    p => { p.structural_max_references = 1; }, p => { p.structural_max_references = 101; }];
  for (const change of changes) {
    const changed = structuredClone(original); change(changed); const accepted = await rewrite(result.plan, changed);
    await assert.rejects(verify(result.plan, result.plan_sha256), /Plan hash mismatch/);
    await assert.rejects(verify(result.plan, accepted));
  }
});

test('role-only or coherent order changes cannot bypass original independent acceptance', async t => {
  const f = await fixture(t), result = await prepare(f.options), plan = await readJSON(result.plan);
  plan.references[0].role = 'another identity'; await rewrite(result.plan, plan);
  await assert.rejects(verify(result.plan, result.plan_sha256), /Plan hash mismatch/);
});

for (const key of ['references', 'upload_files']) {
  test(`${key} child hashes and ordered array consistency are checked`, async t => {
    const f = await fixture(t), result = await prepare(f.options), plan = await readJSON(result.plan);
    const child = plan.files[key], original = await readJSON(child.path);
    original.reverse(); const childHash = await rewrite(child.path, original);
    await assert.rejects(verify(result.plan, result.plan_sha256), /Child hash mismatch/);
    child.sha256 = childHash;
    await assert.rejects(verify(result.plan, await rewrite(result.plan, plan)), /ordered array mismatch/);
    await fs.unlink(child.path); await fs.symlink(f.manifest, child.path);
    await assert.rejects(verify(result.plan, sha256(await fs.readFile(result.plan))), /Symlink/);
  });
}

test('independent accepted hash is mandatory and plan symlinks fail', async t => {
  const f = await fixture(t), result = await prepare(f.options);
  for (const hash of [undefined, '', '0'.repeat(64), result.plan_sha256.toUpperCase()]) await assert.rejects(verify(result.plan, hash));
  const raw = await fs.readFile(result.plan), other = path.join(f.root, 'other.json'); await fs.writeFile(other, raw);
  await fs.unlink(result.plan); await fs.symlink(other, result.plan);
  await assert.rejects(verify(result.plan, result.plan_sha256), /Symlink/);
});

test('structural cap is configurable, defaults to 100, and does not guess a nine-image provider cap', async t => {
  const f = await fixture(t, 10);
  await assert.rejects(prepare({ ...f.options, maxReferences: 9 }), /structural safety/); await absent(f.outDir);
  for (const cap of [-1, 101, 1.5, '10']) await assert.rejects(prepare({ ...f.options, maxReferences: cap }));
  const result = await prepare(f.options); assert.equal((await verify(result.plan, result.plan_sha256)).length, 10);
  assert.equal((await readJSON(result.plan)).structural_max_references, 100);
  await rewrite(f.manifest, Array(101).fill(f.references[0]));
  await assert.rejects(prepare({ ...f.options, outDir: path.join(f.root, 'second') }), /structural safety/);
});

test('CLI validates required, duplicate, unknown and traversal inputs; executable verify prints only array', async t => {
  const f = await fixture(t, 0);
  for (const args of [[], ['upload'], ['prepare'], ['prepare', '--references', f.manifest],
    ['prepare', '--references', f.manifest, '--out-dir', f.outDir, '--max-references', '1e2'],
    ['prepare', '--references', f.manifest, '--references', f.manifest, '--out-dir', f.outDir],
    ['verify', 'plan'], ['verify', 'plan', '--sha256', 'x', '--upload'],
    ['verify', 'plan', 'extra', '--sha256', 'x']]) await assert.rejects(main(args));
  await assert.rejects(prepare({ ...f.options, outDir: `${f.root}/../escape` }), /traversal/);
  const prepared = spawnSync(process.execPath, [SCRIPT, 'prepare', '--references', f.manifest, '--out-dir', f.outDir, '--max-references', '0'], { encoding: 'utf8' });
  assert.equal(prepared.status, 0, prepared.stderr); const result = JSON.parse(prepared.stdout);
  const checked = spawnSync(process.execPath, [SCRIPT, 'verify', result.plan, '--sha256', result.plan_sha256], { encoding: 'utf8' });
  assert.equal(checked.status, 0, checked.stderr); assert.deepEqual(JSON.parse(checked.stdout), []);
});

test('exported references.json passes actual submission prepare/verify unchanged', async t => {
  const f = await fixture(t), result = await prepare(f.options), prompt = 'Synthetic Seedance reference-binding test only.\n';
  await fs.writeFile(path.join(f.root, 'prompt.txt'), prompt);
  const requested = await request({ stage: 'seedance_prompt', root: f.root, prompt: 'prompt.txt', out: 'request.json',
    context: { user_instruction: 'Synthetic reference-binding test in English.', model: { modelId: 'gpt-6-astra' }, session_id: 'SYNTHETIC-requester' } });
  const evidence = path.join(f.root, 'messages.jsonl');
  await fs.writeFile(evidence, JSON.stringify({ role: 'assistant', model: 'gpt-6-astra', provider: 'synthetic', api: 'synthetic',
    responseId: 'SYNTHETIC-response', session_id: 'SYNTHETIC-author', usage: { input: 1, output: 1 },
    timestamp: requested.created_at + 1, stopReason: 'stop', content: [{ type: 'text', text: `Prompt-SHA256: ${sha256(Buffer.from(prompt))}` }] }) + '\n');
  const receipt = await seal({ request: requested.file, evidence, out: 'receipt.json' });
  const submitted = await submissionPrepare({ stage: 'seedance_prompt', receipt: receipt.file, sha256: receipt.receipt_sha256,
    out: path.join(f.root, 'payload.json'), references: result.files.references.path });
  const checked = await submissionVerify(submitted.file, submitted.payload_sha256);
  assert.deepEqual(checked.payload.references, await readJSON(result.files.references.path));
  assert.deepEqual(checked.payload.references.map(r => r.path), await verify(result.plan, result.plan_sha256));
});


test('writable staged files, nonprivate directory and hardlink substitutions are rejected', async t => {
  const f = await fixture(t), result = await prepare(f.options), plan = await readJSON(result.plan);
  const staged = plan.references[0].upload_path;
  await fs.chmod(staged, 0o600);
  await assert.rejects(verify(result.plan, result.plan_sha256), /private read-only/);
  await fs.chmod(staged, 0o400); await fs.chmod(f.outDir, 0o755);
  await assert.rejects(verify(result.plan, result.plan_sha256), /directory must remain private/);
  await fs.chmod(f.outDir, 0o700); await fs.unlink(staged);
  await fs.link(f.references[0].path, staged); await fs.chmod(staged, 0o400);
  await assert.rejects(verify(result.plan, result.plan_sha256), /single-link/);
});

test('high-bit pseudo-WebP magic cannot pass an ASCII-masking check', async t => {
  const f = await fixture(t, 0), file = path.join(f.root, 'fake.webp'), raw = Buffer.from(WEBP);
  raw[0] |= 0x80; await fs.writeFile(file, raw);
  await rewrite(f.manifest, [{ path: file, sha256: sha256(raw), role: 'identity' }]);
  await assert.rejects(prepare(f.options), /magic/);
});
