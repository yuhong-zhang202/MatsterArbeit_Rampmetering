import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { writeFile } from 'node:fs/promises';

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
  const nativeLayers = { l0: l0.total, l1: l1.total, l2: l2Index.total, l3: Boolean(l3.content) };
  if (!(l0.total > 0 && l1.total > 0 && l2Index.total > 0 && l3.content)) {
    console.log(JSON.stringify({ status: 'incomplete', native_layers: nativeLayers }));
    process.exitCode = 2;
  } else {
    const combined = JSON.stringify({ l0, l1, l2, l3 }).toLowerCase();
    if (!combined.includes('masterarbeit-ramp-metering') || !combined.includes('robert hilbrich')) {
      throw new Error('Persisted content identity check failed');
    }
    const result = { status: 'passed', native_layers: nativeLayers, hashes: { l0: digest(l0), l1: digest(l1), l2: digest(l2Index), l2_documents: digest(l2Documents), l3: digest(l3.content) } };
    if (process.env.FORMAL_MEMORY_OUTPUT === 'full') {
      result.memory = { l1, l2, l3 };
      result.notice = 'Auxiliary memory only; current repository documents remain authoritative.';
    }
    console.log(JSON.stringify(result));
  }
} catch (error) {
  console.log(JSON.stringify({ status: 'failed', error: error instanceof Error ? error.message : String(error), gateway_stderr_tail: stderr.slice(-2000) }));
  process.exitCode = 1;
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
