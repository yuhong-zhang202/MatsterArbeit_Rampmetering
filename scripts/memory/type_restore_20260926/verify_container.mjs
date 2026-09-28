import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';

const sha = value => createHash('sha256').update(value).digest('hex');
const jsonSha = value => sha(JSON.stringify(value));
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const spec = JSON.parse(await readFile('/correction_spec.json', 'utf8'));
const restore = JSON.parse(await readFile('/restore_receipt.json', 'utf8'));
const ids = { team_id: spec.team_id, agent_id: spec.agent_id, user_id: spec.user_id };
const key = 'type-restore-fresh-verification-local-only';
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
`;
function assert(condition, message) { if (!condition) throw new Error(message); }
async function api(route, body) {
  const response = await fetch(`http://127.0.0.1:8420/v3/${route}`, {
    method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${key}`,
      'x-tdai-service-id': spec.service_id }, body: JSON.stringify(body), signal: AbortSignal.timeout(10000),
  });
  const result = await response.json();
  assert(response.ok && result.code === 0, `${route}: ${response.status} ${result.code}`);
  return result.data;
}
let gateway;
let stderr = '';
try {
  assert(restore.status === 'passed' && restore.result?.status === 'passed', 'Production receipt not passed');
  await writeFile('/tmp/tdai-type-verify.yaml', config, { flag: 'wx', mode: 0o600 });
  gateway = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app', env: { ...process.env, TDAI_GATEWAY_CONFIG: '/tmp/tdai-type-verify.yaml',
      TDAI_GATEWAY_HOST: '127.0.0.1', TDAI_GATEWAY_API_KEY: key },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  gateway.stderr.on('data', chunk => { stderr += chunk; });
  for (let i = 0; i < 240; i++) {
    try { if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(300) })).ok) break; } catch {}
    if (i === 239) throw new Error(`Gateway startup timeout: ${stderr.slice(-1500)}`);
    await sleep(250);
  }
  const [l0, l1, l2, l3, episodic, persona] = await Promise.all([
    api('conversation/query', { ...ids, limit: 100, offset: 0 }),
    api('atomic/query', { ...ids, limit: 100, offset: 0 }),
    api('scenario/ls', ids), api('core/read', ids),
    api('atomic/query', { ...ids, type: 'episodic', limit: 100, offset: 0 }),
    api('atomic/query', { ...ids, type: 'persona', limit: 100, offset: 0 }),
  ]);
  const paths = l2.entries.filter(item => typeof item.path === 'string' && !item.path.endsWith('/'));
  const l2Docs = await Promise.all(paths.map(item => api('scenario/read', { ...ids, path: item.path })));
  const hashes = { l0: jsonSha(l0), l1: jsonSha(l1), l2: jsonSha(l2),
    l2_documents: jsonSha(l2Docs), l3: jsonSha(l3.content) };
  for (const [name, expected] of Object.entries(restore.result.after.layer_hashes)) {
    assert(hashes[name] === expected, `Independent ${name} readback mismatch`);
  }
  assert(l0.total === 10 && l1.total === 13 && l2.total === 2, 'Layer count mismatch');
  const item = l1.items.find(x => x.id === spec.atomic.id);
  assert(item?.type === 'episodic' && item.version === 2 &&
    sha(item.content) === spec.atomic.new_content_sha256 && item.background === spec.atomic.background,
    'Target item type/version/content/background mismatch');
  assert(episodic.items.some(x => x.id === spec.atomic.id) && !persona.items.some(x => x.id === spec.atomic.id),
    'Type-filtered retrieval mismatch');
  const forbidden = {};
  const texts = { l1: l1.items.map(x => x.content).join('\n'),
    l2: l2Docs.map(x => x.content).join('\n'), l3: l3.content };
  for (const [layer, content] of Object.entries(texts)) {
    forbidden[layer] = Object.fromEntries(spec.forbidden_error_phrases.map(phrase => [phrase, content.includes(phrase)]));
    assert(Object.values(forbidden[layer]).every(present => !present), `False statement remains in ${layer}`);
  }
  console.log(JSON.stringify({ status: 'passed', network: 'none', model_calls: 0,
    unpatched_gateway: true, layer_counts: { l0: l0.total, l1: l1.total, l2: l2.total, l3: Boolean(l3.content) },
    layer_hashes: hashes,
    target: { id: item.id, type: item.type, version: item.version,
      content_sha256: sha(item.content), background_sha256: sha(item.background), item_sha256: jsonSha(item) },
    type_filter: { episodic_contains_target: true, persona_contains_target: false },
    forbidden_error_phrases_present: forbidden }));
} catch (error) {
  console.log(JSON.stringify({ status: 'failed', network: 'none', model_calls: 0,
    error: error instanceof Error ? error.message : String(error), gateway_stderr_tail: stderr.slice(-1500) }));
  process.exitCode = 1;
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
