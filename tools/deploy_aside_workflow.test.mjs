import test from 'node:test';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import * as fs from 'node:fs/promises';
import { applyDeployment, checkDeployment, freezeSource } from './deploy_aside_workflow.mjs';

async function temp() { return fs.mkdtemp(path.join(os.tmpdir(), 'aside-workflow-test-')); }
async function write(file, text) { await fs.mkdir(path.dirname(file), { recursive: true }); await fs.writeFile(file, text); }
async function fixture() {
  const root = await temp(), source = path.join(root, 'source'), account = path.join(root, 'account');
  await fs.mkdir(account);
  await write(path.join(source, 'aside-video', 'SKILL.md'), '# skill\n');
  await write(path.join(source, 'aside-video', 'references', 'guide.md'), '# reference\n');
  await write(path.join(source, 'aside-video', 'references', 'config.json'), '{"a":1}\n');
  await write(path.join(source, 'aside-video', 'scripts', 'run.mjs'), 'export default 1;\n');
  await write(path.join(source, 'AGENTS.fragment.md'), '<!-- aside-video-workflow:start -->\nroot=<accountRoot>\n<!-- aside-video-workflow:end -->\n');
  await freezeSource({ sourceRoot: source });
  return { root, source, account };
}
async function cleanup(x) { await fs.rm(x.root, { recursive: true, force: true }); }

test('staged apply reaches check parity and preserves unrelated AGENTS text', async () => {
  const x = await fixture();
  try {
    await write(path.join(x.account, 'AGENTS.md'), 'before\n\nafter\n');
    const before = await checkDeployment({ sourceRoot: x.source, accountRoot: x.account });
    assert.equal(before.ok, false);
    await applyDeployment({ sourceRoot: x.source, accountRoot: x.account });
    assert.deepEqual(await checkDeployment({ sourceRoot: x.source, accountRoot: x.account }), { ok: true, problems: [] });
    const agents = await fs.readFile(path.join(x.account, 'AGENTS.md'), 'utf8');
    assert.match(agents, /^before\n\nafter\n/); assert.match(agents, new RegExp(`root=${x.account.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`));
  } finally { await cleanup(x); }
});

test('tampered frozen source blocks apply and check reports it', async () => {
  const x = await fixture();
  try {
    await write(path.join(x.source, 'aside-video', 'SKILL.md'), 'tampered\n');
    const checked = await checkDeployment({ sourceRoot: x.source, accountRoot: x.account });
    assert.equal(checked.ok, false); assert.match(checked.problems.join('\n'), /source manifest mismatch/);
    await assert.rejects(applyDeployment({ sourceRoot: x.source, accountRoot: x.account }), /source manifest mismatch/);
  } finally { await cleanup(x); }
});

test('changed installed files are backed up without removing unrelated files', async () => {
  const x = await fixture();
  try {
    await applyDeployment({ sourceRoot: x.source, accountRoot: x.account });
    await write(path.join(x.account, 'skills/user/aside-video/SKILL.md'), 'old\n');
    const result = await applyDeployment({ sourceRoot: x.source, accountRoot: x.account });
    assert.ok(result.backup);
    assert.equal(await fs.readFile(path.join(x.account, result.backup, 'skills/user/aside-video/SKILL.md'), 'utf8'), 'old\n');
    assert.equal(await fs.readFile(path.join(x.account, 'skills/user/aside-video/SKILL.md'), 'utf8'), '# skill\n');
  } finally { await cleanup(x); }
});

test('rejects unexpected source or installed files rather than deleting them', async () => {
  const x = await fixture();
  try {
    await write(path.join(x.source, 'aside-video', 'secret.txt'), 'no');
    await assert.rejects(freezeSource({ sourceRoot: x.source }), /unexpected source file/);
    await fs.rm(path.join(x.source, 'aside-video', 'secret.txt'));
    await applyDeployment({ sourceRoot: x.source, accountRoot: x.account });
    await write(path.join(x.account, 'skills/user/aside-video', 'unknown.bin'), 'keep');
    await assert.rejects(applyDeployment({ sourceRoot: x.source, accountRoot: x.account }), /unexpected installed file/);
    assert.equal(await fs.readFile(path.join(x.account, 'skills/user/aside-video', 'unknown.bin'), 'utf8'), 'keep');
  } finally { await cleanup(x); }
});

test('rejects symlink traversal and malformed manifests', async t => {
  const x = await fixture();
  try {
    try { await fs.symlink('/tmp', path.join(x.source, 'aside-video', 'references', 'escape')); }
    catch { t.skip('symlinks unavailable'); return; }
    await assert.rejects(freezeSource({ sourceRoot: x.source }), /symlinks are not allowed/);
    await fs.unlink(path.join(x.source, 'aside-video', 'references', 'escape'));
    await write(path.join(x.source, 'manifest.json'), JSON.stringify({ version: 1, files: [{ path: '../escape', sha256: '0'.repeat(64) }] }));
    const checked = await checkDeployment({ sourceRoot: x.source, accountRoot: x.account });
    assert.equal(checked.ok, false); assert.match(checked.problems.join('\n'), /invalid manifest|manifest file set/);
  } finally { await cleanup(x); }
});
