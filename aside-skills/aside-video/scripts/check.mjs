#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { checkVideoMode } from './mode-lock.mjs';
const harnessPath = fileURLToPath(new URL('./harness.mjs', import.meta.url));
const submissionPath = fileURLToPath(new URL('./submission.mjs', import.meta.url));
const referenceBundlePath = fileURLToPath(new URL('./seedance-references.mjs', import.meta.url));
const [mode, input] = process.argv.slice(2);
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
try {
  if (mode === 'mode') {
    const result = checkVideoMode(JSON.parse(fs.readFileSync(path.resolve(input), 'utf8')));
    console.log(JSON.stringify(result, null, 2)); process.exitCode = result.ok ? 0 : 1;
  } else if (mode === 'preflight') {
    const file = path.resolve(input);
    const p = JSON.parse(fs.readFileSync(file, 'utf8'));
    const promptPath = path.resolve(path.dirname(file), p.prompt_file);
    const prompt = fs.readFileSync(promptPath, 'utf8');
    const errors = [...checkVideoMode(p).errors];
    if (p.harness_policy_version !== 1 || p.execution_model !== 'inherit_session') errors.push('HARNESS_POLICY_REQUIRED');
    const handoffs = p.author_handoffs;
    if (!Array.isArray(handoffs) || !handoffs.length) errors.push('ASTRA_HANDOFFS_REQUIRED');
    let seedanceBound = false;
    for (const h of Array.isArray(handoffs) ? handoffs : []) {
      if (!h || typeof h.receipt !== 'string' || !/^[a-f0-9]{64}$/.test(h.sha256 || '')) { errors.push('INVALID_AUTHOR_HANDOFF'); continue; }
      const receiptPath = path.resolve(path.dirname(file), h.receipt);
      const verified = spawnSync(process.execPath, [harnessPath, 'verify', receiptPath, '--sha256', h.sha256], { encoding:'utf8', timeout:30000, shell:false });
      if (verified.error || verified.status !== 0) { errors.push('AUTHOR_HANDOFF_FAILED:' + h.receipt); continue; }
      const receipt = JSON.parse(fs.readFileSync(receiptPath, 'utf8'));
      if (receipt.stage === 'seedance_prompt') {
        if (receipt.prompt?.sha256 === p.prompt_sha256) seedanceBound = true;
        else errors.push('SEEDANCE_AUTHOR_PROMPT_MISMATCH');
      }
    }
    if (!seedanceBound) errors.push('SEEDANCE_ASTRA_HANDOFF_REQUIRED');
    let boundReferences = null;
    if (Object.hasOwn(p, 'reference_bundle')) {
      const link = p.reference_bundle;
      if (!link || typeof link.path !== 'string' || !/^[a-f0-9]{64}$/.test(link.sha256 || '')) errors.push('INVALID_REFERENCE_BUNDLE_LINK');
      else {
        const bundleFile = path.resolve(path.dirname(file), link.path);
        const checkedBundle = spawnSync(process.execPath, [referenceBundlePath, 'verify', bundleFile, '--sha256', link.sha256], {encoding:'utf8',timeout:30000,shell:false});
        if (checkedBundle.error || checkedBundle.status !== 0) errors.push('REFERENCE_BUNDLE_VERIFICATION_FAILED');
        else {
          boundReferences = JSON.parse(fs.readFileSync(path.join(path.dirname(bundleFile), 'references.json'), 'utf8'));
          if (!isDeepStrictEqual(p.references, boundReferences)) errors.push('REFERENCE_BUNDLE_PACKAGE_MISMATCH');
        }
      }
    }
    const payloadLink = p.provider_payload;
    if (!payloadLink || typeof payloadLink.path !== 'string' || !/^[a-f0-9]{64}$/.test(payloadLink.sha256 || '')) errors.push('VERIFIED_PROVIDER_PAYLOAD_REQUIRED');
    else {
      const payloadFile = path.resolve(path.dirname(file), payloadLink.path);
      const verifiedPayload = spawnSync(process.execPath, [submissionPath, 'verify', payloadFile, '--sha256', payloadLink.sha256], {encoding:'utf8',timeout:30000,shell:false});
      if (verifiedPayload.error || verifiedPayload.status !== 0) errors.push('PROVIDER_PAYLOAD_VERIFICATION_FAILED');
      else {
        const verifiedLanguage = JSON.parse(verifiedPayload.stdout);
        if (verifiedLanguage.language_status !== 'CURRENT_POLICY_VALIDATED') errors.push('CURRENT_LANGUAGE_CONTRACT_REQUIRED');
        if (verifiedLanguage.knowledge_status !== 'CURRENT_KNOWLEDGE_VALIDATED') errors.push('CURRENT_KNOWLEDGE_REQUIRED');
        const payload = JSON.parse(fs.readFileSync(payloadFile, 'utf8'));
        if (verifiedLanguage.language_status === 'CURRENT_POLICY_VALIDATED' && p.prompt_language && p.prompt_language !== payload.language_contract?.language) errors.push('PACKAGE_LANGUAGE_CONTRACT_MISMATCH');
        if (payload.stage !== 'seedance_prompt' || payload.provider !== 'runway_web' || payload.prompt_sha256 !== p.prompt_sha256 || payload.prompt !== prompt) errors.push('PROVIDER_PAYLOAD_PROMPT_OR_STAGE_MISMATCH');
        if (boundReferences !== null && !isDeepStrictEqual(payload.references, boundReferences)) errors.push('REFERENCE_BUNDLE_PAYLOAD_MISMATCH');
      }
    }
    if (!prompt.trim() || prompt !== prompt.normalize('NFC') || [...prompt].length > 3500) errors.push('PROMPT_EMPTY_NON_NFC_OR_OVER_LIMIT');
    if (hash(promptPath) !== p.prompt_sha256) errors.push('PROMPT_HASH_MISMATCH');
    if (!Number.isInteger(p.duration_sec) || p.duration_sec < 5 || p.duration_sec > 15) errors.push('INVALID_DURATION');
    if (!Array.isArray(p.references)) errors.push('ORDERED_REFERENCES_REQUIRED');
    if (p.generation_mode !== 'no_i2v_reference_native') errors.push('EXPECTED_NO_I2V');
    if (!p.observed_settings || Date.now() - Date.parse(p.observed_settings.observed_at) > 120000 || !Number.isFinite(Date.parse(p.observed_settings?.observed_at))) errors.push('FRESH_UI_OBSERVATION_REQUIRED');
    for (const key of ['provider_model', 'duration_sec', 'aspect_ratio', 'resolution', 'audio']) {
      if (p.observed_settings?.[key] !== p[key]) errors.push('UI_MISMATCH:' + key);
    }
    if (p.observed_settings?.reference_count !== p.references?.length) errors.push('REFERENCE_COUNT_MISMATCH');
    const result = { ok: !errors.length, errors, prompt_sha256: hash(promptPath), prompt_characters: [...prompt].length, checks: 'local_package_consistency_only_not_browser_or_quality_proof' };
    console.log(JSON.stringify(result, null, 2)); process.exitCode = result.ok ? 0 : 1;
  } else if (mode === 'media') {
    const file = path.resolve(input);
    if (!fs.statSync(file).isFile()) throw new Error('MEDIA_FILE_REQUIRED');
    const ffprobe = fs.existsSync('/opt/homebrew/bin/ffprobe') ? '/opt/homebrew/bin/ffprobe' : 'ffprobe';
    const result = spawnSync(ffprobe, ['-v','error','-show_format','-show_streams','-of','json',file], { encoding:'utf8',timeout:30000,shell:false });
    if (result.error || result.status) throw new Error(result.error?.message || result.stderr || 'FFPROBE_FAILED');
    const data = JSON.parse(result.stdout);
    const video = data.streams?.find(s => s.codec_type === 'video');
    if (!video) throw new Error('VIDEO_STREAM_REQUIRED');
    const duration = Number(data.format?.duration || video.duration);
    if (!Number.isFinite(duration) || duration <= 0) throw new Error('POSITIVE_DURATION_REQUIRED');
    console.log(JSON.stringify({ ok:true,file,bytes:fs.statSync(file).size,sha256:hash(file),duration_sec:duration,width:video.width,height:video.height,codec:video.codec_name,frame_rate:video.avg_frame_rate,audio:data.streams.filter(s=>s.codec_type==='audio').map(s=>({codec:s.codec_name,sample_rate:s.sample_rate,channels:s.channels})),checks:'technical_file_verification_only',visual_qc:'NOT_ASSESSED',audio_listening_qc:'NOT_ASSESSED'},null,2));
  } else {
    console.log('Usage: node check.mjs mode <package.json> | preflight <package.json> | media <video.mp4>');
    if (mode && !['--help','-h'].includes(mode)) process.exitCode=2;
  }
} catch(error) { console.log(JSON.stringify({ok:false,error:error.message})); process.exitCode=2; }
