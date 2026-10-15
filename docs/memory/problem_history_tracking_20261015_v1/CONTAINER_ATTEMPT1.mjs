import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';

const ids = {
  team_id: 'team-masterarbeit-ramp-metering',
  agent_id: 'agent-project-memory',
  user_id: 'user-yuhong-zhang',
};
const gatewayKey = 'formal-memory-read-local-only';
const config = `deployMode: standalone
stateBackend: local
server: { port: 8420, host: 127.0.0.1, apiKey: ${gatewayKey} }
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
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const digest = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
async function api(route, body) {
  const response = await fetch(`http://127.0.0.1:8420/v3/${route}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization: `Bearer ${gatewayKey}`, 'x-tdai-service-id': 'ramp-metering-formal-memory-v1' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(10000),
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0) throw new Error(`${route} failed: ${response.status} ${JSON.stringify(result)}`);
  return result.data;
}
let gateway;
let stderr = '';
try {
  await writeFile('/tmp/tdai-formal-probe.yaml', config, { flag: 'w', mode: 0o600 });
  gateway = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app',
    env: { ...process.env, TDAI_GATEWAY_CONFIG: '/tmp/tdai-formal-probe.yaml', TDAI_GATEWAY_HOST: '127.0.0.1', TDAI_GATEWAY_API_KEY: gatewayKey },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  gateway.stderr.on('data', chunk => { stderr += chunk; });
  for (let i = 0; i < 240; i++) {
    try { if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(300) })).ok) break; } catch {}
    if (i === 239) throw new Error(`gateway startup timeout: ${stderr.slice(-2000)}`);
    await sleep(250);
  }
  const [l0, l1, l2Index, l3] = await Promise.all([
    api('conversation/query', { ...ids, limit: 10, offset: 0 }),
    api('atomic/query', { ...ids, limit: 50, offset: 0 }),
    api('scenario/ls', { ...ids }),
    api('core/read', { ...ids }),
  ]);
  const scenarioEntries = Array.isArray(l2Index.entries)
    ? l2Index.entries.filter(entry => typeof entry?.path === 'string' && !entry.path.endsWith('/'))
    : [];
  if (scenarioEntries.length > 50) throw new Error('Refusing to read more than 50 L2 scenario documents');
  const l2Documents = await Promise.all(scenarioEntries.map(entry => api('scenario/read', { ...ids, path: entry.path })));
  const l2 = { index: l2Index, documents: l2Documents };
  const spec = JSON.parse(await readFile('/update_spec.json', 'utf8'));
  const newScene = await readFile('/new_scene.md', 'utf8');
  const newCore = await readFile('/new_core.md', 'utf8');
  const byteHash = text => createHash('sha256').update(text).digest('hex');
  if (spec.network !== 'none' || spec.model_calls !== 0 || spec.authorization !== 'direct-user-model-free-memory-update-20261015') throw new Error('Unsupported update authority');
  if (byteHash(newScene) !== spec.scene.sha256 || byteHash(newCore) !== spec.core.sha256) throw new Error('Candidate drift');
  const before = { l0, l1, l2, l3 };
  const beforeHashes = {l0:digest(l0),l1:digest(l1),l2:digest(l2Index),l2_documents:digest(l2Documents),l3:digest(l3.content)};
  for (const [key, expected] of Object.entries(spec.expected_before)) if (beforeHashes[key] !== expected) throw new Error(`Prewrite drift:${key}`);
  if (l2Documents.some(item => item.path === spec.scene.path)) throw new Error('Scene already exists; no duplicate update');
  await writeFile('/tmp/before.json', JSON.stringify(before,null,2), {flag:'wx'});
  const sceneWrite = await api('scenario/write', {...ids,path:spec.scene.path,content:newScene,summary:spec.scene.summary});
  const coreWrite = await api('core/write', {...ids,content:newCore});
  const [newL0,newL1,newIndex,newL3] = await Promise.all([
    api('conversation/query',{...ids,limit:10,offset:0}),api('atomic/query',{...ids,limit:50,offset:0}),api('scenario/ls',{...ids}),api('core/read',{...ids})]);
  const entries = newIndex.entries.filter(x=>typeof x.path==='string'&&!x.path.endsWith('/'));
  const newDocs = await Promise.all(entries.map(x=>api('scenario/read',{...ids,path:x.path})));
  if (digest(newL0)!==beforeHashes.l0 || digest(newL1)!==beforeHashes.l1) throw new Error('Append-only history changed');
  for (const oldDoc of l2Documents) if (JSON.stringify(oldDoc)!==JSON.stringify(newDocs.find(x=>x.path===oldDoc.path))) throw new Error(`Old scenario changed:${oldDoc.path}`);
  const stripMeta = text=>text.replace(/^-----META-START-----\n[\s\S]*?\n-----META-END-----\n\n/,'');
  const current = newDocs.find(x=>x.path===spec.scene.path);
  if (newIndex.total!==l2Index.total+1 || !current || stripMeta(current.content).trim()!==newScene.trim() || newL3.content.trim()!==newCore.trim()) throw new Error('New content readback mismatch');
  const after = {l0:newL0,l1:newL1,l2:{index:newIndex,documents:newDocs},l3:newL3};
  await writeFile('/tmp/after.json',JSON.stringify(after,null,2),{flag:'wx'});
  const receipt={status:'passed',network:'none',model_calls:0,paid_requests:0,identity:ids,service_id:'ramp-metering-formal-memory-v1',
    writes:[{layer:'L2',path:spec.scene.path,version:sceneWrite.version},{layer:'L3',version:coreWrite.version}],
    before_hashes:beforeHashes,after_hashes:{l0:digest(newL0),l1:digest(newL1),l2:digest(newIndex),l2_documents:digest(newDocs),l3:digest(newL3.content)},
    counts_before:{l0:l0.total,l1:l1.total,l2:l2Index.total},counts_after:{l0:newL0.total,l1:newL1.total,l2:newIndex.total},
    old_scenarios_unchanged:true,history_L0_L1_unchanged:true,new_L1_extraction:false,scene_sha256:byteHash(newScene),core_sha256:byteHash(newCore)};
  await writeFile('/tmp/receipt.json',JSON.stringify(receipt,null,2),{flag:'wx'});
  console.log(JSON.stringify(receipt));
} catch (error) {
  console.log(JSON.stringify({ status: 'failed', error: error instanceof Error ? error.message : String(error), gateway_stderr_tail: stderr.slice(-2000) }));
  process.exitCode = 1;
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
