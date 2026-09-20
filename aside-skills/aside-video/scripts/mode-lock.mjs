// Local UI-observation consistency gate, not a browser controller or live UI proof.
export const VIDEO_MODE_LOCK = Object.freeze({ workspace: 'Video', input_mode: 'Reference', max_age_ms: 30000 });
export function checkVideoMode(p, now = Date.now()) {
  const errors = [];
  const o = p?.observed_settings;
  if (p?.video_workspace !== VIDEO_MODE_LOCK.workspace || p?.video_input_mode !== VIDEO_MODE_LOCK.input_mode) errors.push('REFERENCE_MODE_LOCK_REQUIRED');
  const stamp = Date.parse(o?.observed_at);
  if (!Number.isFinite(stamp) || stamp > now + 1000 || now - stamp > VIDEO_MODE_LOCK.max_age_ms) errors.push('FRESH_MODE_OBSERVATION_REQUIRED');
  if (o?.video_workspace !== VIDEO_MODE_LOCK.workspace) errors.push('BLOCKED_WRONG_VIDEO_WORKSPACE');
  if (o?.video_input_mode !== VIDEO_MODE_LOCK.input_mode) errors.push('BLOCKED_REFERENCE_MODE_NOT_CONFIRMED');
  if (o?.mode_selection_verified !== true) errors.push('BLOCKED_MODE_SELECTION_UNVERIFIED');
  if (o?.keyframe_slots_visible !== false) errors.push('BLOCKED_KEYFRAME_SLOTS_OR_UNKNOWN');
  return { ok: errors.length === 0, errors, required: VIDEO_MODE_LOCK, checks: 'local_observation_consistency_only_not_live_browser_proof' };
}
