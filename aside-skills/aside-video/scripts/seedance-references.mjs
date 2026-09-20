#!/usr/bin/env node
// Local file binding only: NOT browser attachment, upload, provider, or visual-QC evidence.
// Immutable means private read-only copies + independently accepted hashes, not OS attestation.
// maxReferences (default/hard ceiling 100) is configurable local safety, NOT a provider limit.
// Inputs are explicit ordered manifests; there is no basename search or directory enumeration.
import fs from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';

const fail = message => { throw new Error(message); };
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const encode = value => Buffer.from(`${JSON.stringify(value, null, 2)}\n`);
const decode = raw => JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(raw));
const KIND = 'seedance_reference_bundle';
function keys(value, expected) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      !isDeepStrictEqual(Object.keys(value).sort(), [...expected].sort())) fail('Invalid metadata fields');
}
function absolute(value) {
  if (typeof value !== 'string' || !path.isAbsolute(value) || value.includes('\0') ||
      value.includes('\\') || path.resolve(value) !== value) fail('Expected canonical absolute path without traversal');
  return value;
}
function hash(value) {
  if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) fail('Independently accepted lowercase SHA256 required');
}
function limit(value) {
  if (!Number.isInteger(value) || value < 0 || value > 100) fail('Structural maxReferences must be an integer from 0 to 100');
  return value;
}
function role(value) {
  if (typeof value !== 'string' || !value.trim()) fail('Reference role must be nonempty');
  // Never accept credential-bearing metadata; roles describe an image, not authentication.
  if (/(?:password|passwd|pwd|api[_ -]?key|access[_ -]?token)\s*[:=]/i.test(value)) fail('Credential metadata is forbidden');
}
async function safePath(file, directory = false) {
  absolute(file);
  let current = path.parse(file).root;
  for (const part of path.relative(current, file).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    const stat = await fs.lstat(current);
    if (stat.isSymbolicLink()) fail('Symlink paths are forbidden');
    if (current !== file && !stat.isDirectory()) fail('Parent must be a directory');
  }
  const stat = await fs.lstat(file);
  if (directory ? !stat.isDirectory() : !stat.isFile()) fail('Expected regular file or directory');
  if (await fs.realpath(file) !== file) fail('Path is not canonical');
  return stat;
}
async function bytes(file) {
  const before = await safePath(file);
  const handle = await fs.open(file, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const opened = await handle.stat();
    if (!opened.isFile() || opened.dev !== before.dev || opened.ino !== before.ino) fail('File changed during read');
    const raw = await handle.readFile();
    const after = await safePath(file);
    if (after.dev !== opened.dev || after.ino !== opened.ino || after.size !== raw.length ||
        after.mtimeMs !== opened.mtimeMs || after.ctimeMs !== opened.ctimeMs) fail('File changed during read');
    return raw;
  } finally { await handle.close(); }
}
function imageType(raw, file) {
  let ext;
  if (raw.length >= 8 && raw.subarray(0, 8).equals(Buffer.from('89504e470d0a1a0a', 'hex'))) ext = '.png';
  else if (raw.length >= 3 && raw[0] === 255 && raw[1] === 216 && raw[2] === 255) ext = '.jpg';
  else if (raw.length >= 16 && raw.toString('latin1', 0, 4) === 'RIFF' &&
    raw.toString('latin1', 8, 12) === 'WEBP' && ['VP8 ', 'VP8L', 'VP8X'].includes(raw.toString('latin1', 12, 16))) ext = '.webp';
  else fail('Only PNG/JPEG/WebP magic is supported (not a decode or visual-QC check)');
  const suffix = path.extname(file).toLowerCase();
  if (suffix !== ext && !(ext === '.jpg' && suffix === '.jpeg')) fail('Image extension/magic mismatch');
  return ext;
}
function validateReferences(references, maximum) {
  if (!Array.isArray(references)) fail('Explicit ordered references array is required (empty is allowed)');
  if (references.length > maximum) fail('Reference count exceeds structural safety limit, not provider limit');
  const seen = new Set();
  for (const ref of references) {
    keys(ref, ['path', 'sha256', 'role']); absolute(ref.path); hash(ref.sha256); role(ref.role);
    if (seen.has(ref.sha256)) fail('Duplicate reference hash');
    seen.add(ref.sha256);
  }
}
async function image(file, accepted) {
  hash(accepted);
  const raw = await bytes(file);
  if (digest(raw) !== accepted) fail('Reference hash mismatch');
  return { raw, ext: imageType(raw, file) };
}
async function writeNew(file, raw) {
  await safePath(path.dirname(file), true);
  const handle = await fs.open(file, 'wx', 0o600);
  try { await handle.writeFile(raw); await handle.chmod(0o400); await handle.sync(); }
  finally { await handle.close(); }
}
async function privateCopy(file) {
  const stat = await safePath(file);
  if ((stat.mode & 0o777) !== 0o400 || stat.nlink !== 1) fail('Bundle files must remain private read-only single-link copies (0400)');
}
const nameFor = (index, sha, ext) => `ref-${String(index).padStart(2, '0')}-${sha}${ext}`;

