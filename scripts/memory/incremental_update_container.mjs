import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';

const proxyBaseUrl = process.env.MEMORY_PROXY_BASE_URL?.trim();
const proxyClientKey = process.env.MEMORY_PROXY_CLIENT_KEY?.trim();
const sessionId = process.env.MEMORY_UPDATE_SESSION_ID?.trim();
if (!proxyBaseUrl || !proxyClientKey) throw new Error('Memory proxy configuration is missing');
if (!/^[a-z0-9][a-z0-9-]{5,79}$/.test(sessionId ?? '')) throw new Error('Invalid MEMORY_UPDATE_SESSION_ID');

const ids = {
  team_id: 'team-masterarbeit-ramp-metering',
  agent_id: 'agent-project-memory',
  user_id: 'user-yuhong-zhang',
};
const gatewayKey = 'formal-memory-incremental-local-only';
const serviceId = 'ramp-metering-formal-memory-v1';
const digest = value => createHash('sha256').update(typeof value === 'string' ? value : JSON.stringify(value)).digest('hex');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

const config = `deployMode: standalone
stateBackend: local
server: { port: 8420, host: 127.0.0.1, apiKey: ${gatewayKey} }
data: { baseDir: /data/tdai-memory }
llm:
  provider: openai
  baseUrl: ${proxyBaseUrl}
  apiKey: ${proxyClientKey}
  model: gpt-4.1-mini
  maxTokens: 4096
  timeoutMs: 120000
memory:
  capture: { enabled: true }
  extraction: { enabled: true, enableDedup: false, maxMemoriesPerSession: 12 }
  persona: { triggerEveryN: 1000000, maxScenes: 8 }
  pipeline: { everyNConversations: 1, enableWarmup: true, l1IdleTimeoutSeconds: 1, l2DelayAfterL1Seconds: 1, l2MinIntervalSeconds: 1, l2MaxIntervalSeconds: 2 }
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

function splitByParagraph(text, maxChars = 7200) {
  const chunks = [];
  let current = '';
  for (const paragraph of text.split('\n\n')) {
    const candidate = current ? `${current}\n\n${paragraph}` : paragraph;
    if (candidate.length <= maxChars) current = candidate;
    else {
      if (current) chunks.push(current);
      if (paragraph.length > maxChars) throw new Error('One delta-bundle paragraph exceeds 7,200 characters');
      current = paragraph;
    }
  }
  if (current) chunks.push(current);
  return chunks;
}

async function api(route, body) {
  const response = await fetch(`http://127.0.0.1:8420/v3/${route}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization: `Bearer ${gatewayKey}`, 'x-tdai-service-id': serviceId },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(10000),
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0) throw new Error(`${route} failed: ${response.status} ${JSON.stringify(result)}`);
  return result.data;
}

async function readLayers() {
  const [l0, l1, l2Index, l3] = await Promise.all([
    api('conversation/query', { ...ids, limit: 100, offset: 0 }),
    api('atomic/query', { ...ids, limit: 100, offset: 0 }),
    api('scenario/ls', { ...ids }),
    api('core/read', { ...ids }),
  ]);
  const entries = Array.isArray(l2Index.entries)
    ? l2Index.entries.filter(entry => typeof entry?.path === 'string' && !entry.path.endsWith('/'))
    : [];
  if (entries.length > 50) throw new Error('Refusing to read more than 50 L2 documents');
  const l2Documents = await Promise.all(entries.map(entry => api('scenario/read', { ...ids, path: entry.path })));
  return { l0, l1, l2Index, l2Documents, l3 };
}

