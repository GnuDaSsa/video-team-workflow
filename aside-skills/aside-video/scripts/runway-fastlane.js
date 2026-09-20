async function runwayFastStep({page, snapshot, log, claimUpload}, job) {
  // Trusted local helper, loaded in the existing REPL. No imports, hidden API,
  // model calls, loops, Generate, authoring, or permission escalation.
  const started = Date.now();
  const result = (status, extra = {}) => ({status, action: job?.action, ...extra,
    elapsed_ms: Date.now() - started, generation_submitted: false});
  const permitted = ['SEARCH_ASSET', 'SELECT_EXISTING', 'FILL_PROMPT', 'UPLOAD_FIRST', 'VERIFY_INPUTS', 'REOBSERVE'];
  if (!job || !permitted.includes(job.action)) return result('UNSUPPORTED_ACTION');
  if (typeof job.expected_url !== 'string' || !/^https:\/\/app\.runwayml\.com\//.test(job.expected_url)) return result('SESSION_MISMATCH');
  if (typeof log !== 'function') throw new Error('Snapshot logger is required');
  const observe = async (initial = false) => {
    const s = await snapshot(page, {interactive: true});
    log(initial ? s.tree : s.diff);
    return s.tree;
  };
  const escape = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const ref = (tree, role, name) => {
    const re = new RegExp('^\\s*- ' + escape(role) + ' "' + escape(name) + '"[^\\n]*\\[ref=([^\\]]+)\\][^\\n]*$', 'gm');
    const matches = [...tree.matchAll(re)];
    return matches.length === 1 && !matches[0][0].includes('[disabled]') ? matches[0][1] : null;
  };
  const mode = tree => /radio "Video"[^\n]*\[checked\]/.test(tree) && /radio "Reference"[^\n]*\[checked\]/.test(tree) && !/radio "Keyframe"[^\n]*\[checked\]/.test(tree) && !/\b(?:Start|End) [Ff]rame\b/.test(tree);
  const slots = tree => [...tree.matchAll(/button "View Image (\d+) larger"/g)].map(m => Number(m[1]));
  const ordered = (tree, count) => JSON.stringify(slots(tree)) === JSON.stringify(Array.from({length:count}, (_, i) => i + 1));
  const currentText = locator => locator.evaluate(el => typeof el.value === 'string' ? el.value : el.innerText);
  // Aside page.url() can retain the initial newSession URL after the provider
  // assigns a sessionId. Bind identity to the fresh snapshot URL, not that cache.
  const observedUrl = tree => tree.match(/\[url=(https:\/\/app\.runwayml\.com\/[^\]\n]+)\]/)?.[1] ?? null;
  let tree = await observe(true);
  if (observedUrl(tree) !== job.expected_url) return result('SESSION_MISMATCH');
  if (job.action === 'REOBSERVE') return result('OBSERVED');
  if (!mode(tree)) return result('BLOCKED_REFERENCE_MODE_NOT_CONFIRMED');
  if (job.action === 'VERIFY_INPUTS') return result('OBSERVED', {reference_slots: slots(tree), final_approval: false});
  if (job.action === 'FILL_PROMPT' && /^\s*- (?:dialog|alertdialog)\b/m.test(tree)) return result('BLOCKING_DIALOG_CLOSE_AND_REOBSERVE');
  // The supplied gate is the preceding check.mjs mode result, not a Jev answer.
  if (job.action !== 'SEARCH_ASSET') {
    const at = Date.parse(job.mode_gate?.observed_at);
    if (job.mode_gate?.passed !== true || !Number.isFinite(at) || Date.now() - at < 0 || Date.now() - at > 30000) return result('MODE_GATE_REQUIRED');
  }
  try {
    if (job.action === 'SEARCH_ASSET') {
      if (typeof job.asset_name !== 'string' || !job.asset_name.trim() || job.asset_name.length > 255) return result('INVALID_ASSET_NAME');
      let search = ref(tree, 'textbox', 'Search');
      if (!search) {
        const control = ref(tree, 'button', 'Reference');
        if (!control) return result('SEARCH_ENTRY_NOT_OBSERVED');
        await page.locator(control).click();
        tree = await observe();
        if (observedUrl(tree) !== job.expected_url) return result('SESSION_MISMATCH');
        search = ref(tree, 'textbox', 'Search');
      }
      if (!search || !tree.includes('dialog "Asset selector"')) return result('SEARCH_NOT_OBSERVED');
      await page.locator(search).fill(job.asset_name);
      tree = await observe();
      if (observedUrl(tree) !== job.expected_url) return result('SESSION_MISMATCH_AFTER_ACTION');
      return result('SEARCH_OBSERVED', {selection_confirmed:false, empty_result_is_not_upload_permission:true});
    }
    if (job.action === 'SELECT_EXISTING') {
      if (job.binding_confirmed !== true || !['row','button','img'].includes(job.candidate?.role) || typeof job.candidate?.name !== 'string' || !Number.isInteger(job.expected_count) || job.expected_count < 1 || job.expected_count > 9) return result('ASSET_BINDING_REQUIRED');
      if (slots(tree).length >= job.expected_count) return result('REFERENCES_ALREADY_PRESENT_VERIFY');
      if (!ordered(tree, job.expected_count - 1) || !tree.includes('dialog "Asset selector"')) return result('SELECTION_STATE_MISMATCH');
      const candidate = ref(tree, job.candidate.role, job.candidate.name);
      if (!candidate) return result('CANDIDATE_NOT_UNIQUE');
      await page.locator(candidate).dblclick();
      tree = await observe();
      if (observedUrl(tree) !== job.expected_url) return result('SESSION_MISMATCH_AFTER_ACTION');
      return result(mode(tree) && ordered(tree, job.expected_count) ? 'REFERENCE_SLOT_ACCEPTED' : 'SELECTION_UNCONFIRMED', {reference_slots:slots(tree), identity_qc_proven:false});
    }
    if (job.action === 'FILL_PROMPT') {
      const verified = job.verified_submission, p = verified?.payload;
      if (verified?.language_status !== 'CURRENT_POLICY_VALIDATED') return result('CURRENT_LANGUAGE_CONTRACT_REQUIRED');
      if (verified?.state !== 'READY_FOR_PROVIDER_INPUT' || verified.stage !== 'seedance_prompt' || verified.provider !== 'runway_web' || !/^[a-f0-9]{64}$/.test(verified.payload_sha256 ?? '') || p?.required_author !== 'gpt-6-astra' || p.stage !== verified.stage || p.provider !== verified.provider || typeof p.prompt !== 'string' || !p.prompt.trim() || p.prompt !== p.prompt.normalize('NFC') || p.prompt.length > 3500 || !Array.isArray(p.references)) return result('VERIFIED_ASTRA_PAYLOAD_REQUIRED');
      if (!ordered(tree, p.references.length)) return result('REFERENCE_COUNT_MISMATCH');
      const promptRef = ref(tree, 'textbox', 'Prompt');
      if (!promptRef) return result('PROMPT_NOT_OBSERVED');
      const before = await currentText(page.locator(promptRef));
      if (before === p.prompt) return result('PROMPT_ALREADY_ACCEPTED', {characters:p.prompt.length});
      // Observed Runway empty contenteditable contains one LF. Normalize ONLY
      // this empty-editor comparison, never the bound author prompt.
      const observedBlank = job.expected_previous_prompt === '' && (before === '' || before === '\n');
      if (typeof job.expected_previous_prompt !== 'string' || (!observedBlank && before !== job.expected_previous_prompt)) return result('PRESERVE_EXISTING_PROMPT');
      await page.locator(promptRef).fill(p.prompt);
      tree = await observe();
      if (observedUrl(tree) !== job.expected_url || !mode(tree)) return result('MODE_OR_SESSION_CHANGED_AFTER_INPUT');
      const afterRef = ref(tree, 'textbox', 'Prompt');
      const after = afterRef ? await currentText(page.locator(afterRef)) : null;
      return result(after === p.prompt ? 'PROMPT_ACCEPTED' : 'PROMPT_UNCONFIRMED', {characters:after?.length ?? null, payload_sha256:verified.payload_sha256});
    }
    if (job.action === 'UPLOAD_FIRST') {
      if (job.search_absence_verified !== true || job.files_verified !== true || typeof claimUpload !== 'function' || !Number.isInteger(job.expected_existing_count) || !ordered(tree, job.expected_existing_count) || typeof job.observed_file_input_selector !== 'string' || !job.observed_file_input_selector || !Array.isArray(job.files) || !job.files.length || job.files.some(f => typeof f !== 'string' || !f.startsWith('/'))) return result('FIRST_UPLOAD_GATES_REQUIRED');
      // Selector must have been inspected in this exact live UI, NEVER supplied by Jev.
      const input = page.locator(job.observed_file_input_selector);
      if (await input.count() !== 1 || await input.getAttribute('type') !== 'file') return result('FILE_INPUT_NOT_UNIQUE');
      // Durable exclusive claim before dispatch. Retain it even on timeouts.
      if (await claimUpload({expected_url:job.expected_url, files:job.files}) !== true) return result('UPLOAD_ALREADY_ATTEMPTED_REOBSERVE');
      await input.setInputFiles(job.files);
      tree = await observe();
      return result('UPLOAD_DISPATCHED_UNCONFIRMED', {reference_slots:slots(tree), upload_success_proven:false});
    }
  } catch {
    // Timeouts can occur AFTER acceptance. Observe once, never repeat the action.
    try { await observe(); } catch { /* Browser unavailable. No retry. */ }
    return result('ACTION_UNCONFIRMED_REOBSERVE');
  }
  return result('UNSUPPORTED_ACTION');
}
