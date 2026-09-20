import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { selectKnowledge, verifyKnowledge, knowledgeHash } from './knowledge.mjs';

const hash = x => createHash('sha256').update(x).digest('hex');
const web = { kind: 'web', url: 'https://example.test/reviewed', reviewed_at: '2026-09-20' };
async function fixture(t, live = true) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aside-knowledge-test-'));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const wikiRoot = path.join(root, 'wiki'), dir = path.join(root, 'catalog');
  await fs.mkdir(path.join(wikiRoot, 'concepts'), { recursive: true });
  await fs.mkdir(dir);
  const upstream = '# Upstream\nReviewed guidance.\n';
  await fs.writeFile(path.join(wikiRoot, 'concepts/upstream.md'), upstream);
  const wiki = { kind: 'wiki', path: 'concepts/upstream.md', sha256: hash(upstream), section: '# Upstream' };
  const make = (id, stage, version, tags, always, sources = [web]) => ({ id, heading: `### ${id}`, stages: [stage], versions: [version], tags, always, status: 'active', evidence: 'reviewed_heuristic', sources });
  const cards = [make('image-base', 'image_prompt', 'chatgpt-web', [], true), make('image-identity', 'image_prompt', 'chatgpt-web', ['identity', 'reference'], false, [wiki]), make('image-edit', 'image_prompt', 'chatgpt-web', ['edit', 'text', 'product'], false), make('video-base', 'seedance_prompt', 'seedance-2.0', ['action', 'camera', 'live_action', 'animation', 'audio', 'storyboard'], true), make('video25-base', 'seedance_prompt', 'seedance-2.5', ['action', 'animation'], true)];
  let corpus = '---\nprivate: FRONTMATTER_SECRET\n---\n# Compiled\nINTRO_SECRET\n## Cards\n';
  for (const card of cards) corpus += `${card.heading}\nFull ${card.id} content.\n#### Detail\nKeep the complete nested detail.\n\n`;
  corpus += '## CHANGELOG\nCHANGELOG_SECRET\n';
  const c = { schema_version: 1, revision: '2026-09-20.1', reviewed_at: '2026-09-20', wiki_file: 'concepts/compiled.md', source_file: 'compiled.md', source_sha256: hash(corpus), max_cards: 6, max_chars: 9000, cards };
  const options = { catalogFile: path.join(dir, 'catalog.json'), wikiRoot };
  const liveFile = path.join(wikiRoot, c.wiki_file), snapshotFile = path.join(dir, c.source_file);
  const save = () => fs.writeFile(options.catalogFile, JSON.stringify(c));
  const writeCorpus = async text => { c.source_sha256 = hash(text); await fs.writeFile(snapshotFile, text); if (live) await fs.writeFile(liveFile, text); await save(); };
  await writeCorpus(corpus);
  return { root, c, options, save, corpus, writeCorpus, liveFile, snapshotFile };
}
const select = (f, context = {}, stage = 'image_prompt') => selectKnowledge(stage, context, f.options);
const reseal = packet => ({ ...packet, sha256: knowledgeHash(packet) });