let gateway;
let stderr = '';
let failure;
const beganAt = new Date().toISOString();
try {
  const [bundle, coreCandidate] = await Promise.all([
    readFile('/incremental_bundle.md', 'utf8'),
    readFile('/core_candidate.md', 'utf8'),
  ]);
  if (!bundle.includes('Project identity: `Masterarbeit-Ramp-Metering`')) throw new Error('Delta bundle identity mismatch');
  if (!coreCandidate.includes('Masterarbeit-Ramp-Metering')) throw new Error('L3 candidate identity mismatch');
  await writeFile('/tmp/tdai-incremental-memory.yaml', config, { flag: 'w', mode: 0o600 });
  gateway = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app',
    env: { ...process.env, TDAI_GATEWAY_CONFIG: '/tmp/tdai-incremental-memory.yaml', TDAI_GATEWAY_HOST: '127.0.0.1', TDAI_GATEWAY_API_KEY: gatewayKey },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  gateway.stderr.on('data', chunk => { stderr += chunk; });
  for (let i = 0; i < 240; i++) {
    try { if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(300) })).ok) break; } catch {}
    if (i === 239) throw new Error(`gateway startup timeout: ${stderr.slice(-2000)}`);
    await sleep(250);
  }

  const sessionBefore = await api('conversation/query', { ...ids, session_id: sessionId, limit: 10, offset: 0 });
  if ((sessionBefore.total ?? 0) !== 0) throw new Error(`Session ${sessionId} already exists; refusing duplicate update`);
  const before = await readLayers();
  if (!(before.l0.total > 0 && before.l1.total > 0 && before.l2Index.total > 0 && before.l3.content)) {
    throw new Error('Existing formal L0-L3 prerequisites are incomplete');
  }
  if (digest(before.l3.content.trim()) === digest(coreCandidate.trim())) throw new Error('L3 candidate is unchanged');

  const chunks = splitByParagraph(bundle);
  const messages = chunks.flatMap((chunk, index) => [{
    role: 'user',
    content: `Reviewed incremental project-memory update ${sessionId}, part ${index + 1}/${chunks.length}. Preserve approval levels, evidence boundaries, superseded state and uncertainty exactly.\n\n${chunk}`,
  }, {
    role: 'assistant',
    content: index + 1 === chunks.length
      ? 'Recorded the complete reviewed delta. Repository documents remain authoritative and supersede stale memory.'
      : `Recorded reviewed delta part ${index + 1}/${chunks.length}; awaiting remaining parts.`,
  }]);
  await api('conversation/add', { ...ids, session_id: sessionId, messages });

  let generated;
  for (let i = 0; i < 480; i++) {
    generated = await readLayers();
    const l1Changed = generated.l1.total > before.l1.total || digest(generated.l1) !== digest(before.l1);
    const l2Changed = digest({ index: generated.l2Index, documents: generated.l2Documents })
      !== digest({ index: before.l2Index, documents: before.l2Documents });
    if (generated.l0.total > before.l0.total && l1Changed && l2Changed) break;
    await sleep(1000);
  }
  const l1Changed = generated && (generated.l1.total > before.l1.total || digest(generated.l1) !== digest(before.l1));
  const l2Changed = generated && digest({ index: generated.l2Index, documents: generated.l2Documents })
    !== digest({ index: before.l2Index, documents: before.l2Documents });
  if (!(generated?.l0?.total > before.l0.total)) throw new Error('L0 delta was not persisted');
  if (!l1Changed) throw new Error('L1 did not change within eight minutes');
  if (!l2Changed) throw new Error('L2 did not change within eight minutes');

  await api('core/write', { ...ids, content: coreCandidate });
  const after = await readLayers();
  if (after.l3.content?.trim() !== coreCandidate.trim()) throw new Error('Exact reviewed L3 candidate was not persisted');
  const sessionAfter = await api('conversation/query', { ...ids, session_id: sessionId, limit: 100, offset: 0 });
  if ((sessionAfter.total ?? 0) <= 0) throw new Error('Unique update session was not readable after write');

  console.log(JSON.stringify({
    status: 'passed', began_at: beganAt, finished_at: new Date().toISOString(), session_id: sessionId,
    bundle_sha256: digest(bundle), core_candidate_sha256: digest(coreCandidate), l0_message_count: messages.length,
    before: { l0: before.l0.total, l1: before.l1.total, l2: before.l2Index.total, l3_sha256: digest(before.l3.content.trim()), l2_sha256: digest({ index: before.l2Index, documents: before.l2Documents }) },
    after: { l0: after.l0.total, l1: after.l1.total, l2: after.l2Index.total, l3_sha256: digest(after.l3.content.trim()), l2_sha256: digest({ index: after.l2Index, documents: after.l2Documents }) },
  }));
} catch (error) {
  failure = error;
  console.log(JSON.stringify({ status: 'failed', began_at: beganAt, finished_at: new Date().toISOString(), error: error instanceof Error ? error.message : String(error), gateway_stderr_tail: stderr.slice(-3000) }));
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
if (failure) process.exitCode = 1;
