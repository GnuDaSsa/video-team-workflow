// Reviewed, bounded local knowledge. No model, network, browser, or settings access.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';

const DEFAULT_CATALOG = fileURLToPath(new URL('../references/knowledge/catalog.json', import.meta.url));
const STAGES = { image_prompt: ['chatgpt-web'], seedance_prompt: ['seedance-2.0', 'seedance-2.5'] };
const TAGS = ['reference', 'identity', 'edit', 'text', 'product', 'live_action', 'animation', 'action', 'camera', 'storyboard', 'audio'];
const PATTERNS = [
  /\b(?:references?|ref)\b|참조|레퍼런스/i,
  /\b(?:identity|characters?|faces?|portraits?)\b|정체성|캐릭터|인물|얼굴/i,
  /\b(?:edit|editing|modify|replace|remove)\b|수정|편집|교체|제거/i,
  /\b(?:text|typography|letters?|captions?|logos?)\b|문구|글자|텍스트|로고/i,
  /\b(?:products?|packaging|bottles?)\b|제품|상품|패키지/i,
  /\b(?:live[ -]action|photoreal(?:istic)?|realistic)\b|실사|포토리얼/i,
  /\b(?:animation|animated|anime|cartoon|2d|3d)\b|애니|만화/i,
  /\b(?:action|motion|movement|dance|dancing|run|running)\b|동작|움직임|액션|댄스|춤/i,
  /\b(?:camera|pan|dolly|tracking|zoom)\b|카메라|줌|트래킹/i,
  /\b(?:storyboard|multi[ -]?shot|shot sequence)\b|스토리보드|콘티|멀티.?샷|다중.?컷/i,
  /\b(?:audio|sound|music|dialogue|voice)\b|오디오|음향|소리|음악|대사/i,
];
const fail = message => { throw new Error(`Knowledge: ${message}`); };
const hash = value => createHash('sha256').update(value).digest('hex');
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const nonempty = x => typeof x === 'string' && x.trim().length > 0;
const hex = x => typeof x === 'string' && /^[a-f0-9]{64}$/.test(x);
const date = x => typeof x === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(x) && !Number.isNaN(Date.parse(x)) && new Date(x).toISOString().startsWith(x);
function list(value, allowed, label, allowEmpty = false) {
  if (!Array.isArray(value) || (!allowEmpty && !value.length) || new Set(value).size !== value.length || value.some(x => !allowed.includes(x))) fail(`invalid ${label}`);
}
function relative(name) {
  if (!nonempty(name) || name.includes('\\') || name.includes('\0') || path.isAbsolute(name) || name.split('/').some(x => !x || x === '.' || x === '..' || /^(?:_?raw|_?archive|_?capsules|_hub|context-capsules)$/i.test(x)) || !name.endsWith('.md')) fail('unsafe knowledge path');
  return name;
}
const inside = (root, file) => file === root || file.startsWith(root + path.sep);
// Walk only explicitly registered paths; a dangling or escaping symlink is not an absent source.
async function safeFile(root, name, optional = false) {
  const absoluteRoot = path.resolve(root);
  let realRoot;
  try { realRoot = await fs.realpath(absoluteRoot); }
  catch (e) { if (optional && e.code === 'ENOENT') return null; throw e; }
  let file = absoluteRoot;
  const parts = name.split('/');
  for (let i = 0; i < parts.length; i++) {
    file = path.join(file, parts[i]);
    let stat;
    try { stat = await fs.lstat(file); }
    catch (e) { if (optional && e.code === 'ENOENT') return null; throw e; }
    const real = await fs.realpath(file);
    if (!inside(realRoot, real)) fail('symlink path escape');
    if (stat.isSymbolicLink()) stat = await fs.stat(file);
    if (i < parts.length - 1 ? !stat.isDirectory() : !stat.isFile()) fail('knowledge path is not a regular file');
  }
  return file;
}
function validateCatalog(c) {
  if (!object(c) || c.schema_version !== 1 || !nonempty(c.revision) || !date(c.reviewed_at) || !hex(c.source_sha256)) fail('invalid catalog metadata');
  relative(c.wiki_file); relative(c.source_file);
  if (!c.wiki_file.startsWith('concepts/')) fail('wiki source must be a compiled concept');
  if (!Number.isInteger(c.max_cards) || c.max_cards < 1 || c.max_cards > 6 || !Number.isInteger(c.max_chars) || c.max_chars < 1 || c.max_chars > 9000) fail('invalid catalog budget');
  if (!Array.isArray(c.cards) || !c.cards.length) fail('missing catalog cards');
  const ids = new Set();
  for (const card of c.cards) {
    if (!object(card) || typeof card.id !== 'string' || !/^[\w][\w.-]*$/.test(card.id) || ids.has(card.id) || card.heading !== `### ${card.id}`) fail('invalid or duplicate card id/heading');
    ids.add(card.id);
    list(card.stages, Object.keys(STAGES), 'card stages');
    list(card.versions, Object.values(STAGES).flat(), 'card versions');
    if (card.stages.some(s => !card.versions.some(v => STAGES[s].includes(v))) || card.versions.some(v => !card.stages.some(s => STAGES[s].includes(v)))) fail('incompatible card stage/version');
    list(card.tags, TAGS, 'card tags', true);
    if (typeof card.always !== 'boolean' || card.status !== 'active' || !['official_guidance', 'reviewed_heuristic'].includes(card.evidence)) fail('invalid card status/evidence/always');
    if (!Array.isArray(card.sources) || !card.sources.length) fail('missing card provenance');
    for (const source of card.sources) {
      if (!object(source)) fail('invalid source');
      if (source.kind === 'wiki') {
        relative(source.path);
        if (!source.path.startsWith('concepts/') || !hex(source.sha256) || !nonempty(source.section)) fail('invalid wiki provenance');
      } else if (source.kind === 'web') {
        let url; try { url = new URL(source.url); } catch { fail('invalid web provenance URL'); }
        if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password || !date(source.reviewed_at)) fail('invalid web provenance');
      } else fail('unknown provenance kind');
    }
  }
}
// Markdown headings inside fenced code and YAML are never card boundaries.
function sections(text) {
  const lines = text.match(/[^\n]*(?:\n|$)/g).filter(Boolean);
  const headings = []; let offset = 0, fence = null, yaml = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].replace(/\r?\n$/, '');
    if (i === 0 && line === '---') yaml = true;
    else if (yaml && /^(---|\.\.\.)$/.test(line)) yaml = false;
    else if (!yaml) {
      const marker = line.match(/^ {0,3}(`{3,}|~{3,})/);
      if (fence) { if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length && /^ {0,3}(`+|~+)\s*$/.test(line)) fence = null; }
      else if (marker) fence = marker[1];
      else {
        const atx = line.match(/^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
        if (atx) headings.push({ level: atx[1].length, title: atx[2], start: offset });
        else if (i + 1 < lines.length && line.trim() && /^ {0,3}(=+|-+)\s*$/.test(lines[i + 1].trimEnd())) headings.push({ level: lines[i + 1].trim()[0] === '=' ? 1 : 2, title: line.trim(), start: offset });
      }
    }
    offset += lines[i].length;
  }
  if (yaml || fence) fail('unterminated source frontmatter/fence');
  return heading => {
    const matches = headings.filter(h => '#'.repeat(h.level) + ' ' + h.title === heading);
    if (matches.length !== 1) fail(`missing or duplicate section ${heading}`);
    const h = matches[0], index = headings.indexOf(h);
    const end = headings.slice(index + 1).find(next => next.level <= h.level)?.start ?? text.length;
    const ancestors = [];
    for (const prior of headings.slice(0, index + 1)) { while (ancestors.at(-1)?.level >= prior.level) ancestors.pop(); ancestors.push(prior); }
    if ([...ancestors, ...headings.filter(next => next.start > h.start && next.start < end)].some(x => /changelog/i.test(x.title))) fail('CHANGELOG is not creative knowledge');
    const content = text.slice(h.start, end).trimEnd();
    if (!content.includes('\n') || !content.slice(content.indexOf('\n')).trim()) fail(`empty section ${heading}`);
    return content;
  };
}
function attributes(stage, context) {
  if (!Object.hasOwn(STAGES, stage)) fail('unknown stage');
  if (!object(context)) fail('invalid context');
  const version = context.knowledge_version === undefined ? STAGES[stage][0] : context.knowledge_version;
  if (!STAGES[stage].includes(version)) fail('wrong stage/version');
  const explicit = context.knowledge_tags === undefined ? [] : context.knowledge_tags;
  list(explicit, TAGS, 'explicit knowledge tags', true);
  const instruction = context.user_instruction === undefined ? '' : context.user_instruction;
  if (typeof instruction !== 'string') fail('invalid user_instruction');
  const tags = TAGS.filter((tag, i) => explicit.includes(tag) || PATTERNS[i].test(instruction));
  return { attrs: { stage, version, tags }, input: { knowledge_version: version, knowledge_tags: TAGS.filter(t => explicit.includes(t)), user_instruction: instruction } };
}
export function knowledgeHash(packet) {
  if (!object(packet)) fail('invalid packet');
  const { sha256, ...rest } = packet;
  return hash(JSON.stringify(rest));
}
export async function selectKnowledge(stage, context = {}, options = {}) {
  return buildKnowledge(stage, context, options);
}
async function buildKnowledge(stage, context, options, requiredMode) {
  if (stage === 'music_prompt') return null;
  const { attrs, input } = attributes(stage, context);
  const catalogFile = path.resolve(options.catalogFile instanceof URL ? fileURLToPath(options.catalogFile) : options.catalogFile ?? DEFAULT_CATALOG);
  const wikiRoot = path.resolve(options.wikiRoot ?? process.env.ASIDE_VIDEO_WIKI_ROOT ?? path.join(os.homedir(), 'wiki'));
  await safeFile(path.dirname(catalogFile), path.basename(catalogFile));
  const catalogBytes = await fs.readFile(catalogFile), c = JSON.parse(catalogBytes.toString('utf8'));
  validateCatalog(c);
  const eligible = c.cards.filter(card => card.stages.includes(stage) && card.versions.includes(attrs.version));
  for (const tag of input.knowledge_tags) if (!eligible.some(card => card.tags.includes(tag))) fail(`explicit tag has no eligible card: ${tag}`);
  const selected = eligible.filter(card => card.always || card.tags.some(tag => attrs.tags.includes(tag)));
  if (!selected.length || selected.length > c.max_cards) fail('card selection budget exceeded or empty');
  const live = await safeFile(wikiRoot, c.wiki_file, true);
  if (requiredMode && requiredMode !== (live ? 'live_wiki' : 'reviewed_snapshot')) fail('recorded source mode changed; no verification fallback permitted');
  const sourceFile = live ?? await safeFile(path.dirname(catalogFile), c.source_file);
  const sourceBytes = await fs.readFile(sourceFile);
  if (hash(sourceBytes) !== c.source_sha256) fail('source hash drift');
  const extract = sections(sourceBytes.toString('utf8'));
  // Detect missing catalog sections even when a malformed card is not selected.
  const contents = new Map(c.cards.map(card => [card.id, extract(card.heading)]));
  const checked = new Map();
  const cards = [];
  for (const card of selected) {
    if (live) for (const source of card.sources.filter(s => s.kind === 'wiki')) {
      const key = source.path;
      if (!checked.has(key)) checked.set(key, hash(await fs.readFile(await safeFile(wikiRoot, key))));
      if (checked.get(key) !== source.sha256) fail(`upstream wiki hash drift: ${key}`);
    }
    cards.push({ ...card, text: contents.get(card.id) });
  }
  const text = cards.map(card => card.text).join('\n\n');
  if (text.length > c.max_chars) fail('character budget exceeded; no truncation permitted');
  const packet = {
    schema_version: 1, status: 'CURRENT_KNOWLEDGE_VALIDATED',
    catalog: { path: catalogFile, sha256: hash(catalogBytes), revision: c.revision, reviewed_at: c.reviewed_at },
    source: { mode: live ? 'live_wiki' : 'reviewed_snapshot', path: sourceFile, sha256: hash(sourceBytes), fallback: !live,
      notice: live ? 'Live compiled wiki and selected upstream wiki hashes validated.' : 'FALLBACK: reviewed catalog-adjacent snapshot; live upstream wiki hashes not checked.' },
    attributes: attrs, selection_context: input, selected_ids: cards.map(card => card.id), cards, text,
  };
  return { ...packet, sha256: knowledgeHash(packet) };
}
export async function verifyKnowledge(packet, options = {}) {
  if (!object(packet) || !hex(packet.sha256) || packet.sha256 !== knowledgeHash(packet)) fail('packet digest mismatch');
  if (packet.status !== 'CURRENT_KNOWLEDGE_VALIDATED' || !Object.hasOwn(STAGES, packet.attributes?.stage)) fail('invalid packet status/stage');
  if (!['live_wiki', 'reviewed_snapshot'].includes(packet.source?.mode)) fail('invalid packet source mode');
  const current = await buildKnowledge(packet.attributes.stage, packet.selection_context, options, packet.source.mode);
  if (!isDeepStrictEqual(packet, current)) fail('packet differs from current catalog/source/selection');
  return current;
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const [command, stage, flag, file, ...extra] = process.argv.slice(2);
    if (command !== 'select' || !stage || (flag && (flag !== '--context' || !file)) || extra.length) fail('usage: knowledge.mjs select STAGE [--context JSONFILE]');
    console.log(JSON.stringify(await selectKnowledge(stage, file ? JSON.parse(await fs.readFile(file, 'utf8')) : {}), null, 2));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
