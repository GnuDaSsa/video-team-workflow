// Bounded language metadata and script checks. This is not semantic language detection.
import { isDeepStrictEqual } from 'node:util';

const fail = message => { throw new Error(message); };
const keys = ['language', 'user_instruction', 'preserved_literals', 'override_reason'];
const latin = /\p{Script=Latin}/u;
const letter = /\p{L}/u;
const validTag = value => {
  if (typeof value !== 'string' || !value) return false;
  try { return Intl.getCanonicalLocales(value).length === 1; } catch { return false; }
};
function string(value, label) {
  if (typeof value !== 'string' || !value.trim() || value !== value.normalize('NFC')) fail(`Invalid language contract ${label}`);
  return value;
}
function literalList(value) {
  if (!Array.isArray(value) || value.some(x => typeof x !== 'string' || !x || x !== x.normalize('NFC')) || new Set(value).size !== value.length) fail('Invalid language contract preserved_literals');
  return value;
}
export function createLanguageContract(context = {}) {
  if (!context || typeof context !== 'object' || Array.isArray(context)) fail('Invalid context');
  const override = context.prompt_language_override;
  if (override !== undefined && (!override || typeof override !== 'object' || Array.isArray(override) || !isDeepStrictEqual(Object.keys(override).sort(), ['language', 'reason', 'user_instruction']))) fail('Invalid prompt_language_override');
  const requestedLanguage = override?.language ?? 'en-US';
  if (!validTag(requestedLanguage)) fail('Invalid language contract language');
  const language = Intl.getCanonicalLocales(requestedLanguage)[0];
  const user_instruction = string(override?.user_instruction ?? context.user_instruction, 'user_instruction');
  const preserved_literals = literalList(context.preserved_literals ?? []);
  const override_reason = override ? string(override.reason, 'override_reason') : null;
  if (override && language === 'en-US') fail('Language override must differ from en-US');
  return Object.freeze({ language, user_instruction, preserved_literals, override_reason });
}
export function validateLanguageContract(contract) {
  if (!contract || typeof contract !== 'object' || Array.isArray(contract) || !isDeepStrictEqual(Object.keys(contract).sort(), keys.slice().sort())) fail('Invalid language contract schema');
  if (!validTag(contract.language) || Intl.getCanonicalLocales(contract.language)[0] !== contract.language) fail('Invalid language contract language');
  string(contract.user_instruction, 'user_instruction');
  literalList(contract.preserved_literals);
  if (contract.language === 'en-US') {
    if (contract.override_reason !== null) fail('Invalid default language contract override_reason');
  } else string(contract.override_reason, 'override_reason');
  return contract;
}
function outsideLiterals(text, literals) {
  let remainder = text;
  for (const literal of literals) if (!text.includes(literal)) fail('Declared preserved literal is absent from prompt');
  for (const literal of [...literals].sort((a, b) => b.length - a.length)) remainder = remainder.split(literal).join('');
  return remainder;
}
export function validatePromptLanguage(prompt, contract) {
  validateLanguageContract(contract);
  if (typeof prompt !== 'string' || !prompt.trim() || prompt !== prompt.normalize('NFC')) fail('Invalid prompt language input');
  const prose = outsideLiterals(prompt, contract.preserved_literals);
  if (new Intl.Locale(contract.language).language !== 'en') return { language_status: 'CURRENT_POLICY_VALIDATED', language_validation_limitations: 'Explicit non-default language override; script guard is not semantic language proof.' };
  let hasLatin = false;
  for (const char of prose) {
    if (letter.test(char)) {
      if (!latin.test(char)) fail('English prompt contains non-Latin letter outside preserved_literals');
      hasLatin = true;
    }
  }
  if (!hasLatin) fail('English prompt requires Latin prose outside preserved_literals');
  return { language_status: 'CURRENT_POLICY_VALIDATED', language_validation_limitations: 'Script validation is not semantic proof of English; it does not distinguish English from other Latin-script languages.' };
}
export const LANGUAGE_STATUS = Object.freeze({ CURRENT: 'CURRENT_POLICY_VALIDATED', LEGACY: 'LEGACY_UNSPECIFIED_READ_ONLY' });
