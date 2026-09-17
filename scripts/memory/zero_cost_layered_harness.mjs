import http from 'node:http';
import { spawn } from 'node:child_process';
import { writeFile } from 'node:fs/promises';

const MAX_ATTEMPTS = 41;
let acceptedAttempts = 0;
let blockedAttempts = 0;
let service;
const requests = [];

function stageOf(body) {
  const text = JSON.stringify(body);
  if (text.includes('persona.md') || text.includes('persona-generation')) return 'l3';
  if (text.includes('Memory Consolidation Architect')) return 'l2';
  if (text.includes('l1-extraction') || text.includes('scene_name') || !body.tools) return 'l1';
  return 'unknown';
}

function completion(message, finishReason = 'stop') {
  return {
    id: `chatcmpl-fake-${acceptedAttempts}`,
    object: 'chat.completion',
    created: 0,
    model: 'fake-local-layered-memory',
    choices: [{ index: 0, message, finish_reason: finishReason }],
    usage: { prompt_tokens: 100, completion_tokens: 50, total_tokens: 150 },
  };
}

function toolCompletion(path, content) {
  return completion({
    role: 'assistant', content: null,
    tool_calls: [{
      id: `call_fake_${acceptedAttempts}`,
      type: 'function',
      function: { name: 'write', arguments: JSON.stringify({ path, content }) },
    }],
  }, 'tool_calls');
}

const fake = http.createServer((req, res) => {
  if (req.method !== 'POST' || req.url !== '/v1/chat/completions') {
    res.writeHead(404).end(); return;
  }
  let raw = '';
  req.setEncoding('utf8');
  req.on('data', chunk => { raw += chunk; });
  req.on('end', () => {
    if (acceptedAttempts >= MAX_ATTEMPTS) {
      blockedAttempts++;
      res.writeHead(429, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ error: { message: 'zero-cost hard gate exhausted', type: 'budget_gate' } }));
      return;
    }
    acceptedAttempts++;
    const body = JSON.parse(raw);
    const stage = stageOf(body);
    const hasToolResult = Array.isArray(body.messages) && body.messages.some(m => m.role === 'tool');
    requests.push({
      attempt: acceptedAttempts,
      stage,
      request_bytes: Buffer.byteLength(raw),
      model: body.model ?? null,
      max_tokens: body.max_tokens ?? body.max_completion_tokens ?? null,
      has_tools: Boolean(body.tools),
      has_tool_result: hasToolResult,
    });

    let result;
    if (stage === 'l1') {
      const allText = JSON.stringify(body.messages ?? []);
      const sourceId = allText.match(/msg-[A-Za-z0-9_-]+/)?.[0] ?? 'synthetic-source';
      result = completion({ role: 'assistant', content: JSON.stringify([{
        scene_name: '零费用分层记忆测试',
        message_ids: [sourceId],
        memories: [{
          content: '这是隔离的虚构记忆：蓝色方案已批准，红色方案仍待确认。',
          type: 'episodic', priority: 50, source_message_ids: [sourceId], metadata: { synthetic: true },
        }],
      }]) });
    } else if (stage === 'l2' && !hasToolResult) {
      result = toolCompletion('零费用-分层记忆测试.md', `-----META-START-----\ncreated: 2026-09-09T00:00:00.000Z\nupdated: 2026-09-09T00:00:00.000Z\nsummary: 隔离的零费用分层记忆测试，区分已批准蓝色方案与待确认红色方案。\nheat: 1\n-----META-END-----\n\n## 核心叙事\n虚构测试明确蓝色方案已批准，而红色方案仍待确认，用于检查状态边界能否进入场景记忆。\n\n## 待确认/矛盾点\n- 红色方案仍待确认。`);
    } else if (stage === 'l2') {
      result = completion({ role: 'assistant', content: '[PERSONA_UPDATE_REQUEST]\nreason: 首个隔离测试场景已建立\n[/PERSONA_UPDATE_REQUEST]' });
    } else if (stage === 'l3' && !hasToolResult) {
      result = toolCompletion('persona.md', '# 隔离测试长期记忆\n\n蓝色方案已批准；红色方案仍待确认。该内容完全虚构，仅用于验证分层链路。');
    } else if (stage === 'l3') {
      result = completion({ role: 'assistant', content: 'persona.md 已写入。' });
    } else {
      result = completion({ role: 'assistant', content: '[]' });
    }
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify(result));
  });
});

