import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';

const proxyBaseUrl = process.env.MEMORY_PROXY_BASE_URL;
const proxyClientKey = process.env.MEMORY_PROXY_CLIENT_KEY;
if (!proxyBaseUrl || !proxyClientKey) throw new Error('Memory proxy configuration is missing');

const ids = {
  team_id: 'team-masterarbeit-ramp-metering',
  agent_id: 'agent-project-memory',
  user_id: 'user-yuhong-zhang',
};
const sessionId = 'formal-project-seed-20260909-v1';
const gatewayKey = 'formal-memory-gateway-local-only';
const serviceId = 'ramp-metering-formal-memory-v1';

const config = `deployMode: standalone
stateBackend: local
server:
  port: 8420
  host: 127.0.0.1
  apiKey: ${gatewayKey}
data:
  baseDir: /data/tdai-memory
llm:
  provider: openai
  baseUrl: ${proxyBaseUrl}
  apiKey: ${proxyClientKey}
  model: gpt-4.1-mini
  maxTokens: 4096
  timeoutMs: 120000
memory:
  capture: { enabled: true }
  extraction:
    enabled: true
    enableDedup: false
    maxMemoriesPerSession: 12
  persona:
    triggerEveryN: 1
    maxScenes: 8
  pipeline:
    everyNConversations: 1
    enableWarmup: true
    l1IdleTimeoutSeconds: 1
    l2DelayAfterL1Seconds: 1
    l2MinIntervalSeconds: 1
    l2MaxIntervalSeconds: 2
  recall:
    enabled: true
    maxResults: 12
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
const digest = value => createHash('sha256')
  .update(typeof value === 'string' ? value : JSON.stringify(value)).digest('hex');

function splitByParagraph(text, maxChars = 7200) {
  const chunks = [];
  let current = '';
  for (const paragraph of text.split('\n\n')) {
    const candidate = current ? `${current}\n\n${paragraph}` : paragraph;
    if (candidate.length <= maxChars) {
      current = candidate;
      continue;
    }
    if (current) chunks.push(current);
    if (paragraph.length > maxChars) throw new Error('One import-bundle paragraph exceeds the L0 chunk limit');
    current = paragraph;
  }
  if (current) chunks.push(current);
  return chunks;
}

async function api(route, body) {
  const response = await fetch(`http://127.0.0.1:8420/v3/${route}`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${gatewayKey}`,
      'x-tdai-service-id': serviceId,
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(10000),
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0) {
    throw new Error(`${route} failed: ${response.status} ${JSON.stringify(result)}`);
  }
  return result.data;
}

let gateway;
let failure;
let stderr = '';
const beganAt = new Date().toISOString();
try {
  const bundle = await readFile('/formal_import_bundle.md', 'utf8');
  if (!bundle.includes('Project identity: `Masterarbeit-Ramp-Metering`')) {
    throw new Error('Formal import bundle project identity mismatch');
  }
  await writeFile('/tmp/tdai-formal-memory.yaml', config, { flag: 'w', mode: 0o600 });
  gateway = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app',
    env: {
      ...process.env,
      TDAI_GATEWAY_CONFIG: '/tmp/tdai-formal-memory.yaml',
      TDAI_GATEWAY_HOST: '127.0.0.1',
      TDAI_GATEWAY_API_KEY: gatewayKey,
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

  const before = await api('conversation/query', { ...ids, limit: 10, offset: 0 });
  if ((before.total ?? 0) !== 0) throw new Error('Target project identity is not empty; refusing duplicate seed');

  const chunks = splitByParagraph(bundle);
  const messages = chunks.flatMap((chunk, index) => [{
    role: 'user',
    content: `Reviewed project-memory seed, part ${index + 1}/${chunks.length}. Preserve approval levels, uncertainty, source authority and next-action boundaries exactly.\n\n${chunk}`,
  }, {
    role: 'assistant',
    content: index + 1 === chunks.length
      ? 'Recorded the complete auxiliary project-memory seed. Repository documents remain authoritative and later versions supersede stale memory.'
      : `Recorded part ${index + 1}/${chunks.length}; awaiting the remaining reviewed seed content.`,
  }]);
  await api('conversation/add', { ...ids, session_id: sessionId, messages });

  let layers;
  for (let i = 0; i < 480; i++) {
    const [l0, l1, l2, l3] = await Promise.all([
      api('conversation/query', { ...ids, limit: 10, offset: 0 }),
      api('atomic/query', { ...ids, limit: 50, offset: 0 }),
      api('scenario/ls', { ...ids }),
      api('core/read', { ...ids }),
    ]);
    layers = { l0, l1, l2, l3 };
    if ((l0.total ?? 0) > 0 && (l1.total ?? 0) > 0 && (l2.total ?? 0) > 0 && l3.content) break;
    await sleep(1000);
  }
  if (!(layers?.l0?.total > 0)) throw new Error('L0 was not persisted');
  if (!(layers?.l1?.total > 0)) throw new Error('L1 did not materialize within eight minutes');
  if (!(layers?.l2?.total > 0)) throw new Error('L2 did not materialize within eight minutes');
  if (!layers?.l3?.content) throw new Error('L3 did not materialize within eight minutes');

  const combined = JSON.stringify(layers).toLowerCase();
  const checks = {
    project_identity: combined.includes('masterarbeit-ramp-metering'),
    research_focus: combined.includes('sweet spot') || combined.includes('sweet-spot'),
    supervisor: combined.includes('robert hilbrich'),
    protocol_boundary: combined.includes('formal protocol') || combined.includes('experiment protocol'),
  };
  if (!Object.values(checks).every(Boolean)) {
    throw new Error(`Layered semantic checks failed: ${JSON.stringify(checks)}`);
  }

  const otherIds = {
    team_id: 'team-memory-isolation-probe',
    agent_id: 'agent-memory-isolation-probe',
    user_id: 'user-memory-isolation-probe',
  };
  const [otherL0, otherL1, otherL2, otherL3] = await Promise.all([
    api('conversation/query', { ...otherIds, limit: 10, offset: 0 }),
    api('atomic/query', { ...otherIds, limit: 10, offset: 0 }),
    api('scenario/ls', { ...otherIds }),
    api('core/read', { ...otherIds }),
  ]);
  const crossProjectEmpty = (otherL0.total ?? 0) === 0
    && (otherL1.total ?? 0) === 0
    && (otherL2.total ?? 0) === 0
    && otherL3.content === null;
  if (!crossProjectEmpty) throw new Error('Cross-project isolation query was not empty');

  console.log(JSON.stringify({
    status: 'passed',
    began_at: beganAt,
    finished_at: new Date().toISOString(),
    project_identity: ids,
    session_id: sessionId,
    bundle_sha256: digest(bundle),
    l0_message_count: messages.length,
    native_layers: {
      l0: layers.l0.total,
      l1: layers.l1.total,
      l2: layers.l2.total,
      l3: Boolean(layers.l3.content),
    },
    layer_hashes: {
      l0_sha256: digest(layers.l0),
      l1_sha256: digest(layers.l1),
      l2_sha256: digest(layers.l2),
      l3_sha256: digest(layers.l3.content),
    },
    semantic_checks: checks,
    cross_project_empty: true,
  }));
} catch (error) {
  failure = error;
  console.log(JSON.stringify({
    status: 'failed',
    began_at: beganAt,
    finished_at: new Date().toISOString(),
    error: error instanceof Error ? error.message : String(error),
    gateway_stderr_tail: stderr.slice(-3000),
  }));
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
if (failure) process.exitCode = 1;