export async function prepare({ references: manifestFile, outDir, 'out-dir': cliOutDir, maxReferences = 100 } = {}) {
  const root = absolute(outDir ?? cliOutDir);
  limit(maxReferences); absolute(manifestFile);
  const manifest = decode(await bytes(manifestFile));
  validateReferences(manifest, maxReferences);
  await safePath(path.dirname(root), true);
  // Reserve a NEW private directory. Never clean or overwrite any existing directory.
  await fs.mkdir(root, { mode: 0o700 });
  try {
    await fs.chmod(root, 0o700);
    const refs = [];
    for (const [i, ref] of manifest.entries()) {
      const { raw, ext } = await image(ref.path, ref.sha256);
      const upload_name = nameFor(i + 1, ref.sha256, ext);
      const upload_path = path.join(root, upload_name);
      await writeNew(upload_path, raw);
      refs.push({ index: i + 1, slot: `Image${i + 1}`, source_path: ref.path,
        upload_path, sha256: ref.sha256, role: ref.role, upload_name });
    }
    const exported = refs.map(ref => ({ path: ref.upload_path, sha256: ref.sha256, role: ref.role }));
    const paths = refs.map(ref => ref.upload_path);
    const files = {};
    for (const [key, filename, value] of [['references', 'references.json', exported], ['upload_files', 'upload-files.json', paths]]) {
      const raw = encode(value), file = path.join(root, filename);
      await writeNew(file, raw);
      files[key] = { path: file, sha256: digest(raw) };
    }
    const plan = { schema_version: 1, kind: KIND, structural_max_references: maxReferences, references: refs, files };
    const raw = encode(plan), file = path.join(root, 'plan.json');
    await writeNew(file, raw);
    // Verify source/staged consistency once more before reporting a successful prepare.
    await verify(file, digest(raw));
    return { kind: KIND, plan: file, plan_sha256: digest(raw), files, reference_count: refs.length };
  } catch (error) {
    // Leave only this reserved failed directory for explicit inspection; never recursively delete.
    throw new Error(`Bundle preparation failed; partial directory retained: ${root}. ${error.message}`, { cause: error });
  }
}

