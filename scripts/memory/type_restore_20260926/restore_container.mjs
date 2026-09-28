import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';

const sha = value => createHash('sha256').update(value).digest('hex');
const jsonSha = value => sha(JSON.stringify(value));
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const spec = JSON.parse(await readFile('/correction_spec.json', 'utf8'));
const baseline = JSON.parse(await readFile('/baseline_receipt.json', 'utf8'));
const ids = { team_id: spec.team_id, agent_id: spec.agent_id, user_id: spec.user_id };
const key = 'type-restore-local-network-disabled';
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

function assert(condition, message) {
  if (!condition) throw new Error(message);
}
async function call(route, body) {
  const response = await fetch(`http://127.0.0.1:8420/v3/${route}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization: `Bearer ${key}`, 'x-tdai-service-id': spec.service_id },
    body: JSON.stringify(body), signal: AbortSignal.timeout(10000),
  });
  const envelope = await response.json();
  return { http_status: response.status, ...envelope };
}
async function api(route, body) {
  const result = await call(route, body);
  assert(result.http_status === 200 && result.code === 0, `${route} failed: ${result.http_status} ${result.code} ${result.message}`);
  return result.data;
}
async function readLayers() {
  const [l0, l1, l2, l3] = await Promise.all([
    api('conversation/query', { ...ids, limit: 100, offset: 0 }),
    api('atomic/query', { ...ids, limit: 100, offset: 0 }),
    api('scenario/ls', ids),
    api('core/read', ids),
  ]);
  const entries = l2.entries.filter(item => typeof item.path === 'string' && !item.path.endsWith('/'));
  const l2Docs = await Promise.all(entries.map(item => api('scenario/read', { ...ids, path: item.path })));
  return { l0, l1, l2, l2Docs, l3 };
}
function hashes(layers) {
  return { l0: jsonSha(layers.l0), l1: jsonSha(layers.l1), l2: jsonSha(layers.l2),
    l2_documents: jsonSha(layers.l2Docs), l3: jsonSha(layers.l3.content) };
}
function target(layers) {
  const matches = layers.l1.items.filter(item => item.id === spec.atomic.id);
  assert(matches.length === 1, `Expected one target L1 record, found ${matches.length}`);
  return matches[0];
}
function snapshot(item) {
  return { id: item.id, type: item.type, version: item.version, content_sha256: sha(item.content),
    background_sha256: sha(item.background ?? ''), item_sha256: jsonSha(item) };
}
function assertOriginalState(layers) {
  const actualHashes = hashes(layers);
  for (const [name, value] of Object.entries(baseline.layer_hashes)) {
    assert(actualHashes[name] === value, `Current ${name} hash differs from the reviewed baseline`);
  }
  assert(layers.l0.total === 10 && layers.l1.total === 13 && layers.l2.total === 2, 'Layer counts changed');
  const item = target(layers);
  assert(item.type === 'persona' && item.version === 1, 'L1 target type/version changed');
  assert(sha(item.content) === spec.atomic.new_content_sha256 && item.background === spec.atomic.background,
    'L1 target content/background changed');
  return item;
}

let gateway;
let writeAttempted = false;
let stderr = '';
const negative = [];
try {
  assert(process.env.TDAI_TYPE_RESTORE_MODE === 'stage6-l1-type-restore-20260926-v1', 'Repair mode missing');
  assert(spec.correction_id === 'stage6-content-correction-20260926-v1' && spec.no_model_calls,
    'Correction provenance/policy mismatch');
  await writeFile('/tmp/tdai-type-restore.yaml', config, { flag: 'wx', mode: 0o600 });
  gateway = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app', env: { ...process.env, TDAI_GATEWAY_CONFIG: '/tmp/tdai-type-restore.yaml',
      TDAI_GATEWAY_HOST: '127.0.0.1', TDAI_GATEWAY_API_KEY: key },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  gateway.stderr.on('data', chunk => { stderr += chunk; });
  for (let i = 0; i < 240; i++) {
    try { if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(300) })).ok) break; } catch {}
    if (i === 239) throw new Error(`Gateway startup timeout: ${stderr.slice(-1500)}`);
    await sleep(250);
  }

  const before = await readLayers();
  const oldTarget = assertOriginalState(before);
  const request = { ...ids, id: spec.atomic.id, content: spec.atomic.new_content,
    background: spec.atomic.background, restore_type: 'episodic', expected_type: 'persona', expected_version: 1 };
  const cases = [
    ['missing_expected_type', { ...request, expected_type: undefined }],
    ['extra_field', { ...request, unexpected: true }],
    ['wrong_id', { ...request, id: 'm_wrong' }],
    ['wrong_content', { ...request, content: `${request.content} wrong` }],
    ['wrong_background', { ...request, background: 'wrong' }],
    ['wrong_expected_type', { ...request, expected_type: 'episodic' }],
    ['wrong_expected_version', { ...request, expected_version: 0 }],
  ];
  for (const [name, badRequest] of cases) {
    const result = await call('atomic/update', badRequest);
    assert(result.http_status >= 400 && result.code !== 0, `Negative fixture ${name} unexpectedly accepted`);
    negative.push({ name, http_status: result.http_status, code: result.code });
  }
  const afterNegative = await readLayers();
  assert(JSON.stringify(afterNegative) === JSON.stringify(before), 'Negative requests changed stored layers');

  writeAttempted = true;
  const write = await api('atomic/update', request);
  assert(write.id === spec.atomic.id && write.version === 'v2', 'Unexpected repair response');
  const after = await readLayers();
  const newTarget = target(after);
  assert(newTarget.type === 'episodic' && newTarget.version === 2, 'Target type/version not restored');
  assert(newTarget.id === oldTarget.id && newTarget.content === oldTarget.content &&
    newTarget.background === oldTarget.background && newTarget.created_at === oldTarget.created_at &&
    newTarget.team_id === oldTarget.team_id && newTarget.agent_id === oldTarget.agent_id &&
    newTarget.user_id === oldTarget.user_id, 'Target non-repair fields changed');
  const allowedChanged = new Set(['type', 'version', 'updated_at']);
  for (const key of new Set([...Object.keys(oldTarget), ...Object.keys(newTarget)])) {
    if (!allowedChanged.has(key)) assert(JSON.stringify(newTarget[key]) === JSON.stringify(oldTarget[key]),
      `Target field ${key} changed unexpectedly`);
  }
  const oldOthers = before.l1.items.filter(item => item.id !== spec.atomic.id);
  const newOthers = after.l1.items.filter(item => item.id !== spec.atomic.id);
  assert(JSON.stringify(oldOthers) === JSON.stringify(newOthers), 'Unrelated L1 records changed');
  const beforeHash = hashes(before);
  const afterHash = hashes(after);
  for (const key of ['l0', 'l2', 'l2_documents', 'l3']) {
    assert(beforeHash[key] === afterHash[key], `Unrelated ${key} layer changed`);
  }
  const repeated = await call('atomic/update', request);
  assert(repeated.http_status === 409 && repeated.code === 409, 'Replay was not rejected');
  const afterReplay = await readLayers();
  assert(JSON.stringify(afterReplay) === JSON.stringify(after), 'Rejected replay changed stored layers');

  console.log(JSON.stringify({ status: 'passed', network: 'none', model_calls: 0,
    before: { layer_hashes: beforeHash, target: snapshot(oldTarget) }, negative,
    write_response: write, after: { layer_hashes: afterHash, target: snapshot(newTarget) },
    replay_rejected: { http_status: repeated.http_status, code: repeated.code },
    unrelated_l1_unchanged: true, l0_l2_l3_unchanged: true }));
} catch (error) {
  console.log(JSON.stringify({ status: 'failed', network: 'none', model_calls: 0, write_attempted: writeAttempted,
    negative, error: error instanceof Error ? error.message : String(error), gateway_stderr_tail: stderr.slice(-1500) }));
  process.exitCode = 1;
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
