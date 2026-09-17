import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { writeFile } from 'node:fs/promises';

const proxyBaseUrl = process.env.PILOT_PROXY_BASE_URL;
const proxyClientKey = process.env.PILOT_PROXY_CLIENT_KEY;
if (!proxyBaseUrl || !proxyClientKey) throw new Error('Pilot proxy configuration is missing');

const config = `deployMode: standalone
stateBackend: local
server:
  port: 8420
  host: 127.0.0.1
  apiKey: synthetic-gateway-local-only
data:
  baseDir: /data/tdai-memory
llm:
  provider: openai
  baseUrl: ${proxyBaseUrl}
  apiKey: ${proxyClientKey}
  model: gpt-4.1-mini-2025-04-14
  maxTokens: 4096
  timeoutMs: 120000
memory:
  capture: { enabled: true }
  extraction:
    enabled: true
    enableDedup: false
    maxMemoriesPerSession: 5
  persona:
    triggerEveryN: 1
    maxScenes: 5
  pipeline:
    everyNConversations: 1
    enableWarmup: true
    l1IdleTimeoutSeconds: 1
    l2DelayAfterL1Seconds: 1
    l2MinIntervalSeconds: 1
    l2MaxIntervalSeconds: 2
  recall:
    enabled: true
    maxResults: 5
    strategy: bm25
    timeoutMs: 1000
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
    headers: {
      'content-type': 'application/json',
      authorization: 'Bearer synthetic-gateway-local-only',
      'x-tdai-service-id': 'ramp-memory-paid-synthetic-pilot',
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(5000),
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0) {
    throw new Error(`${route} failed: ${response.status} ${JSON.stringify(result)}`);
  }
  return result.data;
}

function digest(value) {
  return createHash('sha256').update(typeof value === 'string' ? value : JSON.stringify(value)).digest('hex');
}

let gateway;
let failure;
let stderr = '';
const beganAt = new Date().toISOString();
try {
  await writeFile('/tmp/tdai-paid-synthetic.yaml', config, { flag: 'w', mode: 0o600 });
  gateway = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app',
    env: {
      ...process.env,
      TDAI_GATEWAY_CONFIG: '/tmp/tdai-paid-synthetic.yaml',
      TDAI_GATEWAY_HOST: '127.0.0.1',
      TDAI_GATEWAY_API_KEY: 'synthetic-gateway-local-only',
    },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  gateway.stderr.on('data', chunk => { stderr += chunk; });
  for (let i = 0; i < 240; i++) {
    try {
      if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(300) })).ok) break;
    } catch {}
    if (i === 239) throw new Error(`gateway startup timeout: ${stderr.slice(-2000)}`);
    await sleep(250);
  }

  const ids = {
    team_id: 'team-ramp-paid-synthetic-20260909',
    agent_id: 'agent-ramp-paid-synthetic-20260909',
    user_id: 'user-ramp-paid-synthetic-20260909',
  };
  const syntheticMessages = [
    { role: 'user', content: '完全虚构的隔离测试：蓝色方案已批准，红色方案仍待确认。' },
    { role: 'assistant', content: '已记录虚构测试状态，不作真实项目结论。' },
  ];
  await api('conversation/add', {
    ...ids,
    session_id: 'synthetic-paid-layered-session-20260909',
    messages: syntheticMessages,
  });

  let same;
  for (let i = 0; i < 240; i++) {
    const [atomic, scenes, core] = await Promise.all([
      api('atomic/query', { ...ids, limit: 20, offset: 0 }),
      api('scenario/ls', { ...ids }),
      api('core/read', { ...ids }),
    ]);
    same = { atomic, scenes, core };
    if ((atomic.total ?? 0) > 0 && (scenes.total ?? 0) > 0 && core.content) break;
    await sleep(1000);
  }
  if (!(same?.atomic?.total > 0)) throw new Error('L1 did not materialize within four minutes');
  if (!(same?.scenes?.total > 0)) throw new Error('L2 did not materialize within four minutes');
  if (!same?.core?.content) throw new Error('L3 did not materialize within four minutes');

  const otherIds = {
    team_id: 'team-other-paid-synthetic-20260909',
    agent_id: 'agent-other-paid-synthetic-20260909',
    user_id: 'user-other-paid-synthetic-20260909',
  };
  const [otherL0, otherL1, otherL2, otherL3] = await Promise.all([
    api('conversation/query', { ...otherIds, limit: 20, offset: 0 }),
    api('atomic/query', { ...otherIds, limit: 20, offset: 0 }),
    api('scenario/ls', { ...otherIds }),
    api('core/read', { ...otherIds }),
  ]);
  const crossProjectEmpty = (otherL0.total ?? 0) === 0
    && (otherL1.total ?? 0) === 0
    && (otherL2.total ?? 0) === 0
    && otherL3.content === null;
  if (!crossProjectEmpty) throw new Error('cross-project isolation query was not empty');

  console.log(JSON.stringify({
    status: 'passed',
    began_at: beganAt,
    finished_at: new Date().toISOString(),
    synthetic_input_sha256: digest(syntheticMessages),
    native_layers: {
      l0: syntheticMessages.length,
      l1: same.atomic.total,
      l2: same.scenes.total,
      l3: Boolean(same.core.content),
    },
    output_hashes: {
      l1_sha256: digest(same.atomic),
      l2_sha256: digest(same.scenes),
      l3_sha256: digest(same.core.content),
    },
    cross_project_empty: true,
  }));
} catch (error) {
  failure = error;
  console.log(JSON.stringify({
    status: 'failed',
    began_at: beganAt,
    finished_at: new Date().toISOString(),
    error: error instanceof Error ? error.message : String(error),
    gateway_stderr_tail: stderr.slice(-2000),
  }));
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
if (failure) process.exitCode = 1;
