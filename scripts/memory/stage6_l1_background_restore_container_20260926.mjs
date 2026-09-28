import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';

const spec = JSON.parse(await readFile('/correction_spec.json', 'utf8'));
const ids = { team_id: spec.team_id, agent_id: spec.agent_id, user_id: spec.user_id };
const key = 'formal-memory-l1-background-restore-local-only';
const sha = text => createHash('sha256').update(text).digest('hex');
const config = `deployMode: standalone
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
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function api(route, body) {
  const response = await fetch(`http://127.0.0.1:8420/v3/${route}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization: `Bearer ${key}`, 'x-tdai-service-id': spec.service_id },
    body: JSON.stringify(body), signal: AbortSignal.timeout(10000),
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0) throw new Error(`${route}: ${response.status} ${JSON.stringify(result)}`);
  return result.data;
}
let gateway;
let applied = false;
try {
  if (spec.correction_id !== 'stage6-content-correction-20260926-v1' || !spec.no_model_calls) throw new Error('Correction identity/policy mismatch');
  await writeFile('/tmp/tdai-l1-background-restore.yaml', config, { flag: 'wx', mode: 0o600 });
  gateway = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app', env: { ...process.env, TDAI_GATEWAY_CONFIG: '/tmp/tdai-l1-background-restore.yaml', TDAI_GATEWAY_HOST: '127.0.0.1', TDAI_GATEWAY_API_KEY: key },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  for (let i = 0; i < 240; i++) {
    try { if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(300) })).ok) break; } catch {}
    if (i === 239) throw new Error('Gateway startup timeout');
    await sleep(250);
  }
  const beforeQuery = await api('atomic/query', { ...ids, limit: 100, offset: 0 });
  const before = beforeQuery.items.find(item => item.id === spec.atomic.id);
  if (!before || before.version !== 1 || sha(before.content) !== spec.atomic.new_content_sha256
    || before.background !== 'I am assisting Yuhong Zhang in formalizing and preserving project memory for the Masterarbeit Ramp Metering research') {
    throw new Error('L1 side-effect precondition failed; refusing write');
  }
  const response = await api('atomic/update', { ...ids, id: spec.atomic.id, content: spec.atomic.new_content, background: spec.atomic.background });
  applied = true;
  const afterQuery = await api('atomic/query', { ...ids, limit: 100, offset: 0 });
  const after = afterQuery.items.find(item => item.id === spec.atomic.id);
  if (!after || after.version !== 2 || sha(after.content) !== spec.atomic.new_content_sha256 || after.background !== spec.atomic.background
    || afterQuery.total !== beforeQuery.total) throw new Error('L1 background restore readback mismatch');
  const beforeOther = beforeQuery.items.filter(item => item.id !== spec.atomic.id);
  const afterOther = afterQuery.items.filter(item => item.id !== spec.atomic.id);
  if (JSON.stringify(beforeOther) !== JSON.stringify(afterOther)) throw new Error('Unrelated L1 records changed');
  console.log(JSON.stringify({ status: 'passed', network: 'none', model_calls: 0, route: 'atomic/update',
    id: spec.atomic.id, before: { version: before.version, background: before.background, content_sha256: sha(before.content) },
    write_response: response,
    after: { version: after.version, background: after.background, content_sha256: sha(after.content) },
    l1_total: afterQuery.total }));
} catch (error) {
  console.log(JSON.stringify({ status: 'failed', applied, error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
