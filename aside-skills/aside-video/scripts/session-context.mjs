#!/usr/bin/env node
// Read-only runtime lookup. Never edits model/settings or starts a session.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const accountRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');
const [sessionId,flag,out] = process.argv.slice(2);
try {
  if (!/^[A-Za-z0-9_-]+$/.test(sessionId??'') || flag!=='--out' || !out || process.argv.length!==5) throw new Error('Usage: node session-context.mjs <current-session-id> --out <context.json>');
  const query=`select model from sessions where id='${sessionId}';`;
  const read=spawnSync('/usr/bin/sqlite3',['-readonly',path.join(accountRoot,'state.db'),query],{encoding:'utf8',shell:false});
  if (read.error || read.status!==0 || !read.stdout.trim()) throw new Error('CURRENT_SESSION_MODEL_NOT_FOUND');
  const model=JSON.parse(read.stdout);
  const settings=JSON.parse(fs.readFileSync(path.join(accountRoot,'settings.json'),'utf8'));
  const context={session_id:sessionId,model,modelCategories:settings.modelCategories??{},observed_at:new Date().toISOString(),evidence:'read_only_session_configuration_not_actual_author_response'};
  fs.writeFileSync(path.resolve(out),JSON.stringify(context,null,2)+'\n',{flag:'wx',mode:0o600});
  console.log(JSON.stringify({ok:true,file:path.resolve(out),session_id:sessionId,model,settings_changed:false},null,2));
} catch(e) {console.error(e.message);process.exitCode=1;}
