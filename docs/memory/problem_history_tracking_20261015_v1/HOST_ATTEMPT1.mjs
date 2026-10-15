import {execFile as execFileCallback} from 'node:child_process';
import {promisify} from 'node:util';
import {readFile,writeFile,mkdir,access} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
const execFile=promisify(execFileCallback);
const root=path.resolve(new URL('../..',import.meta.url).pathname);
const dir=path.join(root,'docs/memory/problem_history_tracking_20261015_v1');
const out=path.join(root,'data/processed/memory_problem_history_tracking_20261015_v1');
const docker='/opt/homebrew/bin/docker';
const name='tdai-ramp-reviewed-state-20261015-v1';
const image='sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const volume='tdai-ramp-metering-memory-v1';
const hash=x=>createHash('sha256').update(x).digest('hex');
const run=(args,opts={})=>execFile(docker,['--context','colima-memory-pilot',...args],{maxBuffer:20*1024*1024,timeout:180000,...opts});
if(process.argv.length!==3 || process.argv[2]!=='--execute')throw new Error('Use --execute only for the explicit model-free update');
const spec=JSON.parse(await readFile(path.join(dir,'UPDATE_SPEC.json'),'utf8'));
for(const item of [spec.scene,spec.core])if(hash(await readFile(path.join(root,item.file)))!==item.sha256)throw new Error('Candidate hash drift');
for(const [p,want] of Object.entries(spec.sources_sha256))if(hash(await readFile(path.join(root,p)))!==want)throw new Error('Source drift:'+p);
try{await access(path.join(out,'execution_receipt.json'));throw new Error('Receipt already exists; refuse repeat');}catch(e){if(e.code!=='ENOENT')throw e;}
await mkdir(out,{recursive:true});
const ledger=path.join(root,'data/processed/memory_formal_import_20260909/ledger_gpt-4.1-mini.json');
const ledgerBefore=hash(await readFile(ledger));let created=false;let result;let failure;
try{
 await run(['volume','inspect',volume]);await run(['image','inspect',image]);
 await run(['create','--name',name,'--pull=never','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,size=32m','--mount',`type=volume,source=${volume},target=/data`,'--entrypoint','node',image,'/update.mjs']);created=true;
 for(const [a,b] of [['scripts/memory/update_reviewed_state_container_20261015.mjs','/update.mjs'],['docs/memory/problem_history_tracking_20261015_v1/UPDATE_SPEC.json','/update_spec.json'],[spec.scene.file,'/new_scene.md'],[spec.core.file,'/new_core.md']])await run(['cp',path.join(root,a),name+':'+b]);
 let execution;try{execution=await run(['start','--attach',name]);}catch(e){execution={stdout:e.stdout||'',stderr:e.stderr||''};}
 const line=execution.stdout.trim().split('\n').filter(Boolean).at(-1);result=JSON.parse(line||'{}');
 for(const file of ['before.json','after.json','receipt.json'])await run(['cp',name+':/tmp/'+file,path.join(out,file)]).catch(()=>{});
 if(result.status!=='passed')throw new Error('Model-free write incomplete:'+JSON.stringify(result));
 await run(['rm','-f',name]);created=false;
 const fresh=await execFile(process.execPath,[path.join(root,'scripts/memory/read_formal_memory.mjs'),'--full'],{cwd:root,maxBuffer:20*1024*1024,timeout:240000});
 const readback=JSON.parse(fresh.stdout.trim().split('\n').filter(Boolean).at(-1));
 await writeFile(path.join(out,'fresh_network_disabled_readback.json'),JSON.stringify(readback,null,2),{flag:'wx'});
 if(readback.status!=='passed'||readback.network!=='none'||readback.hashes.l3!==result.after_hashes.l3||readback.hashes.l1!==result.after_hashes.l1||readback.hashes.l0!==result.after_hashes.l0||readback.hashes.l2_documents!==result.after_hashes.l2_documents)throw new Error('Fresh container readback mismatch');
 if(hash(await readFile(ledger))!==ledgerBefore)throw new Error('Paid request ledger drift');
}catch(e){failure=e.message;}finally{if(created)await run(['rm','-f',name]).catch(()=>{});}
const receipt={status:failure?'failed':'passed',date:'2026-10-15',network:'none',model_calls:0,paid_requests:0,ledger_sha256_before:ledgerBefore,ledger_sha256_after:hash(await readFile(ledger)),immediate:result||null,fresh_readback:!failure,error:failure||null};
await writeFile(path.join(out,'execution_receipt.json'),JSON.stringify(receipt,null,2),{flag:'wx'});
console.log(JSON.stringify(receipt));if(failure)process.exitCode=1;
