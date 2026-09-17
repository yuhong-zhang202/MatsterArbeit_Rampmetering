// 隔离验收：完整快照通过官方 core API 写入，再由另一个容器只读；不调用真实模型。
import http from 'node:http';
import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

const stage = process.env.PILOT_STAGE;
if (!['write', 'read'].includes(stage)) throw new Error('必须指定 write 或 read 阶段');
const raw = await readFile('/app/project-snapshot.txt', 'utf8');
// 官方 core/write 会 trim；唯一接受的正文正规化是首尾空白删除。
const expected = raw.trim();
if (!expected) throw new Error('拒绝空快照');
if (/scene\s+navigation/i.test(raw)) throw new Error('输入含 Scene Navigation，拒绝触发官方导航剥离');
const sha = text => createHash('sha256').update(text, 'utf8').digest('hex');
const expectedSha = sha(expected);
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const MAX_AI_CALLS = 0;
const startedAt = new Date().toISOString();
let modelCalls = 0;
let failure;
const fake = http.createServer((req, res) => {
  modelCalls++;
  failure = new Error('禁止模型调用：已超过 MAX_AI_CALLS=0');
  console.log(JSON.stringify({ kind: '禁止的本地假模型请求', modelCalls, url: req.url }));
  req.resume();
  res.writeHead(400, { 'content-type': 'application/json' });
  res.end(JSON.stringify({ error: { message: '快照验收禁止模型调用', type: 'invalid_request_error' } }));
  service.kill('SIGTERM');
});
await new Promise(resolve => fake.listen(18420, '127.0.0.1', resolve));
const service = spawn('node', ['--import', 'tsx', 'src/gateway/server.ts'], {
  cwd: '/app', env: process.env, stdio: ['ignore', 'ignore', 'pipe']
});
service.stderr.on('data', chunk => process.stderr.write(chunk));
service.on('error', error => { failure = error; });
const watchdog = setTimeout(() => {
  console.log(JSON.stringify({ kind: '验收失败', stage, message: '超过 45 秒总时限', modelCalls }));
  service.kill('SIGKILL');
  process.exit(1);
}, 45000);

async function api(route, body) {
  if (failure) throw failure;
  const began = performance.now();
  const response = await fetch('http://127.0.0.1:8420/v3/' + route, {
    method: 'POST', headers: { 'content-type': 'application/json',
      'x-tdai-service-id': 'default', authorization: 'Bearer fake-gateway-local-only' },
    body: JSON.stringify(body), signal: AbortSignal.timeout(4000)
  });
  const result = await response.json();
  console.log(JSON.stringify({ kind: '快照 API 原始结果', stage, route,
    latency_ms: Math.round(performance.now() - began), http_status: response.status, result }));
  if (!response.ok || result.code !== 0) throw new Error(route + ' 返回失败');
  if (failure) throw failure;
  return result.data;
}

try {
  let ready = false;
  for (let i = 0; i < 40; i++) {
    if (failure) throw failure;
    if (service.exitCode !== null || service.signalCode !== null) throw new Error('服务提前退出');
    try {
      if ((await fetch('http://127.0.0.1:8420/health', { signal: AbortSignal.timeout(500) })).ok) {
        ready = true; break;
      }
    } catch {}
    await delay(500);
  }
  if (!ready) throw new Error('启动超时');
  let written;
  if (stage === 'write') {
    const before = await api('core/read', {});
    if (before?.content !== null) throw new Error('目标已存在或状态不明，拒绝覆盖');
    console.log(JSON.stringify({ kind: '空存储负对照通过', content: before.content }));
    written = await api('core/write', { content: raw });
    if (!Number.isInteger(written?.version)) throw new Error('写入回执缺少整数版本');
  }
  const actual = await api('core/read', {});
  if (actual?.content !== expected) throw new Error('读回正文不逐字相同');
  const actualSha = sha(actual.content);
  if (actualSha !== expectedSha) throw new Error('读回 SHA 不符');
  if (written && actual.version !== written.version) throw new Error('读回版本与写入回执不符');
  if (!Number.isInteger(actual.version)) throw new Error('读回缺少整数版本');
  console.log(JSON.stringify({ kind: '完整快照对照', stage, raw_sha256: sha(raw),
    normalization: '仅删除首尾空白（trim），对应官方 core/write 行为', expected_sha256: expectedSha,
    actual_sha256: actualSha, utf8_bytes: Buffer.byteLength(expected), content: actual.content,
    version: actual.version, write_version: written?.version ?? null }));
  // 给后台任务一个有界观察窗口；这不是耐久测试。
  await delay(2000);
  if (failure) throw failure;
  if (service.exitCode !== null || service.signalCode !== null) throw new Error('验收期间服务退出');
} catch (error) {
  failure = error;
} finally {
  service.kill('SIGTERM');
  if (service.exitCode === null && service.signalCode === null) {
    await Promise.race([new Promise(resolve => service.once('exit', resolve)), delay(2500)]);
  }
  if (service.exitCode === null && service.signalCode === null) service.kill('SIGKILL');
  fake.closeAllConnections();
  await new Promise(resolve => fake.close(resolve));
  clearTimeout(watchdog);
  if (modelCalls > MAX_AI_CALLS) failure = new Error('禁止模型调用次数超限');
  console.log(JSON.stringify({ kind: failure ? '验收失败' : '验收通过', stage, started_at: startedAt,
    finished_at: new Date().toISOString(), modelCalls, MAX_AI_CALLS,
    message: failure ? String(failure) : '完整快照正规化正文及 SHA 通过；写阶段额外验证空存储；当前阶段未触发模型' }));
  if (failure) process.exitCode = 1;
}
