// Size/routing checks, not proof of execution behavior or token savings.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const root=new URL('../',import.meta.url);
for(const [name,budget] of [['SKILL.md',2600],['references/author-executor.md',2800]]) {
  test(`${name} stays a bounded entry`,async()=>{
    const text=await fs.readFile(new URL(name,root),'utf8');
    assert.ok([...text].length<=budget,`${name} exceeds ${budget} characters`);
  });
}
test('entry routes to existing references instead of inlining all stages',async()=>{
  const text=await fs.readFile(new URL('SKILL.md',root),'utf8');
  const links=[...new Set(text.match(/references\/[\w-]+\.md/g))];
  assert.ok(links.length>=6);
  for(const link of links)assert.ok((await fs.stat(new URL(link,root))).isFile());
  for(const invariant of ['gpt-6-astra','영어 기본','submission','Reference','QC'])assert.ok(text.includes(invariant));
});
