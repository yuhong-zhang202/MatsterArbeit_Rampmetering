import http from 'node:http';
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

const temp = await mkdtemp(path.join(os.tmpdir(), 'ramp-memory-budget-test-'));
const statePath = path.join(temp, 'ledger.json');
const proxyPath = new URL('./openai_budget_proxy.mjs', import.meta.url);
let upstreamCalls = 0;
let upstreamPort;
let proxyPort;

const upstream = http.createServer(async (req, res) => {
  let raw = '';
  for await (const chunk of req) raw += chunk;
  upstreamCalls += 1;
  const body = JSON.parse(raw);
  const payload = JSON.stringify({
    id: `fake-${upstreamCalls}`,
    object: 'chat.completion',
    model: body.model,
    choices: [{ index: 0, message: { role: 'assistant', content: 'synthetic' }, finish_reason: 'stop' }],
    usage: { prompt_tokens: 4, completion_tokens: 1, total_tokens: 5 },
  });
  res.writeHead(200, { 'content-type': 'application/json' });
  res.end(payload);
});

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function waitForHealth() {
  for (let i = 0; i < 100; i++) {
    try {
      const response = await fetch(`http://127.0.0.1:${proxyPort}/health`);
      if (response.ok) return response.json();
    } catch {}
    await sleep(50);
  }
  throw new Error('proxy startup timeout');
}

function startProxy(maxNewAttempts = '41') {
  return spawn(process.execPath, [proxyPath.pathname], {
    env: {
      ...process.env,
      BUDGET_PROXY_PORT: String(proxyPort),
      BUDGET_PROXY_UPSTREAM_BASE_URL: `http://127.0.0.1:${upstreamPort}/v1`,
      BUDGET_PROXY_ALLOW_INSECURE_UPSTREAM: 'true',
      BUDGET_PROXY_UPSTREAM_API_KEY: 'fake-upstream-key',
      BUDGET_PROXY_CLIENT_API_KEY: 'fake-client-key',
      BUDGET_PROXY_MODEL: 'fake-fixed-model',
      BUDGET_PROXY_MAX_ATTEMPTS: '41',
      BUDGET_PROXY_MAX_NEW_ATTEMPTS: maxNewAttempts,
      BUDGET_PROXY_MAX_REQUEST_BYTES: '512',
      BUDGET_PROXY_MAX_OUTPUT_TOKENS: '8',
      BUDGET_PROXY_STATE_PATH: statePath,
    },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
}

async function stopProxy(child) {
  if (child.exitCode !== null) return;
  child.kill('SIGTERM');
  await new Promise((resolve, reject) => {
    child.once('exit', resolve);
    setTimeout(() => reject(new Error('proxy shutdown timeout')), 3000);
  });
}

async function waitForExit(child) {
  if (child.exitCode !== null) return child.exitCode;
  return new Promise((resolve, reject) => {
    child.once('exit', resolve);
    setTimeout(() => reject(new Error('child exit timeout')), 3000);
  });
}

async function request(body, authorization = 'Bearer fake-client-key') {
  return fetch(`http://127.0.0.1:${proxyPort}/v1/chat/completions`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization },
    body: JSON.stringify(body),
  });
}

let proxy;
try {
  await new Promise((resolve, reject) => {
    upstream.once('error', reject);
    upstream.listen(0, '127.0.0.1', resolve);
  });
  upstreamPort = upstream.address().port;
  const reservation = http.createServer();
  await new Promise((resolve, reject) => {
    reservation.once('error', reject);
    reservation.listen(0, '127.0.0.1', resolve);
  });
  proxyPort = reservation.address().port;
  await new Promise((resolve, reject) => reservation.close(error => error ? reject(error) : resolve()));
  proxy = startProxy();
  await waitForHealth();

  const concurrent = startProxy();
  if ((await waitForExit(concurrent)) === 0) throw new Error('concurrent proxy was not rejected');

  if ((await request({ model: 'wrong', max_tokens: 1, messages: [] })).status !== 400) throw new Error('wrong model was not rejected');
  if ((await request({ model: 'fake-fixed-model', messages: [] })).status !== 400) throw new Error('missing output cap was not rejected');
  if ((await request({ model: 'fake-fixed-model', max_tokens: 9, messages: [] })).status !== 400) throw new Error('excess output cap was not rejected');
  if ((await request({ model: 'fake-fixed-model', max_tokens: 1, messages: [] }, 'Bearer wrong')).status !== 401) throw new Error('wrong client key was not rejected');

  const valid = { model: 'fake-fixed-model', max_tokens: 8, messages: [{ role: 'user', content: 'synthetic' }] };
  for (let i = 0; i < 17; i++) {
    if (!(await request(valid)).ok) throw new Error(`valid request ${i + 1} failed before restart`);
  }
  await stopProxy(proxy);

  let ledger = JSON.parse(await readFile(statePath, 'utf8'));
  if (ledger.claimed_attempts !== 17 || upstreamCalls !== 17) throw new Error('pre-restart claims were not persisted');

  proxy = startProxy('3');
  const health = await waitForHealth();
  if (health.claimed_attempts !== 17 || health.remaining_attempts !== 24
    || health.session_claimed_attempts !== 0 || health.session_remaining_attempts !== 3) {
    throw new Error('restart did not restore the ledger or session budget');
  }
  for (let i = 17; i < 20; i++) {
    if (!(await request(valid)).ok) throw new Error(`valid request ${i + 1} failed after restart`);
  }
  if ((await request(valid)).status !== 429) throw new Error('per-run request 4 was not blocked');
  await stopProxy(proxy);

  proxy = startProxy();
  await waitForHealth();
  for (let i = 20; i < 41; i++) {
    if (!(await request(valid)).ok) throw new Error(`valid request ${i + 1} failed after second restart`);
  }
  if ((await request(valid)).status !== 429) throw new Error('request 42 was not blocked');

  ledger = JSON.parse(await readFile(statePath, 'utf8'));
  if (ledger.claimed_attempts !== 41 || ledger.attempts.length !== 41 || upstreamCalls !== 41) throw new Error('final ledger or upstream count mismatch');
  console.log(JSON.stringify({ status: 'passed', concurrent_proxy_rejected: true, rejected_invalid_without_claim: 4, restart_restored_claims: true, per_run_cap_enforced: 3, accepted_attempts: 41, blocked_attempt: 42, upstream_calls: upstreamCalls }));
} finally {
  if (proxy) await stopProxy(proxy).catch(() => {});
  await new Promise(resolve => upstream.close(resolve));
  await rm(temp, { recursive: true, force: true });
}
