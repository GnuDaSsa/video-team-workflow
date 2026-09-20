import test from 'node:test';
import assert from 'node:assert/strict';
import { checkVideoMode } from './mode-lock.mjs';
const now = Date.now();
const packet = () => ({video_workspace:'Video',video_input_mode:'Reference',references:[],observed_settings:{observed_at:new Date(now).toISOString(),video_workspace:'Video',video_input_mode:'Reference',mode_selection_verified:true,keyframe_slots_visible:false}});
test('Reference selected in Video passes with zero reference images',()=>{assert.equal(checkVideoMode(packet(),now).ok,true);});
for (const [name,change,error] of [
 ['Keyframe selected',p=>p.observed_settings.video_input_mode='Keyframe','BLOCKED_REFERENCE_MODE_NOT_CONFIRMED'],
 ['wrong workspace',p=>p.observed_settings.video_workspace='Image','BLOCKED_WRONG_VIDEO_WORKSPACE'],
 ['mode label present but not selected',p=>p.observed_settings.mode_selection_verified=false,'BLOCKED_MODE_SELECTION_UNVERIFIED'],
 ['start/end keyframe slots despite Reference label',p=>p.observed_settings.keyframe_slots_visible=true,'BLOCKED_KEYFRAME_SLOTS_OR_UNKNOWN'],
 ['unknown keyframe slots',p=>delete p.observed_settings.keyframe_slots_visible,'BLOCKED_KEYFRAME_SLOTS_OR_UNKNOWN'],
 ['missing mode',p=>delete p.observed_settings.video_input_mode,'BLOCKED_REFERENCE_MODE_NOT_CONFIRMED'],
 ['stale observation',p=>p.observed_settings.observed_at=new Date(now-31000).toISOString(),'FRESH_MODE_OBSERVATION_REQUIRED'],
 ['future observation',p=>p.observed_settings.observed_at=new Date(now+5000).toISOString(),'FRESH_MODE_OBSERVATION_REQUIRED'],
 ['package attempts Keyframe',p=>p.video_input_mode='Keyframe','REFERENCE_MODE_LOCK_REQUIRED'],
 ['package omits lock',p=>delete p.video_input_mode,'REFERENCE_MODE_LOCK_REQUIRED'],
]) test(name+' is blocked',()=>{const p=packet();change(p);const r=checkVideoMode(p,now);assert.equal(r.ok,false);assert.ok(r.errors.includes(error));});
test('missing observation fails closed',()=>{const p=packet();delete p.observed_settings;assert.equal(checkVideoMode(p,now).ok,false);});
