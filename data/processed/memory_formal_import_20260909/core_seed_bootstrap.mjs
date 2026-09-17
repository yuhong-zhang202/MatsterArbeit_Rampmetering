
import { spawn } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
const ids={team_id:'team-masterarbeit-ramp-metering',agent_id:'agent-project-memory',user_id:'user-yuhong-zhang'};
const key='formal-memory-core-seed-local-only';
const service='ramp-metering-formal-memory-v1';
const config=`deployMode: standalone
stateBackend: local
server: { port: 8420, host: 127.0.0.1, apiKey: ${key} }
data: { baseDir: /data/tdai-memory }
llm: { provider: openai, baseUrl: http://127.0.0.1:9/v1, apiKey: disabled, model: disabled, maxTokens: 1, timeoutMs: 1000 }
memory:
  capture: { enabled: false }
  extraction: { enabled: false }
  persona: { triggerEveryN: 1000000, maxScenes: 8 }
  pipeline: { everyNConversations: 1000000, enableWarmup: false, l1IdleTimeoutSeconds: 3600, l2DelayAfterL1Seconds: 3600, l2MinIntervalSeconds: 3600, l2MaxIntervalSeconds: 3601 }
  recall: { enabled: true, maxResults: 12, strategy: bm25, timeoutMs: 1000 }
  storeBackend: sqlite
  embedding: { provider: none }
skill: { enabled: false }
worker: { concurrency: 1 }
observability:
  otel: { enabled: false }
  langfuse: { enabled: false }
  kafka: { enabled: false }
  clickhouse: { enabled: false }
`;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function api(route,body){const r=await fetch('http://127.0.0.1:8420/v3/'+route,{method:'POST',headers:{'content-type':'application/json',authorization:'Bearer '+key,'x-tdai-service-id':service},body:JSON.stringify(body)});const x=await r.json();if(!r.ok||x.code!==0)throw Error(route+' '+r.status+' '+JSON.stringify(x));return x.data}
let gateway;
try{
  await writeFile('/tmp/core-seed.yaml',config);
  gateway=spawn('node',['--import','tsx','src/gateway/server.ts'],{cwd:'/app',env:{...process.env,TDAI_GATEWAY_CONFIG:'/tmp/core-seed.yaml',TDAI_GATEWAY_HOST:'127.0.0.1',TDAI_GATEWAY_API_KEY:key},stdio:['ignore','ignore','pipe']});
  let stderr='';gateway.stderr.on('data',c=>stderr+=c);
  for(let i=0;i<240;i++){try{if((await fetch('http://127.0.0.1:8420/health')).ok)break}catch{}if(i===239)throw Error('startup '+stderr.slice(-1000));await sleep(250)}
  const [l0,l1,l2,l3]=await Promise.all([api('conversation/query',{...ids,limit:10,offset:0}),api('atomic/query',{...ids,limit:50,offset:0}),api('scenario/ls',ids),api('core/read',ids)]);
  if(!(l0.total>0&&l1.total>0&&l2.total>0))throw Error('L0-L2 prerequisites missing');
  if(l3.content)throw Error('L3 already exists; refusing overwrite');
  const content=await readFile('/formal_core_memory.md','utf8');
  await api('core/write',{...ids,content});
  const after=await api('core/read',ids);
  if(!after.content||!after.content.includes('Masterarbeit-Ramp-Metering')||!after.content.includes('Robert Hilbrich'))throw Error('L3 verification failed');
  console.log(JSON.stringify({status:'passed',native_layers:{l0:l0.total,l1:l1.total,l2:l2.total,l3:true},core_chars:content.trim().length}));
}finally{if(gateway&&gateway.exitCode===null)gateway.kill('SIGTERM')}
