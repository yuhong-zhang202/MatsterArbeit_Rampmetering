import http from 'node:http';
import { createHash, randomUUID, timingSafeEqual } from 'node:crypto';
import { mkdir, open, readFile, rename, unlink } from 'node:fs/promises';
import path from 'node:path';

function required(name) {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`${name} is required`);
  return value;
}

function integer(name, fallback, min, max) {
  const raw = process.env[name]?.trim();
  const value = raw ? Number(raw) : fallback;
  if (!Number.isSafeInteger(value) || value < min || value > max) {
    throw new Error(`${name} must be an integer in [${min}, ${max}]`);
  }
  return value;
}

function safeEqual(left, right) {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
}

const config = {
  host: process.env.BUDGET_PROXY_HOST?.trim() || '127.0.0.1',
  port: integer('BUDGET_PROXY_PORT', 18430, 1, 65535),
  upstreamBaseUrl: required('BUDGET_PROXY_UPSTREAM_BASE_URL').replace(/\/$/, ''),
  upstreamApiKey: required('BUDGET_PROXY_UPSTREAM_API_KEY'),
  clientApiKey: required('BUDGET_PROXY_CLIENT_API_KEY'),
  model: process.env.BUDGET_PROXY_MODEL?.trim() || 'gpt-4.1-mini-2025-04-14',
  maxAttempts: integer('BUDGET_PROXY_MAX_ATTEMPTS', 41, 1, 1000),
  maxNewAttempts: integer('BUDGET_PROXY_MAX_NEW_ATTEMPTS', 41, 1, 1000),
  maxRequestBytes: integer('BUDGET_PROXY_MAX_REQUEST_BYTES', 20000, 256, 10_000_000),
  maxOutputTokens: integer('BUDGET_PROXY_MAX_OUTPUT_TOKENS', 4096, 1, 1_000_000),
  statePath: path.resolve(required('BUDGET_PROXY_STATE_PATH')),
};

const upstreamUrl = new URL(`${config.upstreamBaseUrl}/chat/completions`);
if (upstreamUrl.protocol !== 'https:' && process.env.BUDGET_PROXY_ALLOW_INSECURE_UPSTREAM !== 'true') {
  throw new Error('Non-HTTPS upstream requires BUDGET_PROXY_ALLOW_INSECURE_UPSTREAM=true');
}

const policy = {
  model: config.model,
  max_attempts: config.maxAttempts,
  max_request_bytes: config.maxRequestBytes,
  max_output_tokens: config.maxOutputTokens,
  upstream_origin: upstreamUrl.origin,
  upstream_path: upstreamUrl.pathname,
};
const policyHash = createHash('sha256').update(JSON.stringify(policy)).digest('hex');
let ledger;
let sessionStartClaims;
let mutation = Promise.resolve();
let lockHandle;
const lockPath = `${config.statePath}.lock`;

async function acquireProcessLock() {
  await mkdir(path.dirname(config.statePath), { recursive: true, mode: 0o700 });
  try {
    lockHandle = await open(lockPath, 'wx', 0o600);
    await lockHandle.writeFile(`${JSON.stringify({ pid: process.pid, created_at: new Date().toISOString() })}\n`, 'utf8');
    await lockHandle.sync();
  } catch (error) {
    if (error?.code === 'EEXIST') {
      throw new Error(`Budget ledger lock already exists: ${lockPath}. Refusing concurrent or unaudited restart.`);
    }
    throw error;
  }
}

async function releaseProcessLock() {
  if (!lockHandle) return;
  await lockHandle.close();
  lockHandle = undefined;
  await unlink(lockPath).catch(error => {
    if (error?.code !== 'ENOENT') throw error;
  });
}

async function persist(next) {
  await mkdir(path.dirname(config.statePath), { recursive: true, mode: 0o700 });
  const temporary = `${config.statePath}.${process.pid}.${randomUUID()}.tmp`;
  const handle = await open(temporary, 'wx', 0o600);
  try {
    await handle.writeFile(`${JSON.stringify(next, null, 2)}\n`, 'utf8');
    await handle.sync();
  } finally {
    await handle.close();
  }
  await rename(temporary, config.statePath);
}

async function initialize() {
  try {
    ledger = JSON.parse(await readFile(config.statePath, 'utf8'));
    if (ledger.schema_version !== 1 || ledger.policy_hash !== policyHash) {
      throw new Error('Existing budget ledger policy does not match current policy');
    }
    if (!Number.isSafeInteger(ledger.claimed_attempts) || !Array.isArray(ledger.attempts)) {
      throw new Error('Existing budget ledger is malformed');
    }
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
    ledger = {
      schema_version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      policy_hash: policyHash,
      policy,
      claimed_attempts: 0,
      attempts: [],
    };
    await persist(ledger);
  }
  sessionStartClaims = ledger.claimed_attempts;
}

function mutate(operation) {
  const result = mutation.then(operation, operation);
  mutation = result.catch(() => {});
  return result;
}

