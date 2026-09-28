import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';

// One-use, offline correction of three already identified factual errors.
const ids = {
  team_id: 'team-masterarbeit-ramp-metering',
  agent_id: 'agent-project-memory',
  user_id: 'user-yuhong-zhang',
};
const serviceId = 'ramp-metering-formal-memory-v1';
const gatewayKey = 'formal-memory-content-correction-local-only';
const sha = value => createHash('sha256').update(value).digest('hex');
const jsonSha = value => sha(JSON.stringify(value));
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
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
`;

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

async function readLayers() {
  const [l0, l1, l2Index, l3] = await Promise.all([
    api('conversation/query', { ...ids, limit: 100, offset: 0 }),
    api('atomic/query', { ...ids, limit: 100, offset: 0 }),
    api('scenario/ls', { ...ids }),
    api('core/read', { ...ids }),
  ]);
  const entries = l2Index.entries.filter(item => typeof item.path === 'string' && !item.path.endsWith('/'));
  if (entries.length > 50) throw new Error('Too many L2 documents');
  const l2Docs = await Promise.all(entries.map(item => api('scenario/read', { ...ids, path: item.path })));
  return { l0, l1, l2Index, l2Docs, l3 };
}

function fullHashes(layers) {
  return {
    l0: jsonSha(layers.l0),
    l1: jsonSha(layers.l1),
    l2: jsonSha(layers.l2Index),
    l2_documents: jsonSha(layers.l2Docs),
    l3: jsonSha(layers.l3.content),
  };
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function scenarioBody(content) {
  const match = content.match(/^-----META-START-----\n[\s\S]*?\n-----META-END-----\n\n/);
  assert(Boolean(match), 'L2 META header is missing or unexpected');
  return content.slice(match[0].length);
}

function metaFields(content) {
  const match = content.match(/^-----META-START-----\n([\s\S]*?)\n-----META-END-----\n\n/);
  assert(Boolean(match), 'L2 META header is missing or unexpected');
  return Object.fromEntries(match[1].split('\n').map(line => {
    const i = line.indexOf(': ');
    assert(i > 0, `Invalid L2 META line: ${line}`);
    return [line.slice(0, i), line.slice(i + 2)];
  }));
}

let gateway;
let stderr = '';
let applied = [];
try {
  const [specRaw, l2Body, l3Text] = await Promise.all([
    readFile('/correction_spec.json', 'utf8'),
    readFile('/scenario_body_corrected.md', 'utf8'),
    readFile('/core_corrected.md', 'utf8'),
  ]);
  const spec = JSON.parse(specRaw);
  assert(spec.schema_version === 1 && spec.correction_id === 'stage6-content-correction-20260926-v1', 'Correction identity mismatch');
  assert(spec.project === 'Masterarbeit-Ramp-Metering' && spec.service_id === serviceId, 'Project/service mismatch');
  assert(spec.team_id === ids.team_id && spec.agent_id === ids.agent_id && spec.user_id === ids.user_id, 'Isolation identity mismatch');
  assert(spec.no_model_calls === true, 'Model-free policy missing');
  assert(sha(spec.atomic.new_content) === spec.atomic.new_content_sha256, 'L1 candidate hash mismatch');
  assert(sha(l2Body) === spec.scenario.new_body_sha256, 'L2 candidate hash mismatch');
  assert(sha(l3Text) === spec.core.new_content_sha256, 'L3 candidate hash mismatch');
  assert(!l3Text.includes('Scene Navigation'), 'L3 candidate contains derived Scene Navigation');

  await writeFile('/tmp/tdai-stage6-content-correction.yaml', config, { flag: 'wx', mode: 0o600 });
  gateway = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app',
    env: { ...process.env, TDAI_GATEWAY_CONFIG: '/tmp/tdai-stage6-content-correction.yaml', TDAI_GATEWAY_HOST: '127.0.0.1', TDAI_GATEWAY_API_KEY: gatewayKey },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  gateway.stderr.on('data', chunk => { stderr += chunk; });
  for (let i = 0; i < 240; i++) {
    try { if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(300) })).ok) break; } catch {}
    if (i === 239) throw new Error(`Gateway startup timeout: ${stderr.slice(-2000)}`);
    await sleep(250);
  }

  const before = await readLayers();
  const hashesBefore = fullHashes(before);
  for (const [layer, expected] of Object.entries(spec.expected_before_layer_hashes)) {
    assert(hashesBefore[layer] === expected, `Pre-write ${layer} hash mismatch: ${hashesBefore[layer]}`);
  }
  assert(before.l0.total === 10 && before.l1.total === 13 && before.l2Index.total === 2, 'Pre-write layer counts mismatch');
  const atomic = before.l1.items.find(item => item.id === spec.atomic.id);
  const scenario = before.l2Docs.find(item => item.path === spec.scenario.path);
  assert(atomic && scenario && before.l3.content, 'Target L1/L2/L3 not found');
  assert(atomic.version === spec.atomic.expected_version && sha(atomic.content) === spec.atomic.old_content_sha256, 'Target L1 version/content mismatch');
  assert(scenario.version === spec.scenario.expected_version && sha(scenario.content) === spec.scenario.old_content_sha256, 'Target L2 version/content mismatch');
  assert(before.l3.version === spec.core.expected_version && sha(before.l3.content) === spec.core.old_content_sha256, 'Target L3 version/content mismatch');
  assert(atomic.background === spec.atomic.background, 'Target L1 background mismatch');
  assert(!scenarioBody(scenario.content).includes('Scene Navigation'), 'Unexpected L2 body');

  const l1Write = await api('atomic/update', { ...ids, id: spec.atomic.id, content: spec.atomic.new_content });
  applied.push({ layer: 'L1', route: 'atomic/update', result: l1Write });
  const l2Write = await api('scenario/write', { ...ids, path: spec.scenario.path, content: l2Body });
  applied.push({ layer: 'L2', route: 'scenario/write', result: l2Write });
  const l3Write = await api('core/write', { ...ids, content: l3Text });
  applied.push({ layer: 'L3', route: 'core/write', result: l3Write });

  const after = await readLayers();
  const newAtomic = after.l1.items.find(item => item.id === spec.atomic.id);
  const newScenario = after.l2Docs.find(item => item.path === spec.scenario.path);
  assert(after.l0.total === before.l0.total && fullHashes(after).l0 === hashesBefore.l0, 'L0 changed unexpectedly');
  assert(after.l1.total === before.l1.total && after.l2Index.total === before.l2Index.total, 'L1/L2 count changed unexpectedly');
  assert(newAtomic && sha(newAtomic.content) === spec.atomic.new_content_sha256, 'Corrected L1 does not match');
  assert(newAtomic.version > atomic.version && newAtomic.background === atomic.background, 'Corrected L1 version/background mismatch');
  assert(newScenario && scenarioBody(newScenario.content) === l2Body, 'Corrected L2 body does not match');
  assert(l2Write.version !== undefined && newScenario.version !== undefined, 'Corrected L2 version missing');
  const beforeMeta = metaFields(scenario.content);
  const afterMeta = metaFields(newScenario.content);
  for (const [key, value] of Object.entries(beforeMeta)) {
    if (key !== 'updated') assert(afterMeta[key] === value, `L2 META ${key} changed unexpectedly`);
  }
  assert(after.l3.content?.trim() === l3Text.trim() && l3Write.version !== undefined && after.l3.version !== undefined,
    'Corrected L3 content/version missing');
  const oldL1 = new Map(before.l1.items.map(item => [item.id, item]));
  for (const item of after.l1.items) {
    if (item.id !== spec.atomic.id) assert(JSON.stringify(item) === JSON.stringify(oldL1.get(item.id)), `Unrelated L1 changed: ${item.id}`);
  }
  const oldL2 = new Map(before.l2Docs.map(item => [item.path, item]));
  for (const item of after.l2Docs) {
    if (item.path !== spec.scenario.path) assert(JSON.stringify(item) === JSON.stringify(oldL2.get(item.path)), `Unrelated L2 changed: ${item.path}`);
  }
  for (const phrase of spec.forbidden_error_phrases) {
    assert(!newAtomic.content.includes(phrase), `L1 error phrase remains: ${phrase}`);
    assert(!newScenario.content.includes(phrase), `L2 error phrase remains: ${phrase}`);
    assert(!after.l3.content.includes(phrase), `L3 error phrase remains: ${phrase}`);
  }

  console.log(JSON.stringify({
    status: 'passed', correction_id: spec.correction_id,
    network: 'none', model_calls: 0,
    before: { counts: { l0: before.l0.total, l1: before.l1.total, l2: before.l2Index.total }, hashes: hashesBefore,
      target_versions: { l1: atomic.version, l2: scenario.version, l3: before.l3.version } },
    writes: applied,
    after: { counts: { l0: after.l0.total, l1: after.l1.total, l2: after.l2Index.total }, hashes: fullHashes(after),
      target_versions: { l1: newAtomic.version, l2: newScenario.version, l3: after.l3.version },
      target_sha256: { l1: sha(newAtomic.content), l2_body: sha(scenarioBody(newScenario.content)), l3: sha(after.l3.content) } },
  }));
} catch (error) {
  console.log(JSON.stringify({ status: 'failed', applied, error: error instanceof Error ? error.message : String(error), gateway_stderr_tail: stderr.slice(-2000) }));
  process.exitCode = 1;
} finally {
  if (gateway && gateway.exitCode === null) gateway.kill('SIGTERM');
}
