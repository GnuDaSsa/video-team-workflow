#!/usr/bin/env node
// Text-only advisory runner. No media, job, prompt, harness or paid-retry actions.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { classify, status, MODEL, buildRequest, validateInput, validateResponse } from './jev-qc.mjs';

export const DEFAULT_KEY_FILE = fileURLToPath(new URL('../../../../secrets/typesafe-video-team.key', import.meta.url));
export const QUESTION_VERSION = 'jev-qc-1';
export const REASONS = Object.freeze(['mixed_findings', 'repeated_failure', 'uncertain_category']);
const hash = value => crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
const fail = code => { throw Object.assign(new Error(code), { safeCode: code }); };
const summary = (status, extra = {}) => ({ status, ...extra, advisory: true, execution_authorized: false });
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const hex = value => typeof value === 'string' && /^[0-9a-f]{64}$/.test(value);
const idPattern = /^\d{13}-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
function readJSON(file, code, max = 65536) {
  let fd;
  try {
    fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
    const stat = fs.fstatSync(fd);
    if (!stat.isFile() || stat.size > max) fail(code);
    const bytes = Buffer.alloc(max + 1);
    let used = 0, n;
    while (used <= max && (n = fs.readSync(fd, bytes, used, max + 1 - used, null))) used += n;
    if (used > max) fail(code);
    return JSON.parse(bytes.subarray(0, used).toString('utf8'));
  } catch { fail(code); } finally { if (fd !== undefined) fs.closeSync(fd); }
}
function exists(file) {
  try { fs.lstatSync(file); return true; } catch (e) { if (e.code === 'ENOENT') return false; throw e; }
}
function writeNew(file, value) {
  const fd = fs.openSync(file, 'wx', 0o600);
  try { fs.writeFileSync(fd, JSON.stringify(value) + '\n'); fs.fsyncSync(fd); }
  finally { fs.closeSync(fd); }
}
function syncDirectory(dir) {
  const fd = fs.openSync(dir, 'r');
  try { fs.fsyncSync(fd); } finally { fs.closeSync(fd); }
}
function saveLedger(dir, ledger) {
  const temp = path.join(dir, '.ledger-' + crypto.randomUUID());
  try {
    writeNew(temp, ledger);
    fs.renameSync(temp, path.join(dir, 'ledger.json'));
    syncDirectory(dir);
  } finally { if (exists(temp)) fs.unlinkSync(temp); }
}
function loadLedger(dir) {
  const file = path.join(dir, 'ledger.json');
  if (!exists(file)) {
    if (fs.readdirSync(dir).some(name => name !== 'lock')) fail('CORRUPT_LEDGER');
    return { schema_version: 1, attempts: [] };
  }
  const ledger = readJSON(file, 'CORRUPT_LEDGER');
  if (!object(ledger) || Object.keys(ledger).length !== 2 || ledger.schema_version !== 1 ||
      !Array.isArray(ledger.attempts) || ledger.attempts.length > 5) fail('CORRUPT_LEDGER');
  const ids = new Set();
  for (const a of ledger.attempts) {
    if (!object(a) || Object.keys(a).length !== 4 || !idPattern.test(a.id) ||
        !hex(a.input_sha256) || !hex(a.cache_key) || ids.has(a.id) ||
        !['RESERVED', 'CLASSIFIED', 'UNAVAILABLE'].includes(a.status)) fail('CORRUPT_LEDGER');
    ids.add(a.id);
  }
  const allowed = new Set(['ledger.json', 'lock', ...[...ids].map(id => id + '.json')]);
  if (fs.readdirSync(dir).some(name => !allowed.has(name))) fail('CORRUPT_LEDGER');
  return ledger;
}
function validateRecord(record, attempt, state) {
  if (!object(record) || record.schema_version !== 1 || record.question_version !== QUESTION_VERSION ||
      record.input_sha256 !== attempt.input_sha256 || record.model_requested !== MODEL ||
      record.advisory !== true || record.execution_authorized !== false ||
      record.visual_qc !== 'NOT_ASSESSED_BY_JEV' || !['CLASSIFIED', 'UNAVAILABLE'].includes(record.status)) fail('INVALID_RECORD');
  if (record.status === 'CLASSIFIED') {
    try { validateResponse({ model: record.model_actual, answers: record.answers, usage: record.usage }, buildRequest(state)); }
    catch { fail('INVALID_RECORD'); }
  } else if (record.model_actual !== null || record.answers !== null || record.usage !== null) fail('INVALID_RECORD');
  return record;
}
function classified(record, file, cached) {
  return summary(cached ? 'CACHED' : 'CLASSIFIED', {
    path: file, category: record.answers.category.choice, confidence: record.answers.category.confidence
  });
}
export async function run(options, deps = {}) {
  if (!REASONS.includes(options.reason)) fail('INVALID_REASON');
  let root, state;
  try {
    if (!fs.lstatSync(options.root).isDirectory()) fail('INVALID_ROOT');
    root = fs.realpathSync(options.root);
  } catch { fail('INVALID_ROOT'); }
  try { state = validateInput(readJSON(options.input, 'INVALID_INPUT')); }
  catch { fail('INVALID_INPUT'); }
  const dir = path.join(root, '.jev');
  try {
    if (!exists(dir)) fs.mkdirSync(dir, { mode: 0o700 });
    const stat = fs.lstatSync(dir);
    if (!stat.isDirectory() || (stat.mode & 0o7777) !== 0o700 || stat.uid !== process.getuid()) fail('INVALID_STATE_DIR');
  } catch { fail('INVALID_STATE_DIR'); }
  const lock = path.join(dir, 'lock');
  let fd;
  try { fd = fs.openSync(lock, 'wx', 0o600); }
  catch { fail('LOCKED_OR_UNWRITABLE'); }
  const lockStat = fs.fstatSync(fd);
  let staged;
  try {
    const ledger = loadLedger(dir);
    const input_sha256 = hash(state);
    const keyFor = sha => hash({ model: MODEL, question_version: QUESTION_VERSION, questions: buildRequest(state).questions, input_sha256: sha });
    const cache_key = keyFor(input_sha256);
    for (const a of ledger.attempts) {
      if (a.cache_key !== keyFor(a.input_sha256)) fail('CORRUPT_LEDGER');
      const file = path.join(dir, a.id + '.json');
      if (!exists(file)) {
        if (a.status === 'CLASSIFIED') fail('INVALID_RECORD');
        continue; // Reserved/failed attempts count even without a result.
      }
      const record = validateRecord(readJSON(file, 'INVALID_RECORD'), a, state);
      if (a.status !== 'RESERVED' && a.status !== record.status) fail('INVALID_RECORD');
      if (a.cache_key === cache_key && a.input_sha256 === input_sha256 && record.status === 'CLASSIFIED') return classified(record, file, true);
    }
    if (ledger.attempts.length >= 5) return summary('LIMIT_REACHED');
    const keyFile = options.keyFile ?? DEFAULT_KEY_FILE;
    const metadata = await (deps.status ?? status)({ keyFile });
    if (metadata?.key_present !== true) return summary('SKIPPED_NO_KEY');
    const id = Date.now() + '-' + crypto.randomUUID();
    const attempt = { id, input_sha256, cache_key, status: 'RESERVED' };
    staged = path.join(dir, '.input-' + id + '.json');
    writeNew(staged, state); // Stable validated input, never reread a mutable caller file in the classifier.
    ledger.attempts.push(attempt);
    saveLedger(dir, ledger); // Durable reservation BEFORE any possible API attempt; never refund or retry.
    const out = path.join(dir, id + '.json');
    let record;
    try {
      await (deps.classify ?? classify)({ input: staged, out, keyFile });
      record = validateRecord(readJSON(out, 'INVALID_RECORD'), attempt, state);
    } catch {
      attempt.status = 'UNAVAILABLE';
      saveLedger(dir, ledger);
      return summary('UNAVAILABLE', exists(out) ? { path: out } : {});
    }
    attempt.status = record.status;
    saveLedger(dir, ledger);
    return record.status === 'CLASSIFIED' ? classified(record, out, false) : summary('UNAVAILABLE', { path: out });
  } finally {
    try { if (staged && exists(staged)) fs.unlinkSync(staged); }
    finally {
      fs.closeSync(fd);
      // Never delete a replacement or someone else's lock.
      if (exists(lock)) {
        const current = fs.lstatSync(lock);
        if (current.ino === lockStat.ino && current.dev === lockStat.dev && !current.isSymbolicLink()) fs.unlinkSync(lock);
      }
    }
  }
}
export async function main(args, deps = {}) {
  try {
    const [command, ...rest] = args;
    if (!['status', 'classify'].includes(command)) fail('INVALID_ARGUMENTS');
    const allowed = command === 'status' ? ['--key-file'] : ['--root', '--input', '--reason', '--key-file'];
    const options = {};
    for (let i = 0; i < rest.length; i += 2) {
      if (!allowed.includes(rest[i]) || Object.hasOwn(options, rest[i]) || !rest[i + 1] || rest[i + 1].startsWith('--')) fail('INVALID_ARGUMENTS');
      options[rest[i]] = rest[i + 1];
    }
    const keyFile = options['--key-file'] ?? DEFAULT_KEY_FILE;
    if (command === 'status') {
      const metadata = await (deps.status ?? status)({ keyFile });
      return { code: 0, result: summary('METADATA_ONLY', { key_present: metadata?.key_present === true }) };
    }
    if (!options['--root'] || !options['--input'] || !options['--reason']) fail('INVALID_ARGUMENTS');
    const result = await run({ root: options['--root'], input: options['--input'], reason: options['--reason'], keyFile }, deps);
    return { code: result.status === 'UNAVAILABLE' ? 1 : 0, result };
  } catch (error) {
    const codes = ['INVALID_ARGUMENTS', 'INVALID_REASON', 'INVALID_ROOT', 'INVALID_INPUT', 'INVALID_STATE_DIR', 'LOCKED_OR_UNWRITABLE', 'CORRUPT_LEDGER', 'INVALID_RECORD'];
    return { code: 2, result: summary(codes.includes(error?.safeCode) ? error.safeCode : 'LOCAL_ERROR') };
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { code, result } = await main(process.argv.slice(2));
  console.log(JSON.stringify(result)); process.exitCode = code;
}
