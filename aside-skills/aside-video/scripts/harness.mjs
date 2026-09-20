#!/usr/bin/env node
// No model calls, browser calls, process spawning, or settings writes.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { VIDEO_MODE_LOCK } from './mode-lock.mjs';
import { createLanguageContract, validateLanguageContract, validatePromptLanguage, LANGUAGE_STATUS } from './prompt-language.mjs';

export const DEFAULT_POLICY = Object.freeze({
  schema_version: 1, author_model: 'gpt-6-astra',
  author_stages: ['music_prompt', 'image_prompt', 'seedance_prompt'],
  executor_stages: ['brief', 'planning', 'storyboard', 'computer_use', 'music_generate', 'image_generate', 'seedance_generate', 'download', 'image_qc', 'video_qc', 'audio_qc', 'edit', 'package'],
  execution_model: 'inherit_session', author_effort: 'inherit_author_session',
  preferred_author_effort: 'xhigh', image_provider: 'chatgpt_web', image_product: 'ChatGPT Images 2.5',
});
const POLICY_FILE = new URL('../references/harness-policy.json', import.meta.url);
export const LIMITATIONS = 'Machine file/provenance check only. A planned route is not evidence of execution. Checks do not prove quality, thinking effort, semantic authorship, or authenticity of locally editable transcripts. Evidence binds generated assistant text (including ongoing commentary) or an explicit prompt hash; it is not cryptographic provider attestation.';
const BOUNDARY = 'Author: prompt content only for music_prompt, image_prompt, seedance_prompt. No browser/computer use, provider generation, download, QC, editing, packaging, spawning, or model/settings changes. Executor: current session intelligence, always inherit_session; never force Luna or another model.';
const fail = message => { throw new Error(message); };
export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
function policyCheck(p) {
  for (const [key, value] of Object.entries(DEFAULT_POLICY)) {
    if (JSON.stringify(p?.[key]) !== JSON.stringify(value)) fail(`Invalid policy: ${key}`);
  }
  return p;
}
export async function loadPolicy() { return policyCheck(JSON.parse(await fs.readFile(POLICY_FILE, 'utf8'))); }
export function status(policy = DEFAULT_POLICY) {
  policyCheck(policy);
  return { ...policy, prompt_language_default: 'en-US', handoff_schema_version: 2, legacy_language_policy: 'read_only', video_mode_lock: VIDEO_MODE_LOCK, author_effort_required: false, role_boundary: BOUNDARY, limitations: LIMITATIONS };
}
export function route(stage, context = {}, policy = DEFAULT_POLICY) {
  policyCheck(policy);
  const common = { stage, execution_model: 'inherit_session', settings_writes: false, actual_execution_proven: false };
  if (policy.executor_stages.includes(stage)) return { ...common, role: 'executor', mode: 'inherit_session', state: 'PLANNED' };
  if (!policy.author_stages.includes(stage)) fail(`Unknown stage: ${stage}`);
  const author = { ...common, role: 'author', required_model: policy.author_model, effort: policy.author_effort, preferred_effort: policy.preferred_author_effort, effort_required: false };
  if (context.model?.modelId === policy.author_model) return { ...author, mode: 'direct', state: 'PLANNED', planned_model: context.model };
  for (const category of ['standard', 'deep', 'visual', 'fast']) {
    const model = context.modelCategories?.[category];
    if (model?.modelId === policy.author_model) return { ...author, mode: 'functions.subagent', category, planned_model: model, max_tasks: 1, max_minutes: 10, scope: 'prompt_content_only', state: 'PLANNED' };
  }
  return { ...author, mode: 'hold', state: 'HOLD_ASTRA_AUTHOR_REQUIRED' };
}
function relativeName(name) {
  if (typeof name !== 'string' || !name || path.isAbsolute(name) || name.split(/[\\/]/).includes('..')) fail('Expected a within-root relative path');
  return name;
}
function inside(root, target) {
  const rel = path.relative(root, target);
  if (rel === '..' || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) fail(`Path escapes root: ${target}`);
}
async function rootPath(root) {
  if (!root || !path.isAbsolute(root)) fail('Root must be absolute');
  const real = await fs.realpath(root);
  if (!(await fs.stat(real)).isDirectory()) fail('Root must be a directory');
  return real;
}
async function rootFile(root, name, output = false) {
  const absolute = path.resolve(root, name);
  inside(root, absolute);
  // Existing files and all parent symlinks must resolve inside root.
  let real;
  try { real = await fs.realpath(absolute); }
  catch (e) {
    if (!output || e.code !== 'ENOENT') throw e;
    real = path.join(await fs.realpath(path.dirname(absolute)), path.basename(absolute));
  }
  inside(root, real);
  return real;
}
async function textFile(file) {
  const bytes = await fs.readFile(file);
  const text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  if (!text.trim() || text !== text.normalize('NFC')) fail('Prompt must be nonempty NFC UTF-8');
  return { text, hash: sha256(bytes) };
}
async function jsonFile(file) {
  const bytes = await fs.readFile(file);
  return { value: JSON.parse(bytes.toString('utf8')), hash: sha256(bytes) };
}
async function immutable(file, data) {
  const bytes = `${JSON.stringify(data, null, 2)}\n`;
  await fs.writeFile(file, bytes, { flag: 'wx', mode: 0o444 });
  return { ...data, file, file_sha256: sha256(bytes), sha256: sha256(bytes), ...(data.kind === 'astra_author_receipt' ? { receipt_sha256: sha256(bytes) } : {}) };
}
export async function request({ stage, context = {}, root, prompt, out }, policy = DEFAULT_POLICY) {
  const plan = route(stage, context, policy);
  if (plan.role !== 'author') fail('Requests are only for author stages; executors inherit the current session');
  if (plan.state === 'HOLD_ASTRA_AUTHOR_REQUIRED') fail(plan.state);
  const realRoot = await rootPath(root);
  const promptFile = await rootFile(realRoot, relativeName(prompt), true);
  const output = await rootFile(realRoot, relativeName(out), true);
  let initial = null;
  try { initial = await textFile(promptFile); } catch (e) { if (e.code !== 'ENOENT') throw e; }
  if (promptFile === output) fail('Request and prompt paths must differ');
  const language_contract = createLanguageContract(context);
  const data = {
    schema_version: 2, kind: 'astra_author_request', created_at: Date.now(), root: realRoot,
    stage, role: 'author', required_model: policy.author_model, execution_model: 'inherit_session',
    prompt: path.relative(realRoot, promptFile), initial_prompt_sha256: initial?.hash ?? null,
    session_id: context.session_id ?? null, task_id: context.task_id ?? null,
    route: plan, role_boundary: BOUNDARY, language_contract,
    author_task: `${BOUNDARY}\nWrite only the requested ${stage} prompt content, NFC UTF-8. ${language_contract.language === 'en-US' ? 'Use English prose by default.' : `Use ${language_contract.language} only because of the explicit override: ${language_contract.override_reason}.`} Preserve exact user-required dialogue, lyrics, and on-screen literals without translation: ${JSON.stringify(language_contract.preserved_literals)}. No executor translation. Return the exact final prompt as assistant text, or a line Prompt-SHA256: <SHA256 of the final UTF-8 prompt file>. Do not echo this task. The current executor saves the prompt file and seals the receipt. xhigh is preferred, not required; inherit author-session effort. No execution is authorized by this request.`,
    limitations: LIMITATIONS,
  };
  return immutable(output, data);
}
async function checkedRequest(requestFile, policy, { allowLegacy = true } = {}) {
  policyCheck(policy);
  if (!path.isAbsolute(requestFile)) fail('Request path must be absolute');
  const loaded = await jsonFile(requestFile);
  const r = loaded.value;
  const root = await rootPath(r.root);
  await rootFile(root, requestFile);
  if (root !== r.root || ![1, 2].includes(r.schema_version) || r.kind !== 'astra_author_request' || r.role !== 'author' || r.required_model !== policy.author_model || r.execution_model !== 'inherit_session' || !policy.author_stages.includes(r.stage) || !Number.isFinite(r.created_at) || (r.initial_prompt_sha256 !== null && !/^[a-f0-9]{64}$/.test(r.initial_prompt_sha256 ?? ''))) fail('Invalid author request');
  const legacy = r.schema_version === 1;
  if (legacy && !allowLegacy) fail('LEGACY_UNSCOPED_REQUEST_READ_ONLY');
  if (!legacy) validateLanguageContract(r.language_contract);
  if (r.route?.role !== 'author' || r.route?.execution_model !== 'inherit_session' || r.route?.settings_writes !== false || r.route?.actual_execution_proven !== false || r.route?.stage !== r.stage || r.route?.required_model !== policy.author_model || r.route?.planned_model?.modelId !== policy.author_model || !['direct', 'functions.subagent'].includes(r.route?.mode) || r.role_boundary !== BOUNDARY) fail('Invalid request role/route boundary');
  const promptFile = await rootFile(root, relativeName(r.prompt));
  return { ...loaded, root, promptFile, requestFile: await fs.realpath(requestFile), legacy };
}
function assistantText(record) {
  // Only generated text blocks, never user/tool messages, thinking or tool arguments.
  if (!Array.isArray(record.content)) return '';
  return record.content.filter(c => c.type === 'text' && typeof c.text === 'string').map(c => c.text).join('\n');
}
function evidenceMatch(bytes, req, prompt) {
  const lines = bytes.toString('utf8').split('\n');
  for (let i = lines.length - 1; i >= 0; i--) {
    if (!lines[i].trim()) continue;
    let m;
    try { m = JSON.parse(lines[i]); } catch { fail('Malformed messages.jsonl'); }
    if (m.role !== 'assistant' || m.model !== 'gpt-6-astra' || typeof m.provider !== 'string' || !m.provider || typeof m.api !== 'string' || !m.api || typeof m.responseId !== 'string' || !m.responseId || !Number.isFinite(m.usage?.input) || !Number.isFinite(m.usage?.output) || m.usage.output <= 0 || !Number.isFinite(m.timestamp) || m.timestamp <= req.created_at || !['stop', 'end_turn', 'toolUse'].includes(m.stopReason)) continue;
    const text = assistantText(m);
    // Exact whole response or exact fenced payload avoids incidental task quotations.
    const exact = text === prompt.text || text === `\`\`\`\n${prompt.text}\n\`\`\`` || text === `\`\`\`text\n${prompt.text}\n\`\`\``;
    const hash = text.split(/\r?\n/).some(line => line === `Prompt-SHA256: ${prompt.hash}`);
    if (!exact && !hash) continue;
    return { raw_record: lines[i], record_sha256: sha256(lines[i]), line: i + 1, timestamp: m.timestamp, response_id: m.responseId, model: m.model, provider: m.provider, api: m.api, session_id: m.session_id ?? m.sessionId ?? null, task_id: m.task_id ?? m.taskId ?? null, binding: exact ? 'exact_final_prompt' : 'explicit_prompt_sha256' };
  }
  fail('No post-request Astra assistant generation bound to this prompt in messages.jsonl');
}
async function evidenceFile(filename) {
  if (typeof filename !== 'string' || !path.isAbsolute(filename) || path.basename(filename) !== 'messages.jsonl') fail('Evidence must be an absolute messages.jsonl path');
  const real = await fs.realpath(filename);
  if (path.basename(real) !== 'messages.jsonl' || !(await fs.stat(real)).isFile()) fail('Evidence realpath must be a messages.jsonl file');
  return real;
}
function authorSessionId(record, sourcePath) {
  return record.session_id ?? path.basename(path.dirname(sourcePath)).match(/^\d{4}-\d{2}-\d{2}_(.+)$/)?.[1] ?? null;
}
async function mustNotExist(file) {
  try { await fs.lstat(file); } catch (e) { if (e.code === 'ENOENT') return; throw e; }
  fail('EEXIST: immutable output already exists: ' + file);
}
export async function seal({ request: requestFile, evidence, out }, policy = DEFAULT_POLICY) {
  const checked = await checkedRequest(requestFile, policy, { allowLegacy: false });
  const r = checked.value;
  const prompt = await textFile(checked.promptFile);
  validatePromptLanguage(prompt.text, r.language_contract);
  // The source is read-only and may be outside the package root. All writes stay inside.
  const sourcePath = await evidenceFile(evidence);
  const matched = evidenceMatch(await fs.readFile(sourcePath), r, prompt);
  const { raw_record, ...record } = matched;
  const source = { path: sourcePath, line: record.line, record_sha256: record.record_sha256 };
  const output = await rootFile(checked.root, relativeName(out), true);
  const snapshotPath = await rootFile(checked.root, relativeName(out + '.evidence.json'), true);
  await mustNotExist(output);
  await mustNotExist(snapshotPath);
  const saved = await immutable(snapshotPath, {
    schema_version: 1, kind: 'astra_author_evidence_snapshot', source, raw_record,
    limitations: LIMITATIONS,
  });
  return immutable(output, {
    schema_version: 2, kind: 'astra_author_receipt', state: 'READY_FOR_EXECUTION', created_at: Date.now(),
    root: checked.root, stage: r.stage, role: 'author', required_model: policy.author_model,
    execution_model: 'inherit_session', request: path.relative(checked.root, checked.requestFile), request_sha256: checked.hash,
    initial_prompt_sha256: r.initial_prompt_sha256, language_contract: r.language_contract, prompt: { path: r.prompt, sha256: prompt.hash },
    evidence: { path: path.relative(checked.root, snapshotPath), sha256: saved.file_sha256, source },
    author_record: record,
    session_id: authorSessionId(record, sourcePath), task_id: record.task_id ?? null,
    requester_session_id: r.session_id, requester_task_id: r.task_id,
    limitations: LIMITATIONS,
  });
}
export async function verify(receiptFile, acceptedHash, policy = DEFAULT_POLICY) {
  policyCheck(policy);
  if (!/^[a-f0-9]{64}$/.test(acceptedHash ?? '')) fail('An independently accepted receipt SHA256 is required');
  const loaded = await jsonFile(receiptFile);
  if (loaded.hash !== acceptedHash) fail('Receipt hash mismatch');
  const r = loaded.value;
  const root = await rootPath(r.root);
  await rootFile(root, path.resolve(receiptFile));
  if (![1, 2].includes(r.schema_version) || r.kind !== 'astra_author_receipt' || r.state !== 'READY_FOR_EXECUTION' || r.role !== 'author' || r.required_model !== policy.author_model || r.execution_model !== 'inherit_session' || !policy.author_stages.includes(r.stage) || r.limitations !== LIMITATIONS) fail('Invalid receipt role/model/state');
  const legacy = r.schema_version === 1;
  if (!legacy) validateLanguageContract(r.language_contract);
  const reqFile = await rootFile(root, relativeName(r.request));
  const checked = await checkedRequest(reqFile, policy);
  if (legacy !== checked.legacy) fail('Request/receipt language schema mismatch');
  if (!legacy && JSON.stringify(checked.value.language_contract) !== JSON.stringify(r.language_contract)) fail('Language contract binding mismatch');
  if (checked.hash !== r.request_sha256 || checked.root !== root || checked.value.stage !== r.stage || checked.value.prompt !== r.prompt?.path || checked.value.initial_prompt_sha256 !== r.initial_prompt_sha256) fail('Request hash or binding mismatch');
  const prompt = await textFile(await rootFile(root, relativeName(r.prompt.path)));
  if (prompt.hash !== r.prompt.sha256) fail('Prompt hash mismatch');
  const language = legacy ? { language_status: LANGUAGE_STATUS.LEGACY, language_validation_limitations: 'Legacy evidence predates the bounded language contract and is read-only.' } : validatePromptLanguage(prompt.text, r.language_contract);
  const snapshot = await jsonFile(await rootFile(root, relativeName(r.evidence?.path)));
  if (snapshot.hash !== r.evidence.sha256) fail('Evidence snapshot hash mismatch');
  const saved = snapshot.value;
  if (saved.schema_version !== 1 || saved.kind !== 'astra_author_evidence_snapshot' || typeof saved.raw_record !== 'string' || saved.raw_record.includes('\n') || JSON.stringify(saved.source) !== JSON.stringify(r.evidence.source)) fail('Evidence snapshot binding mismatch');
  const source = saved.source;
  if (!Number.isSafeInteger(source.line) || source.line < 1 || sha256(saved.raw_record) !== source.record_sha256) fail('Evidence record hash mismatch');
  const canonical = await evidenceFile(source.path);
  if (canonical !== source.path) fail('Evidence source canonical path changed');
  // Check only the originally selected line. Appending later messages is safe.
  const currentLine = (await fs.readFile(canonical, 'utf8')).split('\n')[source.line - 1];
  if (typeof currentLine !== 'string' || sha256(currentLine) !== source.record_sha256 || currentLine !== saved.raw_record) fail('Original evidence record changed or missing');
  const { raw_record, ...record } = evidenceMatch(Buffer.from(saved.raw_record), checked.value, prompt);
  record.line = source.line;
  if (JSON.stringify(record) !== JSON.stringify(r.author_record) || r.session_id !== authorSessionId(record, canonical) || r.task_id !== (record.task_id ?? null) || r.requester_session_id !== checked.value.session_id || r.requester_task_id !== checked.value.task_id) fail('Author record binding mismatch');
  return { state: 'READY_FOR_EXECUTION', receipt_sha256: loaded.hash, stage: r.stage, prompt: r.prompt, execution_model: 'inherit_session', author_record: record, language_contract: legacy ? undefined : r.language_contract, ...language, limitations: LIMITATIONS };
}
export async function readContext(input) {
  if (typeof input !== 'string' || !input) fail('Context must be a JSON file path or JSON object literal');
  const context = input.trimStart().startsWith('{') ? JSON.parse(input) : JSON.parse(await fs.readFile(input, 'utf8'));
  if (!context || typeof context !== 'object' || Array.isArray(context)) fail('Context must be a JSON object');
  return context;
}
export async function main(argv = process.argv.slice(2)) {
  const [command, ...args] = argv;
  const positional = [], options = {};
  for (let i = 0; i < args.length; i++) {
    if (!args[i].startsWith('--')) { positional.push(args[i]); continue; }
    const key = args[i].slice(2);
    if (!['context', 'root', 'prompt', 'out', 'request', 'evidence', 'sha256'].includes(key) || options[key] !== undefined || !args[i + 1] || args[i + 1].startsWith('--')) fail(`Invalid option: ${args[i]}`);
    options[key] = args[++i];
  }
  const allowed = { status: [], route: ['context'], request: ['context', 'root', 'prompt', 'out'], seal: ['request', 'evidence', 'out'], verify: ['sha256'] };
  if (!(command in allowed) || Object.keys(options).some(k => !allowed[command].includes(k)) || positional.length !== (['route', 'request', 'verify'].includes(command) ? 1 : 0)) fail('Usage: status | route <stage> --context <json> | request <stage> --context <json> --root <absolute> --prompt <relative> --out <relative> | seal --request <absolute> --evidence <absolute> --out <relative> | verify <receipt> --sha256 <accepted hash>');
  for (const key of allowed[command]) if (!options[key]) fail(`Missing --${key}`);
  const policy = await loadPolicy();
  const context = options.context ? await readContext(options.context) : {};
  if (command === 'status') return status(policy);
  if (command === 'route') return route(positional[0], context, policy);
  if (command === 'request') return request({ ...options, stage: positional[0], context }, policy);
  if (command === 'seal') return seal(options, policy);
  return verify(positional[0], options.sha256, policy);
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().then(result => { console.log(JSON.stringify(result, null, 2)); if (result.state === 'HOLD_ASTRA_AUTHOR_REQUIRED') process.exitCode = 2; }).catch(error => { console.error(error.message); process.exitCode = 1; });
}
