// Synthetic files only, under JEV_QC_TEST_TMP. No browser, network, credentials, or provider assertions.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { lookup, record, main } from './runway-assets.mjs';
const sha = text => createHash('sha256').update(text).digest('hex');
async function fixture(t) {
  assert.ok(process.env.JEV_QC_TEST_TMP, 'Set JEV_QC_TEST_TMP to an isolated test directory');
  const root = await fs.mkdtemp(path.join(await fs.realpath(process.env.JEV_QC_TEST_TMP), 'runway-assets-'));
  t.after(() => fs.rm(root, { recursive: true, force: true })); // Only this synthetic test root is removed.
  const file = path.join(root, 'source.png'), evidence = path.join(root, 'evidence.json'), registryDir = path.join(root, 'registry');
  const ev = { kind: 'upload_binding', observed_at: '2026-09-19T00:00:00.000Z', source_url: 'https://app.runwayml.com/video-tools/teams/test-team/assets', sha256: sha('mock image'), asset_name: 'Actual observed label.png', asset_id: 'observed-id' };
  const save = async () => fs.writeFile(evidence, JSON.stringify(ev));
  await fs.writeFile(file, 'mock image'); await save();
  return { root, ev, save, options: { scope: 'test-team', file, evidence, registryDir, assetName: ev.asset_name, assetId: ev.asset_id } };
}
const stored = async f => path.join(f.options.registryDir, (await fs.readdir(f.options.registryDir))[0]);
test('record/lookup JSON fields, actual hash, private modes and no source-path persistence', async t => {
  const f = await fixture(t), value = await record(f.options), file = await stored(f), raw = await fs.readFile(file, 'utf8');
  assert.equal(value.status, 'REGISTERED'); assert.deepEqual(await lookup(f.options), value);
  assert.equal(value.sha256, sha('mock image')); assert.equal(value.browser_reverification_required, true); assert.equal(value.upload_authorized, false);
  assert.equal(value.asset_name, f.ev.asset_name); assert.equal(value.source_url, f.ev.source_url); assert.equal(value.evidence_kind, 'upload_binding');
  assert.deepEqual(Object.keys(value).sort(), ['status', 'scope', 'sha256', 'asset_name', 'asset_id', 'source_url', 'evidence_kind', 'observed_at', 'timestamp', 'browser_reverification_required', 'upload_authorized'].sort());
  assert.equal((await fs.stat(f.options.registryDir)).mode & 0o777, 0o700); assert.equal((await fs.stat(file)).mode & 0o777, 0o600);
  assert.match(path.basename(file), /^[a-f0-9]{64}\.json$/); assert.ok(!raw.includes(f.root));
});
test('same bytes under different basenames hit; changed bytes under same basename miss; scopes segregate', async t => {
  const f = await fixture(t); await record(f.options); const other = path.join(f.root, 'different.jpg'); await fs.copyFile(f.options.file, other);
  assert.equal((await lookup({ ...f.options, file: other })).status, 'REGISTERED');
  await fs.writeFile(f.options.file, 'changed'); assert.equal((await lookup(f.options)).status, 'NOT_REGISTERED');
  assert.equal((await lookup({ ...f.options, file: other, scope: 'another-team' })).status, 'NOT_REGISTERED');
  await assert.rejects(record({ ...f.options, file: other, scope: 'another-team' }), /workspace mismatch/);
  f.ev.source_url='https://app.runwayml.com/video-tools/teams/another-team/assets'; await f.save();
  await record({ ...f.options, file: other, scope: 'another-team' }); assert.equal((await fs.readdir(f.options.registryDir)).length, 2);
});
test('repeat and conflicting name or ID never overwrite first record or its timestamp', async t => {
  const f = await fixture(t); await record(f.options); const file = await stored(f), bytes = await fs.readFile(file), stat = await fs.stat(file);
  f.ev.observed_at = '2026-09-19T01:00:00Z'; await f.save(); assert.equal((await record(f.options)).status, 'ALREADY_REGISTERED');
  f.ev.asset_name = 'Different'; await f.save(); assert.equal((await record({ ...f.options, assetName: f.ev.asset_name })).status, 'CONFLICT');
  f.ev.asset_name = f.options.assetName; f.ev.asset_id = 'other-id'; await f.save(); assert.equal((await record({ ...f.options, assetId: f.ev.asset_id })).status, 'CONFLICT');
  assert.deepEqual(await fs.readFile(file), bytes); assert.equal((await fs.stat(file)).mtimeMs, stat.mtimeMs);
});
test('independent download hash rejects missing, mismatched and same-file bytes, then accepts real match', async t => {
  const f = await fixture(t); f.ev.kind = 'download_hash'; await f.save(); const downloadedFile = path.join(f.root, 'download.png');
  await assert.rejects(record(f.options), /requires downloaded-file/); await assert.rejects(record({ ...f.options, downloadedFile: f.options.file }), /Independent/);
  await fs.link(f.options.file, downloadedFile); await assert.rejects(record({ ...f.options, downloadedFile }), /Independent/); await fs.unlink(downloadedFile);
  await fs.writeFile(downloadedFile, 'wrong'); await assert.rejects(record({ ...f.options, downloadedFile }), /hash mismatch/);
  await assert.rejects(fs.stat(f.options.registryDir), { code: 'ENOENT' }); await fs.copyFile(f.options.file, downloadedFile);
  assert.equal((await record({ ...f.options, downloadedFile })).evidence_kind, 'download_hash');
});
test('missing fields, invented binding kinds, malformed evidence and mismatches fail closed', async t => {
  const f = await fixture(t), original = { ...f.ev };
  for (const key of Object.keys(original)) { f.ev = { ...original }; delete f.ev[key]; await fs.writeFile(f.options.evidence, JSON.stringify(f.ev)); await assert.rejects(record(f.options)); }
  for (const patch of [{ kind: 'filename' }, { kind: 'visual_only' }, { sha256: sha('wrong') }, { asset_name: 'wrong' }, { asset_id: null }, { observed_at: '2026-02-30T00:00:00Z' }, { source_url: 'https://app.runwayml.com.evil.test/' }, { extra: true }]) {
    await fs.writeFile(f.options.evidence, JSON.stringify({ ...original, ...patch })); await assert.rejects(record(f.options));
  }
  await fs.writeFile(f.options.evidence, JSON.stringify(original)); await assert.rejects(record({ ...f.options, downloadedFile: f.options.file }));
  await assert.rejects(record({ ...f.options, assetName: undefined })); await assert.rejects(lookup({ ...f.options, scope: '../escape' }));
  await assert.rejects(lookup({ ...f.options, scope: 'x'.repeat(129) })); await assert.rejects(lookup({ ...f.options, file: `${f.root}/../source.png` }));
});
test('symlink source, ancestor, evidence, registry, record and downloaded file are rejected', async t => {
  const f = await fixture(t), link = path.join(f.root, 'link'); await fs.symlink(f.options.file, link);
  await assert.rejects(lookup({ ...f.options, file: link }), /symlink/); await fs.unlink(link); await fs.symlink(f.root, link);
  await assert.rejects(lookup({ ...f.options, file: path.join(link, 'source.png') }), /symlink/); await fs.unlink(link); await fs.symlink(f.options.evidence, link);
  await assert.rejects(record({ ...f.options, evidence: link }), /symlink/); await fs.unlink(link); await fs.symlink(f.root, link);
  await assert.rejects(record({ ...f.options, registryDir: link }), /symlink/); await fs.unlink(link); await record(f.options);
  const file = await stored(f); await fs.unlink(file); await fs.symlink(f.options.evidence, file); await assert.rejects(lookup(f.options), /symlink/);
  f.ev.kind = 'download_hash'; await f.save(); await fs.symlink(f.options.file, link); await assert.rejects(record({ ...f.options, downloadedFile: link }), /symlink/);
});
test('corrupt, misplaced, public and hardlinked records fail closed without repair', async t => {
  const f = await fixture(t); await record(f.options); const file = await stored(f), original = await fs.readFile(file, 'utf8');
  for (const raw of ['{', '{}', JSON.stringify({ ...JSON.parse(original), scope: 'wrong' })]) { await fs.writeFile(file, raw); await assert.rejects(lookup(f.options)); await assert.rejects(record(f.options)); assert.equal(await fs.readFile(file, 'utf8'), raw); }
  await fs.writeFile(file, original); await fs.chmod(file, 0o644); await assert.rejects(lookup(f.options)); await fs.chmod(file, 0o600);
  await fs.link(file, path.join(f.root, 'hardlink')); await assert.rejects(lookup(f.options)); await fs.chmod(f.options.registryDir, 0o755); await assert.rejects(record(f.options), /0700/);
});
test('CLI emits one JSON summary, rejects invalid args, and supports null asset IDs', async t => {
  const f = await fixture(t); f.ev.asset_id = null; await f.save();
  const args = ['record', '--scope', f.options.scope, '--file', f.options.file, '--asset-name', f.options.assetName, '--evidence', f.options.evidence, '--registry-dir', f.options.registryDir];
  const cli = spawnSync(process.execPath, [fileURLToPath(new URL('./runway-assets.mjs', import.meta.url)), ...args], { encoding: 'utf8' });
  assert.equal(cli.status, 0); assert.equal(cli.stderr, ''); assert.equal(cli.stdout.trim().split('\n').length, 1); assert.equal(JSON.parse(cli.stdout).asset_id, null);
  assert.equal((await main(args)).status, 'ALREADY_REGISTERED'); await assert.rejects(main(['lookup', '--file'])); await assert.rejects(main(['lookup', '--unknown', 'x']));
  const bad = spawnSync(process.execPath, [fileURLToPath(new URL('./runway-assets.mjs', import.meta.url)), 'record'], { encoding: 'utf8' });
  assert.equal(bad.status, 1); assert.equal(bad.stderr, ''); assert.equal(JSON.parse(bad.stdout).status, 'ERROR');
});