const config = `deployMode: standalone
stateBackend: local
server:
  port: 8420
  host: 127.0.0.1
  apiKey: fake-gateway-local-only
data:
  baseDir: /data/tdai-memory
llm:
  baseUrl: http://127.0.0.1:18420/v1
  apiKey: fake-local-only
  model: fake-local-layered-memory
  maxTokens: 4096
  timeoutMs: 10000
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
    headers: { 'content-type': 'application/json', authorization: 'Bearer fake-gateway-local-only', 'x-tdai-service-id': 'ramp-memory-zero-cost' },
    body: JSON.stringify(body), signal: AbortSignal.timeout(3000),
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0) throw new Error(`${route} failed: ${response.status} ${JSON.stringify(result)}`);
  return result.data;
}

let failure;
const beganAt = new Date().toISOString();
try {
  await writeFile('/tmp/tdai-zero-cost.yaml', config, { flag: 'w', mode: 0o600 });
  await new Promise(resolve => fake.listen(18420, '127.0.0.1', resolve));
  service = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
    cwd: '/app',
    env: { ...process.env, TDAI_GATEWAY_CONFIG: '/tmp/tdai-zero-cost.yaml', TDAI_GATEWAY_HOST: '127.0.0.1', TDAI_GATEWAY_API_KEY: 'fake-gateway-local-only' },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  let stderr = '';
  service.stderr.on('data', chunk => { stderr += chunk; });
  // The pinned amd64 image can need tens of seconds to initialize under
  // Apple-Silicon emulation before the HTTP listener is ready.
  for (let i = 0; i < 240; i++) {
    try { if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(300) })).ok) break; } catch {}
    if (i === 239) throw new Error(`gateway startup timeout: ${stderr.slice(-2000)}`);
    await sleep(250);
  }

  const ids = { team_id: 'team-ramp-pilot', agent_id: 'agent-ramp-pilot', user_id: 'user-ramp-pilot' };
  await api('conversation/add', { ...ids, session_id: 'synthetic-layered-session', messages: [
    { role: 'user', content: '完全虚构的隔离测试：蓝色方案已批准，红色方案仍待确认。' },
    { role: 'assistant', content: '已记录虚构测试状态，不作真实项目结论。' },
  ] });

  let same;
  for (let i = 0; i < 80; i++) {
    const [atomic, scenes, core] = await Promise.all([
      api('atomic/query', { ...ids, limit: 20, offset: 0 }),
      api('scenario/ls', { ...ids }),
      api('core/read', { ...ids }),
    ]);
    same = { atomic, scenes, core };
    if ((atomic.total ?? 0) > 0 && (scenes.total ?? 0) > 0 && core.content) break;
    await sleep(500);
  }
  if (!(same?.atomic?.total > 0)) throw new Error('L1 did not materialize');
  if (!(same?.scenes?.total > 0)) throw new Error('L2 did not materialize');
  if (!same?.core?.content) throw new Error('L3 did not materialize');

  const otherIds = { team_id: 'team-other-pilot', agent_id: 'agent-other-pilot', user_id: 'user-other-pilot' };
  const [otherL0, otherL1, otherL2, otherL3] = await Promise.all([
    api('conversation/query', { ...otherIds, limit: 20, offset: 0 }),
    api('atomic/query', { ...otherIds, limit: 20, offset: 0 }),
    api('scenario/ls', { ...otherIds }),
    api('core/read', { ...otherIds }),
  ]);
  if ((otherL0.total ?? 0) !== 0 || (otherL1.total ?? 0) !== 0 || (otherL2.total ?? 0) !== 0 || otherL3.content !== null) {
    throw new Error('cross-project isolation failed');
  }

  while (acceptedAttempts < MAX_ATTEMPTS) {
    const response = await fetch('http://127.0.0.1:18420/v1/chat/completions', {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ messages: [] }),
    });
    if (!response.ok) throw new Error('gate blocked before configured limit');
  }
  const blocked = await fetch('http://127.0.0.1:18420/v1/chat/completions', {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ messages: [] }),
  });
  if (blocked.status !== 429 || acceptedAttempts !== MAX_ATTEMPTS || blockedAttempts !== 1) throw new Error('hard gate enforcement failed');

  console.log(JSON.stringify({
    status: 'passed', began_at: beganAt, finished_at: new Date().toISOString(), external_model_calls: 0,
    native_layers: { l0: 2, l1: same.atomic.total, l2: same.scenes.total, l3: Boolean(same.core.content) },
    native_request_trace: requests.filter(r => r.stage !== 'unknown'),
    cross_project_empty: true,
    ephemeral_gate: { limit: MAX_ATTEMPTS, accepted: acceptedAttempts, blocked: blockedAttempts, status: 'passed' },
    limitations: ['fake semantic content only', 'gate counter is process-local and not suitable for paid use', 'installed image was tested; equivalence to audited source commit remains unverified'],
  }));
} catch (error) {
  failure = error;
  console.log(JSON.stringify({ status: 'failed', began_at: beganAt, finished_at: new Date().toISOString(), external_model_calls: 0, accepted_attempts: acceptedAttempts, blocked_attempts: blockedAttempts, requests, error: error instanceof Error ? error.message : String(error) }));
} finally {
  if (service && service.exitCode === null) service.kill('SIGTERM');
  await new Promise(resolve => fake.close(resolve));
}
if (failure) process.exitCode = 1;
