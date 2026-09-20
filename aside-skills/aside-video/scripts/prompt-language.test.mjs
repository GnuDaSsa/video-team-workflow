import test from 'node:test';
import assert from 'node:assert/strict';
import { createLanguageContract, validateLanguageContract, validatePromptLanguage } from './prompt-language.mjs';

test('default contract is en-US and rejects Korean prose', () => {
  const contract = createLanguageContract({ user_instruction: 'Create an image prompt.' });
  assert.deepEqual(contract, { language: 'en-US', user_instruction: 'Create an image prompt.', preserved_literals: [], override_reason: null });
  assert.throws(() => validatePromptLanguage('한국어 설명', contract), /non-Latin|Latin prose/);
});
test('English prose permits exact preserved Korean dialogue only', () => {
  const contract = createLanguageContract({ user_instruction: 'Create an image prompt.', preserved_literals: ['"안녕하세요"'] });
  assert.equal(validatePromptLanguage('A person says "안녕하세요" in a quiet room.', contract).language_status, 'CURRENT_POLICY_VALIDATED');
  assert.throws(() => validatePromptLanguage('A person says "안녕하세요" then 안녕 in a quiet room.', contract), /non-Latin/);
});
test('explicit valid override needs reason and never auto-infers', () => {
  const override = { language: 'ko-KR', user_instruction: '한국어 프롬프트를 작성해 주세요.', reason: 'The project requires Korean provider text.' };
  const contract = createLanguageContract({ prompt_language_override: override });
  assert.equal(contract.language, 'ko-KR');
  assert.equal(validatePromptLanguage('한국어 설명', contract).language_status, 'CURRENT_POLICY_VALIDATED');
  assert.throws(() => createLanguageContract({ user_instruction: '한국어 요청', prompt_language_override: { language: 'ko-KR', user_instruction: '한국어 요청' } }), /Invalid prompt_language_override/);
});
test('contract schema is exact and script guard is not semantic proof', () => {
  const contract = createLanguageContract({ user_instruction: 'Create a prompt.' });
  assert.throws(() => validateLanguageContract({ ...contract, extra: true }), /schema/);
  assert.match(validatePromptLanguage('Una escena luminosa.', contract).language_validation_limitations, /not semantic proof/);
});

test('English regional tags cannot skip the script guard',()=>{const c=createLanguageContract({prompt_language_override:{language:'en-gb',user_instruction:'Use British English.',reason:'Explicit regional spelling request.'}});assert.equal(c.language,'en-GB');assert.throws(()=>validatePromptLanguage('한국어 문장',c),/non-Latin/);assert.throws(()=>validateLanguageContract({...c,language:'en-gb'}),/language/);});
test('overlapping preserved literals are checked against the full original',()=>{const c=createLanguageContract({user_instruction:'Keep the exact Korean greeting.',preserved_literals:['안녕','안녕하세요']});assert.equal(validatePromptLanguage('A speaker says 안녕하세요.',c).language_status,'CURRENT_POLICY_VALIDATED');});
test('explicit override still requires declared literals to remain verbatim',()=>{const c=createLanguageContract({prompt_language_override:{language:'ko-KR',reason:'Explicit request.',user_instruction:'한국어로 작성'},preserved_literals:['정확한 문구']});assert.throws(()=>validatePromptLanguage('다른 문구',c),/absent/);});