async function claimAttempt(requestBytes, requestedOutputTokens) {
  return mutate(async () => {
    if (ledger.claimed_attempts >= config.maxAttempts) return null;
    if (ledger.claimed_attempts - sessionStartClaims >= config.maxNewAttempts) return null;
    const record = {
      id: randomUUID(),
      claimed_at: new Date().toISOString(),
      request_bytes: requestBytes,
      requested_output_tokens: requestedOutputTokens,
      outcome: 'claimed_before_forward',
    };
    ledger.claimed_attempts += 1;
    ledger.updated_at = new Date().toISOString();
    ledger.attempts.push(record);
    await persist(ledger);
    return record.id;
  });
}

async function finishAttempt(id, patch) {
  await mutate(async () => {
    const record = ledger.attempts.find(item => item.id === id);
    if (!record) throw new Error(`Unknown attempt ${id}`);
    Object.assign(record, patch, { finished_at: new Date().toISOString() });
    ledger.updated_at = new Date().toISOString();
    await persist(ledger);
  });
}

function sendJson(res, status, body) {
  const payload = Buffer.from(JSON.stringify(body));
  res.writeHead(status, { 'content-type': 'application/json', 'content-length': payload.length });
  res.end(payload);
}

async function readBoundedBody(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > config.maxRequestBytes) throw Object.assign(new Error('request too large'), { statusCode: 413 });
    chunks.push(chunk);
  }
  return Buffer.concat(chunks, size);
}

function validateBody(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return 'JSON body must be an object';
  if (body.model !== config.model) return `model must be ${config.model}`;
  if (body.stream === true) return 'streaming is disabled for auditable accounting';
  const output = body.max_completion_tokens ?? body.max_tokens;
  if (!Number.isSafeInteger(output) || output < 1 || output > config.maxOutputTokens) {
    return `max_tokens or max_completion_tokens must be an integer in [1, ${config.maxOutputTokens}]`;
  }
  return null;
}

await acquireProcessLock();
try {
  await initialize();
} catch (error) {
  await releaseProcessLock();
  throw error;
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'GET' && req.url === '/health') {
    const sessionClaimedAttempts = ledger.claimed_attempts - sessionStartClaims;
    sendJson(res, 200, {
      ok: true,
      claimed_attempts: ledger.claimed_attempts,
      remaining_attempts: config.maxAttempts - ledger.claimed_attempts,
      session_claimed_attempts: sessionClaimedAttempts,
      session_remaining_attempts: config.maxNewAttempts - sessionClaimedAttempts,
      session_max_new_attempts: config.maxNewAttempts,
      policy,
    });
    return;
  }
  if (req.method !== 'POST' || req.url !== '/v1/chat/completions') {
    sendJson(res, 404, { error: { message: 'not found' } });
    return;
  }
  const authorization = req.headers.authorization || '';
  if (!safeEqual(authorization, `Bearer ${config.clientApiKey}`)) {
    sendJson(res, 401, { error: { message: 'unauthorized' } });
    return;
  }

  let raw;
  let body;
  try {
    raw = await readBoundedBody(req);
    body = JSON.parse(raw.toString('utf8'));
  } catch (error) {
    sendJson(res, error.statusCode || 400, { error: { message: error.statusCode ? error.message : 'invalid JSON' } });
    return;
  }
  const invalid = validateBody(body);
  if (invalid) {
    sendJson(res, 400, { error: { message: invalid } });
    return;
  }
  const requestedOutputTokens = body.max_completion_tokens ?? body.max_tokens;
  const attemptId = await claimAttempt(raw.length, requestedOutputTokens);
  if (!attemptId) {
    sendJson(res, 429, { error: { message: 'persistent or per-run model-attempt budget exhausted', type: 'budget_gate' } });
    return;
  }

  try {
    const upstream = await fetch(upstreamUrl, {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${config.upstreamApiKey}` },
      body: raw,
      signal: AbortSignal.timeout(120000),
    });
    const responseBody = Buffer.from(await upstream.arrayBuffer());
    let usage = null;
    try { usage = JSON.parse(responseBody.toString('utf8')).usage ?? null; } catch {}
    await finishAttempt(attemptId, { outcome: 'response_received', upstream_status: upstream.status, usage });
    res.writeHead(upstream.status, { 'content-type': upstream.headers.get('content-type') || 'application/json', 'content-length': responseBody.length });
    res.end(responseBody);
  } catch (error) {
    await finishAttempt(attemptId, { outcome: 'transport_error', error_class: error?.name || 'Error' });
    sendJson(res, 502, { error: { message: 'upstream request failed after budget claim' } });
  }
});

server.listen(config.port, config.host, () => {
  console.log(JSON.stringify({ status: 'ready', host: config.host, port: config.port, state_path: config.statePath, policy }));
});

server.on('error', async error => {
  console.error(JSON.stringify({ status: 'failed', error: error.message }));
  await releaseProcessLock().catch(() => {});
  process.exit(1);
});

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => server.close(async () => {
    await releaseProcessLock();
    process.exit(0);
  }));
}
