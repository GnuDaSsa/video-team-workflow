#!/usr/bin/env node
// File-only handoff gate. No provider calls, browser actions, spawning, or generation.
// "Immutable" means exclusive creation plus independently accepted byte hashes,
// not filesystem write protection or cryptographic provider attestation.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { verify as verifyReceipt, sha256 } from './harness.mjs';
import { validateLanguageContract, validatePromptLanguage, LANGUAGE_STATUS } from './prompt-language.mjs';

export const PROVIDERS = Object.freeze({
  image_prompt: 'chatgpt_web', music_prompt: 'suno_web', seedance_prompt: 'runway_web',
});
const AUTHOR = 'gpt-6-astra';
const STATE = 'READY_FOR_PROVIDER_INPUT';
const fail = message => { throw new Error(message); };
function absolute(value, label) {
  if (typeof value !== 'string' || !path.isAbsolute(value)) fail(`${label} must be absolute`);
  return value;
}
function hash(value, label) {
  if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) fail(`An independently accepted ${label} SHA256 is required`);
  return value;
}
function stageProvider(stage) {
  if (!Object.hasOwn(PROVIDERS, stage)) fail('Unsupported author stage');
  return PROVIDERS[stage];
}
function keys(value, expected, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      !isDeepStrictEqual(Object.keys(value).sort(), [...expected].sort())) fail(`Invalid ${label} metadata`);
}
async function bytes(file) {
  const handle = await fs.open(file, 'r');
  try {
    if (!(await handle.stat()).isFile()) fail(`Expected a regular file: ${file}`);
    return await handle.readFile();
  } finally { await handle.close(); }
}
function json(raw) { return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(raw)); }
async function boundReceipt(receiptFile, acceptedHash, expectedStage) {
  absolute(receiptFile, 'Receipt path');
  hash(acceptedHash, 'receipt');
  stageProvider(expectedStage);
  const checked = await verifyReceipt(receiptFile, acceptedHash);
  const raw = await bytes(receiptFile);
  if (sha256(raw) !== acceptedHash) fail('Receipt hash mismatch');
  const receipt = json(raw);
  if (receipt.stage !== expectedStage || checked.stage !== expectedStage) fail('Receipt stage mismatch');
  if (checked.author_record?.model !== AUTHOR) fail('Author model mismatch');
  // Re-read the complete prompt, rather than accepting a caller-supplied excerpt.
  const root = await fs.realpath(receipt.root);
  const promptFile = await fs.realpath(path.resolve(receipt.root, receipt.prompt.path));
  const relative = path.relative(root, promptFile);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) fail('Prompt escapes receipt root');
  const promptBytes = await bytes(promptFile);
  if (sha256(promptBytes) !== receipt.prompt.sha256 || receipt.prompt.sha256 !== checked.prompt.sha256) fail('Prompt hash mismatch');
  // Preserve even a UTF-8 BOM so encoding the provider text reproduces bound bytes.
  const prompt = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(promptBytes);
  if (!prompt.trim() || prompt !== prompt.normalize('NFC') || sha256(Buffer.from(prompt, 'utf8')) !== receipt.prompt.sha256) fail('Invalid full prompt encoding');
  return { receipt, checked, prompt };
}
async function checkReferences(references) {
  if (!Array.isArray(references)) fail('References must be an ordered array');
  const bound = [];
  for (const reference of references) {
    keys(reference, ['path', 'sha256', 'role'], 'reference');
    absolute(reference.path, 'Reference path');
    hash(reference.sha256, 'reference');
    if (typeof reference.role !== 'string' || !reference.role.trim()) fail('Reference role must be nonempty');
    if (sha256(await bytes(reference.path)) !== reference.sha256) fail(`Reference hash mismatch: ${reference.path}`);
    bound.push({ path: reference.path, sha256: reference.sha256, role: reference.role });
  }
  return bound;
}
export async function prepare({ stage, receipt: receiptFile, sha256: acceptedHash, out, references: referencesFile }) {
  const provider = stageProvider(stage);
  absolute(out, 'Output path');
  const { receipt, checked, prompt } = await boundReceipt(receiptFile, acceptedHash, stage);
  if (checked.language_status === LANGUAGE_STATUS.LEGACY) fail('LEGACY_UNSPECIFIED_READ_ONLY');
  if (stage !== 'music_prompt' && checked.knowledge_status !== 'CURRENT_KNOWLEDGE_VALIDATED') fail('LEGACY_KNOWLEDGE_UNSPECIFIED_READ_ONLY');
  validateLanguageContract(receipt.language_contract);
  validatePromptLanguage(prompt, receipt.language_contract);
  if (referencesFile !== undefined && (typeof referencesFile !== 'string' || !referencesFile)) fail('References JSON path must be nonempty');
  const references = await checkReferences(referencesFile === undefined ? [] : json(await bytes(referencesFile)));
  const payload = {
    schema_version: 2, kind: 'astra_provider_payload', stage, required_author: AUTHOR,
    provider, language_contract: receipt.language_contract, knowledge_sha256: checked.knowledge_sha256, prompt, prompt_sha256: receipt.prompt.sha256,
    author_session_id: receipt.session_id, author_record: checked.author_record,
    receipt: { path: receiptFile, sha256: acceptedHash }, references,
    created_at: new Date().toISOString(), state: STATE,
  };
  const output = Buffer.from(`${JSON.stringify(payload, null, 2)}\n`, 'utf8');
  // Never truncate/replace any existing file, including a symlink.
  const handle = await fs.open(out, 'wx', 0o600);
  try {
    await handle.chmod(0o600);
    await handle.writeFile(output);
    await handle.sync();
  } finally { await handle.close(); }
  return { state: STATE, file: out, file_sha256: sha256(output), payload_sha256: sha256(output), stage, provider };
}
export async function verify(payloadFile, acceptedHash) {
  absolute(payloadFile, 'Payload path');
  hash(acceptedHash, 'payload');
  const raw = await bytes(payloadFile);
  if (sha256(raw) !== acceptedHash) fail('Payload hash mismatch');
  const payload = json(raw);
  const legacy = payload.schema_version === 1;
  const expected = legacy ? ['schema_version', 'kind', 'stage', 'required_author', 'provider', 'prompt', 'prompt_sha256', 'author_session_id', 'author_record', 'receipt', 'references', 'created_at', 'state'] : ['schema_version', 'kind', 'stage', 'required_author', 'provider', 'language_contract', 'prompt', 'prompt_sha256', 'author_session_id', 'author_record', 'receipt', 'references', 'created_at', 'state'];
  if (Object.hasOwn(payload, 'knowledge_sha256')) expected.push('knowledge_sha256');
  keys(payload, expected, 'payload');
  if (![1, 2].includes(payload.schema_version) || payload.kind !== 'astra_provider_payload' ||
      payload.required_author !== AUTHOR || payload.provider !== stageProvider(payload.stage) || payload.state !== STATE) fail('Invalid payload stage/provider/author/state');
  if (!legacy) validateLanguageContract(payload.language_contract);
  if (typeof payload.created_at !== 'string' || !Number.isFinite(Date.parse(payload.created_at)) ||
      new Date(payload.created_at).toISOString() !== payload.created_at) fail('Invalid payload created_at');
  keys(payload.receipt, ['path', 'sha256'], 'receipt');
  const { receipt, checked, prompt } = await boundReceipt(payload.receipt.path, payload.receipt.sha256, payload.stage);
  if ((payload.knowledge_sha256 ?? null) !== checked.knowledge_sha256) fail('Payload knowledge binding mismatch');
  if (legacy) {
    if (checked.language_status !== LANGUAGE_STATUS.LEGACY) fail('Payload/receipt language schema mismatch');
  } else {
    if (checked.language_status !== LANGUAGE_STATUS.CURRENT || JSON.stringify(payload.language_contract) !== JSON.stringify(receipt.language_contract)) fail('Language contract binding mismatch');
    validatePromptLanguage(prompt, payload.language_contract);
  }
  if (typeof payload.prompt !== 'string' || payload.prompt !== prompt ||
      payload.prompt_sha256 !== receipt.prompt.sha256 || sha256(Buffer.from(payload.prompt, 'utf8')) !== payload.prompt_sha256) fail('Payload full prompt binding mismatch');
  if (payload.author_session_id !== receipt.session_id || !isDeepStrictEqual(payload.author_record, checked.author_record)) fail('Payload author metadata mismatch');
  await checkReferences(payload.references);
  return { state: STATE, file: payloadFile, payload_sha256: acceptedHash, stage: payload.stage, provider: payload.provider, language_status: legacy ? LANGUAGE_STATUS.LEGACY : LANGUAGE_STATUS.CURRENT, knowledge_status: checked.knowledge_status, knowledge_sha256: checked.knowledge_sha256, payload };
}
const USAGE = 'Usage: prepare --stage image_prompt|music_prompt|seedance_prompt --receipt ABS --sha256 ACCEPTED_RECEIPT_SHA256 --out ABS [--references JSON_FILE] | verify ABS_PAYLOAD --sha256 ACCEPTED_PAYLOAD_SHA256 [--full]';
function parseCli(argv) {
  const [command, ...args] = argv;
  if (!['prepare', 'verify'].includes(command)) fail(USAGE);
  const allowed = command === 'prepare' ? ['stage', 'receipt', 'sha256', 'out', 'references'] : ['sha256'];
  const options = Object.create(null), positional = [];
  let full = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--full') { if (full) fail('Repeated --full'); full = true; continue; }
    if (!args[i].startsWith('-')) { positional.push(args[i]); continue; }
    const name = args[i].slice(2);
    if (!args[i].startsWith('--') || !allowed.includes(name) || Object.hasOwn(options, name) || !args[i + 1] || args[i + 1].startsWith('-')) fail(`Invalid option: ${args[i]}. ${USAGE}`);
    options[name] = args[++i];
  }
  if (positional.length !== (command === 'verify' ? 1 : 0)) fail(USAGE);
  for (const name of allowed.filter(name => name !== 'references')) if (!options[name]) fail(`Missing --${name}. ${USAGE}`);
  return { command, options, positional, full };
}
async function runCli({ command, options, positional }) {
  return command === 'prepare' ? prepare(options) : verify(positional[0], options.sha256);
}
// Keep the full payload available to trusted JS adapters and existing callers.
export async function main(argv = process.argv.slice(2)) { return runCli(parseCli(argv)); }
async function cliSummary(result) {
  const payload = result.payload ?? json(await bytes(result.file));
  const receipt = json(await bytes(payload.receipt.path));
  const request = json(await bytes(path.resolve(receipt.root, receipt.request)));
  return {
    state: result.state, file: result.file, file_sha256: result.file_sha256,
    payload_sha256: result.payload_sha256, receipt_sha256: payload.receipt.sha256,
    stage: result.stage, provider: result.provider,
    author_model: payload.author_record.model, author_session_id: payload.author_session_id,
    author_record: payload.author_record, route: request.route,
    language_status: result.language_status ?? LANGUAGE_STATUS.CURRENT,
    language: payload.language_contract?.language ?? null,
    knowledge_status: result.knowledge_status ?? (request.knowledge ? 'CURRENT_KNOWLEDGE_VALIDATED' : 'NOT_APPLICABLE'),
    knowledge_sha256: payload.knowledge_sha256 ?? null,
    knowledge: request.knowledge ? { selected_ids: request.knowledge.selected_ids, source_mode: request.knowledge.source.mode } : null,
    prompt: { path: receipt.prompt.path, sha256: payload.prompt_sha256, bytes: Buffer.byteLength(payload.prompt, 'utf8'), characters: payload.prompt.length },
    references_count: payload.references.length,
  };
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  (async () => {
    const parsed = parseCli(process.argv.slice(2));
    const result = await runCli(parsed);
    console.log(JSON.stringify(parsed.full ? result : await cliSummary(result), null, parsed.full ? 2 : undefined));
  })().catch(error => { console.error(error.message); process.exitCode = 1; });
}
