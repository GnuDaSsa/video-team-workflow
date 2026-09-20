#!/usr/bin/env node
// Local cache, NOT cryptographic provider attestation. upload_binding is executor attestation only.
// Always freshly search the observed workspace and verify asset identity before selection; never auto-upload.
// registryDir / --registry-dir is for isolated tests only. Never clear/switch registries to bypass history.
// No source paths are persisted. download_hash checks independent local bytes, not their remote provenance.
import fs from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
export const DEFAULT_REGISTRY_DIR = fileURLToPath(new URL('../../../../video-team/runway-assets', import.meta.url));
const fail = message => { throw new Error(message); };
const digest = value => createHash('sha256').update(value).digest('hex');
const guards = { browser_reverification_required: true, upload_authorized: false };
const fields = ['scope', 'sha256', 'asset_name', 'asset_id', 'source_url', 'evidence_kind', 'observed_at', 'timestamp'];
function exact(value, names) {
  if (!value || Array.isArray(value) || typeof value !== 'object' || Object.keys(value).sort().join('|') !== [...names].sort().join('|')) fail('Invalid fields');
}
function text(value, max) {
  if (typeof value !== 'string' || !value.trim() || value.length > max || /[\x00-\x1f\x7f]/.test(value)) fail('Invalid string');
}
function absolute(value) {
  text(value, 4096);
  if (!path.isAbsolute(value) || value.includes('\\') || path.resolve(value) !== value) fail('Unsafe absolute path');
  return value;
}
function scopeCheck(value) { if (typeof value !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}$/.test(value)) fail('Invalid team slug'); }
function iso(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$/.test(value) || !Number.isFinite(Date.parse(value))) fail('Invalid ISO timestamp');
  const [year, month, day] = value.substring(0, 10).split('-').map(Number);
  if (month < 1 || month > 12 || day < 1 || day > new Date(Date.UTC(year, month, 0)).getUTCDate() || Number(value.substring(11, 13)) > 23) fail('Invalid ISO date');
}
function binding(value) {
  if (!['upload_binding', 'download_hash'].includes(value.kind)) fail('Unsupported evidence kind');
  if (typeof value.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(value.sha256)) fail('Invalid SHA256');
  text(value.asset_name, 1024); if (value.asset_id !== null) text(value.asset_id, 256);
  iso(value.observed_at); text(value.source_url, 4096);
  const url = new URL(value.source_url);
  if (!value.source_url.startsWith('https://app.runwayml.com/') || url.origin !== 'https://app.runwayml.com' || url.username || url.password || value.source_url.includes('\\')) fail('Invalid observed Runway URL');
}
async function safePath(file, directory = false, create = false) {
  absolute(file); let current = path.parse(file).root, stat;
  for (const part of path.relative(current, file).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    if (create) { try { await fs.mkdir(current, { mode: 0o700 }); } catch (e) { if (e.code !== 'EEXIST') throw e; } }
    stat = await fs.lstat(current);
    if (stat.isSymbolicLink() || ((current !== file || directory) && !stat.isDirectory())) fail('Unsafe or symlink path');
  }
  stat ??= await fs.lstat(file);
  if ((!directory && !stat.isFile()) || await fs.realpath(file) !== file) fail('Invalid file path');
  if (directory && (stat.uid !== process.getuid() || (stat.mode & 0o777) !== 0o700)) fail('Registry must be owned and private (0700)');
  return stat;
}
async function read(file, json = false, privateRecord = false) {
  const before = await safePath(file), handle = await fs.open(file, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const opened = await handle.stat(), hash = createHash('sha256'), chunks = []; let size = 0;
    if (!opened.isFile() || opened.dev !== before.dev || opened.ino !== before.ino) fail('File changed');
    if (privateRecord && (opened.uid !== process.getuid() || opened.nlink !== 1 || (opened.mode & 0o777) !== 0o600)) fail('Unsafe registry record');
    if (json && opened.size > 16384) fail('Metadata too large');
    for await (const chunk of handle.createReadStream({ autoClose: false })) {
      size += chunk.length; if (json && size > 16384) fail('Metadata too large');
      hash.update(chunk); if (json) chunks.push(chunk);
    }
    const after = await safePath(file);
    if (after.dev !== opened.dev || after.ino !== opened.ino || after.size !== size || after.mtimeMs !== opened.mtimeMs || after.ctimeMs !== opened.ctimeMs) fail('File changed');
    return { sha256: hash.digest('hex'), stat: opened, value: json ? JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(chunks))) : null };
  } finally { await handle.close(); }
}
const recordPath = (dir, scope, sha) => path.join(dir, `${digest(JSON.stringify([scope, sha]))}.json`);
async function existing(dir, scope, sha256) {
  let value;
  try { await safePath(dir, true); value = (await read(recordPath(dir, scope, sha256), true, true)).value; }
  catch (e) { if (e.code === 'ENOENT') return null; throw e; }
  exact(value, fields); scopeCheck(value.scope); iso(value.timestamp);
  binding({ ...value, kind: value.evidence_kind });
  if (value.scope !== scope || value.sha256 !== sha256 || !new URL(value.source_url).pathname.startsWith(`/video-tools/teams/${scope}/`)) fail('Corrupt record identity');
  return value;
}
const summary = (status, value) => ({ status, ...value, ...guards });
export async function lookup({ scope, file, registryDir = DEFAULT_REGISTRY_DIR } = {}) {
  scopeCheck(scope); absolute(registryDir); const { sha256 } = await read(file);
  const found = await existing(registryDir, scope, sha256);
  return summary(found ? 'REGISTERED' : 'NOT_REGISTERED', found ?? { scope, sha256, asset_name: null, asset_id: null, source_url: null, evidence_kind: null, observed_at: null, timestamp: null });
}
export async function record({ scope, file, assetName, assetId = null, evidence, downloadedFile, registryDir = DEFAULT_REGISTRY_DIR } = {}) {
  scopeCheck(scope); absolute(registryDir); text(assetName, 1024); if (assetId !== null) text(assetId, 256);
  const source = await read(file), ev = (await read(evidence, true)).value;
  exact(ev, ['kind', 'observed_at', 'source_url', 'sha256', 'asset_name', 'asset_id']); binding(ev);
  if (!new URL(ev.source_url).pathname.startsWith(`/video-tools/teams/${scope}/`)) fail('Evidence workspace mismatch');
  if (ev.sha256 !== source.sha256 || ev.asset_name !== assetName || ev.asset_id !== assetId) fail('Evidence binding mismatch');
  if (ev.kind === 'download_hash') {
    if (!downloadedFile) fail('download_hash requires downloaded-file');
    const downloaded = await read(downloadedFile);
    if (downloaded.stat.dev === source.stat.dev && downloaded.stat.ino === source.stat.ino) fail('Independent downloaded file required');
    if (downloaded.sha256 !== source.sha256) fail('Downloaded hash mismatch');
  } else if (downloadedFile !== undefined) fail('downloaded-file requires download_hash evidence');
  await safePath(registryDir, true, true);
  const result = previous => summary(previous.asset_name === assetName && previous.asset_id === assetId ? 'ALREADY_REGISTERED' : 'CONFLICT', previous);
  const previous = await existing(registryDir, scope, source.sha256); if (previous) return result(previous);
  const value = { scope, sha256: source.sha256, asset_name: assetName, asset_id: assetId, source_url: ev.source_url, evidence_kind: ev.kind, observed_at: ev.observed_at, timestamp: new Date().toISOString() };
  let handle;
  try { handle = await fs.open(recordPath(registryDir, scope, source.sha256), 'wx', 0o600); }
  catch (e) { if (e.code !== 'EEXIST') throw e; const raced = await existing(registryDir, scope, source.sha256); if (!raced) fail('Record disappeared'); return result(raced); }
  // Never unlink, replace, or repair a record, even after interrupted writes: corruption fails closed.
  try { await handle.chmod(0o600); await handle.writeFile(`${JSON.stringify(value)}\n`); await handle.sync(); }
  finally { await handle.close(); }
  return summary('REGISTERED', value);
}
export async function main(args) {
  const [command, ...rest] = args, options = {}, names = { '--scope': 'scope', '--file': 'file', '--registry-dir': 'registryDir', '--asset-name': 'assetName', '--asset-id': 'assetId', '--evidence': 'evidence', '--downloaded-file': 'downloadedFile' };
  if (!['lookup', 'record'].includes(command)) fail('Expected lookup or record');
  for (let i = 0; i < rest.length; i += 2) {
    const key = names[rest[i]], value = rest[i + 1];
    if (!key || Object.hasOwn(options, key) || !value || value.startsWith('--') || (command === 'lookup' && !['scope', 'file', 'registryDir'].includes(key))) fail('Invalid CLI arguments');
    options[key] = value;
  }
  return command === 'lookup' ? lookup(options) : record(options);
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { const value = await main(process.argv.slice(2)); console.log(JSON.stringify(value)); if (value.status === 'CONFLICT') process.exitCode = 2; }
  catch (e) { console.log(JSON.stringify({ status: 'ERROR', error: e.code ?? e.message, ...guards })); process.exitCode = 1; }
}
