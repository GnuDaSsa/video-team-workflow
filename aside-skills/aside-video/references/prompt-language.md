# Persistent prompt-language contract

## Default and precedence

- New image and Seedance provider prompts use **English (en-US)** by default.
- Music style/production instructions are also English by default. Literal lyrics,
  spoken dialogue and required on-screen text retain the language requested by the
  user. Korean planning, explanation and progress messages remain fine.
- A Korean conversation, old example, file/skill name or existing project's old
  default does not authorize Korean prompt prose for a new task.
- Only a current explicit task/project language instruction overrides the default.
  Record it in `context.prompt_language_override` with `language`, a nonempty
  `reason`, and the actual `user_instruction`. Do not fabricate a quote or infer consent from a language mix.
- Record required verbatim text in `context.preserved_literals`. This list is for
  actual lyrics/dialogue/signage, not a way to exempt the entire descriptive prompt.
- Older Codex Korean-default / block-scoped English rules apply to their historical
  project contracts only. They do not override the native Aside default here.

## Enforced handoff

1. Copy the read-only session-context result and add `context.user_instruction`
   containing the actual user request before `harness request`. Do not ask the user
   to repeat it or invent an English-language approval; English is already the default.
   `harness request` resolves the language contract before Astra writes the prompt.
   Include the emitted `author_task` and `language_contract` in the real author
   assignment; do not prepend a conflicting Korean-writing request.
2. Astra writes/edits/translates the final prompt. The executor never translates,
   summarizes, or silently substitutes a different language after acceptance.
3. `seal`, `submission prepare` and `submission verify` bind and validate the same
   contract and full original text. Unknown or tampered metadata fails closed.
4. Current input requires `language_status=CURRENT_POLICY_VALIDATED`. Legacy
   schema-1 evidence may be read for audit as `LEGACY_UNSPECIFIED_READ_ONLY`, but
   must not be promoted to a new submission without a new Astra request/handoff.
5. Keep old accepted prompts, test assets, receipts and submitted jobs unchanged.
   A new language revision requires new request/receipt/payload files.

Example task-level exception (only when actually requested):

```json
{"prompt_language_override":{"language":"ko-KR","reason":"Explicit language choice for this task","user_instruction":"이번 영상 프롬프트는 한국어로 작성해 주세요."},"preserved_literals":[]}
```

Example English prompt with exact Korean spoken text:

```json
{"user_instruction":"Make an English video prompt with the exact spoken greeting 안녕하세요.","preserved_literals":["안녕하세요"]}
```

The local English guard detects unexpected non-Latin scripts outside the declared
literals. It is **not** a semantic English-language or translation-quality detector;
Latin-script non-English text still needs Astra/executor review. Language switching
is not a way around provider policy and is not a proven quality/speed improvement.