test('music is excluded without reading any files', async () => {
  assert.equal(await selectKnowledge('music_prompt', {}, { catalogFile: '/absent/catalog.json' }), null);
});
test('deterministic complete cards, bounded provenance and JSON digest', async t => {
  const f = await fixture(t), p = await select(f, { knowledge_tags: ['identity'] });
  assert.equal(p.status, 'CURRENT_KNOWLEDGE_VALIDATED');
  assert.equal(p.source.mode, 'live_wiki');
  assert.equal(p.source.fallback, false);
  assert.deepEqual(p.selected_ids, ['image-base', 'image-identity']);
  assert.match(p.text, /#### Detail\nKeep the complete nested detail\./);
  assert.doesNotMatch(p.text, /FRONTMATTER_SECRET|INTRO_SECRET|CHANGELOG_SECRET|image-edit|video-base/);
  const { sha256, ...rest } = p;
  assert.equal(sha256, hash(JSON.stringify(rest)));
  assert.deepEqual(await select(f, { knowledge_tags: ['identity'] }), p);
  assert.deepEqual(await verifyKnowledge(p, f.options), p);
});
test('snapshot fallback is explicit and does not require live upstream', async t => {
  const f = await fixture(t, false);
  await fs.rm(f.options.wikiRoot, { recursive: true });
  const p = await select(f, { knowledge_tags: ['identity'] });
  assert.equal(p.source.mode, 'reviewed_snapshot');
  assert.equal(p.source.fallback, true);
  assert.match(p.source.notice, /FALLBACK.*not checked/);
  assert.deepEqual(await verifyKnowledge(p, f.options), p);
});
test('live mismatch never falls back to a correct snapshot', async t => {
  const f = await fixture(t); await fs.appendFile(f.liveFile, '\nchanged');
  await assert.rejects(select(f), /source hash drift/);
});
test('snapshot itself is hash checked', async t => {
  const f = await fixture(t, false); await fs.appendFile(f.snapshotFile, 'changed');
  await assert.rejects(select(f), /source hash drift/);
});
for (const change of ['delete', 'change']) test(`verify rejects ${change} of recorded live source`, async t => {
  const f = await fixture(t), p = await select(f);
  if (change === 'delete') await fs.unlink(f.liveFile); else await fs.appendFile(f.liveFile, 'drift');
  await assert.rejects(verifyKnowledge(p, f.options), /source|packet/);
});
test('selected upstream drift and deletion fail closed', async t => {
  const f = await fixture(t), p = await select(f, { knowledge_tags: ['identity'] });
  const source = path.join(f.options.wikiRoot, 'concepts/upstream.md');
  await fs.writeFile(source, 'changed');
  await assert.rejects(verifyKnowledge(p, f.options), /upstream wiki hash drift/);
  await fs.unlink(source);
  await assert.rejects(select(f, { knowledge_tags: ['identity'] }), /ENOENT/);
  assert.deepEqual((await select(f)).selected_ids, ['image-base']);
});
test('catalog byte drift invalidates previously selected packets', async t => {
  const f = await fixture(t), p = await select(f); await fs.appendFile(f.options.catalogFile, '\n');
  await assert.rejects(verifyKnowledge(p, f.options), /packet differs/);
});
for (const field of ['text', 'selected_ids', 'cards', 'source', 'status', 'attributes']) test(`rehashed packet ${field} tampering fails`, async t => {
  const f = await fixture(t), p = await select(f);
  if (field === 'text') p.text = 'forged';
  if (field === 'selected_ids') p.selected_ids = ['forged'];
  if (field === 'cards') p.cards[0].sources[0].url = 'https://changed.test';
  if (field === 'source') p.source.sha256 = 'a'.repeat(64);
  if (field === 'status') p.status = 'PASS';
  if (field === 'attributes') p.attributes.version = 'seedance-2.5';
  await assert.rejects(verifyKnowledge(reseal(p), f.options), /packet/);
});
test('unrehashed packet and null packet fail', async t => {
  const f = await fixture(t), p = await select(f); p.text += 'edit';
  await assert.rejects(verifyKnowledge(p, f.options), /digest/);
  await assert.rejects(verifyKnowledge(null, f.options), /digest/);
});
test('version routing keeps 2.0 and 2.5 apart', async t => {
  const f = await fixture(t);
  assert.deepEqual((await select(f, {}, 'seedance_prompt')).selected_ids, ['video-base']);
  assert.deepEqual((await select(f, { knowledge_version: 'seedance-2.5' }, 'seedance_prompt')).selected_ids, ['video25-base']);
  await assert.rejects(select(f, { knowledge_version: 'seedance-2.5' }), /stage\/version/);
  await assert.rejects(select(f, { knowledge_version: 'chatgpt-web' }, 'seedance_prompt'), /stage\/version/);
  await assert.rejects(select(f, {}, 'unknown'), /stage/);
});
test('bilingual inference uses English word boundaries and stable allowlist order', async t => {
  const f = await fixture(t);
  assert.deepEqual((await select(f, { user_instruction: 'character edit typography reference' })).attributes.tags, ['reference', 'identity', 'edit', 'text']);
  assert.deepEqual((await select(f, { user_instruction: '캐릭터 얼굴 참조 수정 문구 제품' })).attributes.tags, ['reference', 'identity', 'edit', 'text', 'product']);
  assert.deepEqual((await select(f, { user_instruction: 'credit actionables cameraman soundtrack' })).attributes.tags, []);
  const p = await select(f, { user_instruction: '실사 애니 동작 카메라 콘티 소리' }, 'seedance_prompt');
  assert.deepEqual(p.attributes.tags, ['live_action', 'animation', 'action', 'camera', 'storyboard', 'audio']);
});
test('explicit unknown/unmapped/duplicate/non-list tags are rejected', async t => {
  const f = await fixture(t);
  for (const tags of [['mystery'], ['audio'], ['identity', 'identity'], 'identity']) await assert.rejects(select(f, { knowledge_tags: tags }), /tag/);
});
const mutations = {
  'duplicate ID': c => c.cards.push({ ...c.cards[0] }),
  'bad heading': c => { c.cards[0].heading = '### wrong'; },
  'inactive status': c => { c.cards[0].status = 'deprecated'; },
  'unknown stage': c => { c.cards[0].stages = ['unknown']; },
  'unknown version': c => { c.cards[0].versions = ['seedance-9']; },
  'incompatible version': c => { c.cards[0].versions = ['seedance-2.0']; },
  'missing always': c => { delete c.cards[0].always; },
  'missing provenance': c => { c.cards[0].sources = []; },
  'unknown evidence': c => { c.cards[0].evidence = 'rumor'; },
  'invalid date': c => { c.reviewed_at = '2026-02-31'; },
  'invalid schema': c => { c.schema_version = 2; },
  'invalid budget': c => { c.max_cards = 7; },
  'unsafe URL': c => { c.cards[0].sources = [{ ...web, url: 'file:///tmp/x' }]; },
  'traversal': c => { c.wiki_file = '../outside.md'; },
  'absolute source': c => { c.source_file = '/tmp/outside.md'; },
  'raw source': c => { c.cards[1].sources[0].path = 'raw/unreviewed.md'; },
};
for (const [name, mutate] of Object.entries(mutations)) test(`catalog rejects ${name}`, async t => {
  const f = await fixture(t); mutate(f.c); await f.save(); await assert.rejects(select(f));
});
test('missing, duplicate and CHANGELOG-contained sections fail', async t => {
  const f = await fixture(t);
  for (const corpus of [f.corpus.replace('### image-base', '### absent'), f.corpus + '\n### image-base\nDuplicate\n', f.corpus.replace('## Cards', '## CHANGELOG')]) {
    await f.writeCorpus(corpus); await assert.rejects(select(f), /section|CHANGELOG/);
  }
});
test('fenced headings do not cut a card, same/lower headings do', async t => {
  const f = await fixture(t);
  await f.writeCorpus(f.corpus.replace('Full image-base content.', 'Full image-base content.\n```md\n## Not a boundary\n```\nTail survives.'));
  const p = await select(f); assert.match(p.text, /## Not a boundary\n```\nTail survives\./);
  assert.doesNotMatch(p.text, /image-identity/);
});
test('card and character caps fail rather than dropping or truncating', async t => {
  const f = await fixture(t); f.c.max_cards = 1; await f.save();
  await assert.rejects(select(f, { knowledge_tags: ['identity'] }), /budget/);
  f.c.max_cards = 6; f.c.max_chars = 10; await f.save();
  await assert.rejects(select(f), /character budget/);
});
for (const target of ['live', 'snapshot', 'upstream', 'directory', 'dangling']) test(`${target} symlink escape fails`, async t => {
  const f = await fixture(t, target !== 'snapshot');
  const outside = path.join(f.root, 'outside.md'); await fs.writeFile(outside, f.corpus);
  let destination = target === 'snapshot' ? f.snapshotFile : target === 'upstream' ? path.join(f.options.wikiRoot, 'concepts/upstream.md') : f.liveFile;
  if (target === 'directory') {
    destination = path.join(f.options.wikiRoot, 'concepts');
    const outdir = path.join(f.root, 'external'); await fs.mkdir(outdir); await fs.writeFile(path.join(outdir, 'compiled.md'), f.corpus);
    await fs.rm(destination, { recursive: true }); await fs.symlink(outdir, destination);
  } else { await fs.unlink(destination); await fs.symlink(target === 'dangling' ? outside + '-absent' : outside, destination); }
  await assert.rejects(select(f, target === 'upstream' ? { knowledge_tags: ['identity'] } : {}), /escape|ENOENT/);
});
test('environment wiki override is isolated and restored', async t => {
  const f = await fixture(t), previous = process.env.ASIDE_VIDEO_WIKI_ROOT;
  process.env.ASIDE_VIDEO_WIKI_ROOT = f.options.wikiRoot;
  try { assert.equal((await selectKnowledge('image_prompt', {}, { catalogFile: f.options.catalogFile })).source.mode, 'live_wiki'); }
  finally { if (previous === undefined) delete process.env.ASIDE_VIDEO_WIKI_ROOT; else process.env.ASIDE_VIDEO_WIKI_ROOT = previous; }
});

test('explicit null and malformed context values cannot silently default', async t => {
  const f = await fixture(t);
  for (const context of [null, [], { knowledge_version: null }, { knowledge_tags: null }, { user_instruction: null }]) await assert.rejects(select(f, context));
});
test('verify never opens fallback after recorded live source disappears', async t => {
  const f = await fixture(t), p = await select(f);
  await fs.unlink(f.liveFile); await fs.unlink(f.snapshotFile);
  await assert.rejects(verifyKnowledge(p, f.options), /no verification fallback/);
});
test('fallback packets cannot silently become live packets', async t => {
  const f = await fixture(t, false), p = await select(f);
  await fs.writeFile(f.liveFile, f.corpus);
  await assert.rejects(verifyKnowledge(p, f.options), /source mode changed/);
});
test('catalog symlink outside its root is rejected', async t => {
  const f = await fixture(t), external = path.join(f.root, 'other-catalog.json');
  await fs.copyFile(f.options.catalogFile, external); await fs.unlink(f.options.catalogFile);
  await fs.symlink(external, f.options.catalogFile);
  await assert.rejects(select(f), /symlink path escape/);
});

for(const dir of ['_archive','_hub'])test('nested '+dir+' is never a creative source',async t=>{const f=await fixture(t);f.c.wiki_file='concepts/'+dir+'/compiled.md';await f.save();await assert.rejects(select(f),/unsafe knowledge path/);});
