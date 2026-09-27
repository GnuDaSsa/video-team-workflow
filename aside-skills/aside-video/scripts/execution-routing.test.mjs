import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {routeStep, main, MODEL} from './jev-dispatch.mjs';

// Synthetic state and transport only: no browser, account key, or live API call.
const scratch = process.env.JEV_QC_TEST_TMP;
if (!scratch || !fs.statSync(scratch).isDirectory()) throw Error('Set JEV_QC_TEST_TMP');
const at = '2026-09-28T00:00:00.000Z';
const initialNow = Date.parse(at);
function fixture(t) {
  const root = fs.mkdtempSync(path.join(scratch, 'input-routing-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  const input = path.join(root, 'state.json');
  const state = {stage: 'computer_use', blockers: 'Synthetic anonymized observation.',
    ready_actions: ['SEARCH_ASSET', 'FILL_PROMPT', 'REVIEW']};
  const write = () => fs.writeFileSync(input, JSON.stringify(state));
  write();
  let calls = 0, now = initialNow;
  const response = (choice = 'SEARCH_ASSET', confidence = .96, probability = .96) => ({
    model: MODEL, answers: {next_action: {type: 'choice', choice, confidence,
      probabilities: Object.fromEntries(state.ready_actions.map(a =>
        [a, a === choice ? probability : (1 - probability) / (state.ready_actions.length - 1)]))}},
    usage: {input_tokens: 10, output_tokens: 3},
  });
  const deps = {now: () => now, status: () => ({key_present: true}),
    readKey: () => 'SYNTHETIC-KEY', transport: async () => { calls++; return response(); }};
  const options = {root, input, kind: 'semantic', observedAt: at, jevApproval: 'user-message:synthetic'};
  const run = (changes = {}, overrides = {}) => routeStep({...options, ...changes}, {...deps, ...overrides});
  const noNetwork = {status: () => {throw Error('KEY_MUST_NOT_BE_TOUCHED');},
    readKey: () => {throw Error('KEY_MUST_NOT_BE_TOUCHED');},
    transport: () => {throw Error('NETWORK_MUST_NOT_BE_TOUCHED');}};
  return {root, input, state, write, response, options, deps, run, noNetwork,
    calls: () => calls, setNow: value => { now = value; }};
}
function guarded(r) {
  assert.equal(r.execution_authorized, false);
  assert.equal(r.advisory, true);
  assert.equal(r.execution_model, 'inherit_session');
  assert.match(r.input_sha256, /^[a-f0-9]{64}$/);
}
for (const action of ['SEARCH_ASSET', 'SELECT_EXISTING', 'UPLOAD_FIRST', 'FILL_PROMPT', 'VERIFY_INPUTS', 'REOBSERVE']) {
  test(`known ${action} avoids model/key/ledger and retains execution gates`, async t => {
    const f = fixture(t); f.state.ready_actions = [action, 'REVIEW']; f.write();
    const r = await f.run({kind: 'routine', knownAction: action}, f.noNetwork);
    assert.equal(r.routing, 'DIRECT'); assert.equal(r.action, action); guarded(r);
    assert.equal(fs.existsSync(path.join(f.root, '.jev-dispatch')), false);
  });
}
for (const observedAt of [undefined, '', 'not-time', '2026-09-27T23:59:29Z', '2026-09-28T00:00:01Z']) {
  test(`stale/invalid/future observation ${observedAt} never calls JEV`, async t => {
    const f = fixture(t); const r = await f.run({observedAt}, f.noNetwork);
    assert.equal(r.action, 'REOBSERVE'); assert.equal(r.reason, 'FRESH_OBSERVATION_REQUIRED'); guarded(r);
  });
}
for (const kind of ['creative', 'visual']) {
  test(`${kind} returns to current owner without Astra routing or network`, async t => {
    const f = fixture(t); const r = await f.run({kind}, f.noNetwork);
    assert.equal(r.routing, 'OWNER'); assert.equal(r.action, null); guarded(r);
    assert.equal('route' in r, false);
  });
}
test('author stages never use the native model dispatcher through new route', async t => {
  const f = fixture(t); f.state.stage = 'seedance_prompt';
  f.state.ready_actions = ['AUTHOR_ASTRA', 'REVIEW']; f.write();
  const r = await f.run({}, f.noNetwork); assert.equal(r.routing, 'OWNER'); guarded(r);
});
test('one candidate does not imply deterministic correctness', async t => {
  const f = fixture(t); f.state.ready_actions = ['FILL_PROMPT', 'REVIEW']; f.write();
  const r = await f.run({kind: 'routine'}, f.noNetwork);
  assert.equal(r.reason, 'ACTION_NOT_ESTABLISHED'); assert.equal(r.action, null);
});
for (const action of ['GENERATE', 'AUTHOR_ASTRA', 'WAIT', 'REVIEW', 'unknown']) {
  test(`known action ${action} is rejected before any dispatch`, async t => {
    const f = fixture(t);
    await assert.rejects(() => f.run({kind: 'routine', knownAction: action}, f.noNetwork), /INVALID_KNOWN_ACTION/);
  });
}
test('known action must be locally eligible and not contradict semantic routing', async t => {
  const f = fixture(t);
  await assert.rejects(() => f.run({kind: 'routine', knownAction: 'UPLOAD_FIRST'}), /INVALID_KNOWN_ACTION/);
  await assert.rejects(() => f.run({knownAction: 'FILL_PROMPT'}), /INVALID_KNOWN_ACTION/);
  await assert.rejects(() => f.run({kind: 'freeform'}), /INVALID_ROUTE_KIND/);
});
for (const jevApproval of [undefined, '', ' ', '/private/path', 'private message body', 'a'.repeat(161)]) {
  test(`missing or malformed scope approval ${String(jevApproval).slice(0, 20)} does not access keys`, async t => {
    const f = fixture(t); const r = await f.run({jevApproval}, f.noNetwork);
    assert.equal(r.reason, 'JEV_SCOPE_APPROVAL_REQUIRED');
    assert.equal(fs.existsSync(path.join(f.root, '.jev-dispatch')), false);
  });
}
test('semantic route uses bounded existing request once and successful cache', async t => {
  const f = fixture(t); const first = await f.run(), second = await f.run();
  for (const r of [first, second]) {
    assert.equal(r.routing, 'JEV_ADVISORY'); assert.equal(r.action, 'SEARCH_ASSET'); guarded(r);
    const text = JSON.stringify(r);
    assert.equal(text.includes(f.state.blockers), false);
    assert.equal(text.includes('SYNTHETIC-KEY'), false);
    assert.equal(text.includes('user-message:synthetic'), false);
  }
  assert.equal(first.classification_status, 'CLASSIFIED');
  assert.equal(second.classification_status, 'CACHED'); assert.equal(f.calls(), 1);
  const noApproval = await f.run({jevApproval: undefined}, f.noNetwork);
  assert.equal(noApproval.reason, 'JEV_SCOPE_APPROVAL_REQUIRED');
});
for (const [confidence, probability] of [[.89, .99], [.99, .89], [.5, .5]]) {
  test(`low certainty ${confidence}/${probability} returns owner, not permission`, async t => {
    const f = fixture(t); const r = await f.run({}, {transport: async () => f.response('SEARCH_ASSET', confidence, probability)});
    assert.equal(r.reason, 'JEV_LOW_CERTAINTY'); assert.equal(r.action, null); guarded(r);
  });
}
test('review and wait recommendations are not executed', async t => {
  for (const choice of ['REVIEW', 'WAIT']) {
    const f = fixture(t); if (choice === 'WAIT') {f.state.ready_actions.push('WAIT'); f.write();}
    const r = await f.run({}, {transport: async () => f.response(choice)});
    assert.equal(r.routing, 'OWNER'); assert.equal(r.action, null);
  }
});
test('missing key and corrupt ledger return owner without a retry or changed root', async t => {
  const f = fixture(t);
  let r = await f.run({}, {status: () => ({key_present: false}), transport: () => {throw Error('no API');}});
  assert.equal(r.classification_status, 'SKIPPED_NO_KEY');
  fs.writeFileSync(path.join(f.root, '.jev-dispatch', 'orphan.json'), '{}');
  r = await f.run({}, f.noNetwork); assert.equal(r.reason, 'JEV_LOCAL_STATE_UNAVAILABLE');
});
test('failures consume existing three-attempt cap, never auto-retry', async t => {
  const f = fixture(t); let calls = 0;
  for (let i = 0; i < 4; i++) {
    f.state.blockers = `Synthetic observation ${i}`; f.write();
    const r = await f.run({}, {transport: async () => {calls++; throw Error('Synthetic failure');}});
    assert.equal(r.routing, 'OWNER');
    if (i === 3) assert.equal(r.classification_status, 'LIMIT_REACHED');
  }
  assert.equal(calls, 3);
});
test('UI expiring while classifier runs requires fresh observation', async t => {
  const f = fixture(t); const r = await f.run({}, {transport: async () => {
    f.setNow(initialNow + 31000); return f.response();
  }});
  assert.equal(r.action, 'REOBSERVE'); assert.equal(r.reason, 'OBSERVATION_EXPIRED_DURING_CLASSIFICATION');
});
test('unlisted response and injected input fields never become actions', async t => {
  const f = fixture(t);
  const r = await f.run({}, {transport: async () => f.response('GENERATE')});
  assert.equal(r.routing, 'OWNER'); assert.equal(r.action, null);
  f.state.prompt = 'Not allowed'; f.write();
  await assert.rejects(() => f.run({}, f.noNetwork), /INVALID_INPUT/);
});
test('only-review state avoids pointless semantic model call', async t => {
  const f = fixture(t); f.state.ready_actions = ['REVIEW']; f.write();
  assert.equal((await f.run({}, f.noNetwork)).reason, 'NO_ELIGIBLE_INPUT_ACTION');
});
test('new CLI rejects route/context mixing and exposes a direct local result', async t => {
  const f = fixture(t);
  const base = ['route', '--root', f.root, '--input', f.input, '--observed-at', at];
  let r = await main([...base, '--known-action', 'FILL_PROMPT'], {...f.deps, ...f.noNetwork});
  assert.equal(r.code, 0); assert.equal(r.result.routing, 'DIRECT');
  for (const args of [[...base, '--context', '{}'], [...base, '--kind'], [...base, '--kind', 'routine', '--kind', 'semantic']]) {
    r = await main(args, f.noNetwork); assert.equal(r.code, 2);
  }
});