export async function verify(planFile, acceptedHash) {
  absolute(planFile); hash(acceptedHash);
  const root = path.dirname(planFile);
  if (path.basename(planFile) !== 'plan.json') fail('Expected plan.json');
  const rootStat = await safePath(root, true);
  if ((rootStat.mode & 0o777) !== 0o700) fail('Bundle directory must remain private (0700)');
  const raw = await bytes(planFile);
  if (digest(raw) !== acceptedHash) fail('Plan hash mismatch');
  const plan = decode(raw);
  keys(plan, ['schema_version', 'kind', 'structural_max_references', 'references', 'files']);
  if (plan.schema_version !== 1 || plan.kind !== KIND) fail('Invalid plan schema/kind');
  limit(plan.structural_max_references);
  if (!Array.isArray(plan.references)) fail('Explicit references required');
  if (plan.references.length > plan.structural_max_references) fail('Reference count exceeds structural safety limit');
  const exported = [], paths = [];
  for (const [i, ref] of plan.references.entries()) {
    keys(ref, ['index', 'slot', 'source_path', 'upload_path', 'sha256', 'role', 'upload_name']);
    absolute(ref.source_path); absolute(ref.upload_path); hash(ref.sha256); role(ref.role);
    if (ref.index !== i + 1 || ref.slot !== `Image${i + 1}`) fail('Reference slot/order mismatch');
    const { ext } = await image(ref.source_path, ref.sha256);
    const expected = nameFor(i + 1, ref.sha256, ext);
    if (ref.upload_name !== expected || ref.upload_path !== path.join(root, expected)) fail('Upload path/name containment mismatch');
    const sourceRelative = path.relative(root, ref.source_path);
    if (sourceRelative === '' || (!sourceRelative.startsWith(`..${path.sep}`) && sourceRelative !== '..' && !path.isAbsolute(sourceRelative))) fail('Source must be outside new bundle');
    await image(ref.upload_path, ref.sha256);
    await privateCopy(ref.upload_path);
    exported.push({ path: ref.upload_path, sha256: ref.sha256, role: ref.role });
    paths.push(ref.upload_path);
  }
  validateReferences(exported, plan.structural_max_references);
  keys(plan.files, ['references', 'upload_files']);
  for (const [key, filename, expected] of [['references', 'references.json', exported], ['upload_files', 'upload-files.json', paths]]) {
    const child = plan.files[key];
    keys(child, ['path', 'sha256']); hash(child.sha256);
    if (child.path !== path.join(root, filename)) fail('Child path containment mismatch');
    const childRaw = await bytes(child.path);
    if (digest(childRaw) !== child.sha256) fail('Child hash mismatch');
    if (!isDeepStrictEqual(decode(childRaw), expected)) fail('Child ordered array mismatch');
    await privateCopy(child.path);
  }
  await privateCopy(planFile);
  return paths; // Only verify returns the ordered chooser paths; this is NOT upload evidence.
}

const USAGE = 'prepare --references ABS_MANIFEST_JSON --out-dir NEW_ABS_DIR [--max-references 0..100] | verify ABS_PLAN --sha256 ACCEPTED_PLAN_SHA256';
export async function main(argv = process.argv.slice(2)) {
  const [command, ...args] = argv;
  if (!['prepare', 'verify'].includes(command)) fail(USAGE);
  const allowed = command === 'prepare' ? ['references', 'out-dir', 'max-references'] : ['sha256'];
  const options = Object.create(null), positional = [];
  for (let i = 0; i < args.length; i++) {
    if (!args[i].startsWith('--')) { positional.push(args[i]); continue; }
    const key = args[i].slice(2);
    if (!allowed.includes(key) || Object.hasOwn(options, key) || !args[i + 1] || args[i + 1].startsWith('--')) fail('Invalid/duplicate CLI option');
    options[key] = args[++i];
  }
  if (command === 'verify') {
    if (positional.length !== 1 || !options.sha256) fail(USAGE);
    return verify(positional[0], options.sha256);
  }
  if (positional.length || !options.references || !options['out-dir']) fail(USAGE);
  if (options['max-references'] !== undefined && !/^(?:0|[1-9][0-9]*)$/.test(options['max-references'])) fail('Invalid structural max');
  return prepare({ references: options.references, outDir: options['out-dir'],
    maxReferences: options['max-references'] === undefined ? 100 : Number(options['max-references']) });
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().then(result => console.log(JSON.stringify(result, null, 2))).catch(error => { console.error(error.message); process.exitCode = 1; });
}
