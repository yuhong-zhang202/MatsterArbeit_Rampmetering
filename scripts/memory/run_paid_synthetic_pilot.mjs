import { randomBytes } from 'node:crypto';
import { execFile as execFileCallback, spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const root = path.resolve(new URL('../..', import.meta.url).pathname);
const docker = '/opt/homebrew/bin/docker';
const dockerContext = 'colima-memory-pilot';
const image = 'sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const ledgerPath = path.join(root, 'data/processed/memory_paid_synthetic_20260909/ledger.json');
const containerScript = path.join(root, 'scripts/memory/paid_synthetic_container.mjs');
const proxyScript = path.join(root, 'scripts/memory/openai_budget_proxy.mjs');
const clientKey = randomBytes(32).toString('hex');
let proxy;
let containerId;
let proxyStderr = '';

async function loadExistingClaims(target) {
  try {
    const existing = JSON.parse(await readFile(target, 'utf8'));
    const expectedPolicy = {
      model: 'gpt-4.1-mini-2025-04-14',
      max_attempts: 41,
      max_request_bytes: 20000,
      max_output_tokens: 4096,
      upstream_origin: 'https://api.openai.com',
      upstream_path: '/v1/chat/completions',
    };
    if (JSON.stringify(existing.policy) !== JSON.stringify(expectedPolicy)
      || !Number.isSafeInteger(existing.claimed_attempts)
      || existing.claimed_attempts < 0
      || existing.claimed_attempts >= 41
      || existing.attempts?.length !== existing.claimed_attempts) {
      throw new Error(`Existing paid-pilot ledger is incompatible or exhausted: ${target}`);
    }
    return existing.claimed_attempts;
  } catch (error) {
    if (error?.code === 'ENOENT') return 0;
    throw error;
  }
}

async function waitForProxy() {
  for (let i = 0; i < 100; i++) {
    if (proxy.exitCode !== null) throw new Error(`budget proxy exited early: ${proxyStderr.slice(-1000)}`);
    try {
      const response = await fetch('http://127.0.0.1:18430/health', { signal: AbortSignal.timeout(300) });
      if (response.ok) return response.json();
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  throw new Error('budget proxy startup timeout');
}

async function stopProxy() {
  if (!proxy || proxy.exitCode !== null) return;
  proxy.kill('SIGTERM');
  await new Promise(resolve => {
    proxy.once('exit', resolve);
    setTimeout(resolve, 3000);
  });
}

async function dockerExec(args, options = {}) {
  return execFile(docker, ['--context', dockerContext, ...args], {
    maxBuffer: 10 * 1024 * 1024,
    ...options,
  });
}

function sumUsage(ledger, field) {
  return ledger.attempts.reduce((sum, item) => sum + (Number(item.usage?.[field]) || 0), 0);
}

const existingClaims = await loadExistingClaims(ledgerPath);
const keyResult = await execFile('/usr/bin/security', [
  'find-generic-password',
  '-w',
  '-a', 'ramp-metering-memory',
  '-s', 'openai-api-key-ramp-metering-memory',
], { maxBuffer: 1024 * 1024 });
const upstreamApiKey = keyResult.stdout.trim();
if (upstreamApiKey.length < 20) throw new Error('Keychain secret is unexpectedly short');

proxy = spawn(process.execPath, [proxyScript], {
  cwd: root,
  env: {
    ...process.env,
    BUDGET_PROXY_HOST: '0.0.0.0',
    BUDGET_PROXY_PORT: '18430',
    BUDGET_PROXY_UPSTREAM_BASE_URL: 'https://api.openai.com/v1',
    BUDGET_PROXY_UPSTREAM_API_KEY: upstreamApiKey,
    BUDGET_PROXY_CLIENT_API_KEY: clientKey,
    BUDGET_PROXY_MODEL: 'gpt-4.1-mini-2025-04-14',
    BUDGET_PROXY_MAX_ATTEMPTS: '41',
    BUDGET_PROXY_MAX_REQUEST_BYTES: '20000',
    BUDGET_PROXY_MAX_OUTPUT_TOKENS: '4096',
    BUDGET_PROXY_STATE_PATH: ledgerPath,
  },
  stdio: ['ignore', 'ignore', 'pipe'],
});
proxy.stderr.on('data', chunk => { proxyStderr += chunk; });

try {
  const initialHealth = await waitForProxy();
  if (initialHealth.claimed_attempts !== existingClaims || initialHealth.remaining_attempts !== 41 - existingClaims) {
    throw new Error('budget ledger did not restore the expected attempt count');
  }

  const connectivity = await dockerExec([
    'run', '--rm', '--pull=never', '--network', 'bridge', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--entrypoint', 'node', image,
    '-e', `fetch('http://host.docker.internal:18430/health').then(r=>{if(!r.ok)throw Error(String(r.status));return r.json()}).then(x=>{if(x.remaining_attempts!==${41 - existingClaims})throw Error('unexpected health');console.log('proxy-reachable')})`,
  ]);
  if (!connectivity.stdout.includes('proxy-reachable')) throw new Error('container-to-proxy check failed');

  const created = await dockerExec([
    'create', '--pull=never', '--network', 'bridge', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--tmpfs', '/data:rw,size=64m',
    '--env', 'PILOT_PROXY_BASE_URL=http://host.docker.internal:18430/v1',
    '--env', `PILOT_PROXY_CLIENT_KEY=${clientKey}`,
    '--entrypoint', 'node', image, '/tmp/paid_synthetic_container.mjs',
  ]);
  containerId = created.stdout.trim();
  if (!/^[a-f0-9]{64}$/.test(containerId)) throw new Error('unexpected Docker container id');
  await dockerExec(['cp', containerScript, `${containerId}:/tmp/paid_synthetic_container.mjs`]);

  let containerResult;
  let containerExitCode = 0;
  try {
    containerResult = await dockerExec(['start', '--attach', containerId]);
  } catch (error) {
    containerExitCode = error.code ?? 1;
    containerResult = { stdout: error.stdout || '', stderr: error.stderr || '' };
  }
  const outputLines = containerResult.stdout.trim().split('\n').filter(Boolean);
  const nativeResult = JSON.parse(outputLines.at(-1) || '{}');

  await stopProxy();
  const ledger = JSON.parse(await readFile(ledgerPath, 'utf8'));
  const promptTokens = sumUsage(ledger, 'prompt_tokens');
  const completionTokens = sumUsage(ledger, 'completion_tokens');
  const totalTokens = sumUsage(ledger, 'total_tokens');
  const estimatedUsd = promptTokens * 0.40 / 1_000_000 + completionTokens * 1.60 / 1_000_000;
  console.log(JSON.stringify({
    status: nativeResult.status === 'passed' && containerExitCode === 0 ? 'passed' : 'failed',
    native_result: nativeResult,
    budget: {
      claimed_attempts: ledger.claimed_attempts,
      remaining_attempts: 41 - ledger.claimed_attempts,
      prompt_tokens: promptTokens,
      completion_tokens: completionTokens,
      total_tokens: totalTokens,
      estimated_usd_at_published_text_rates: Number(estimatedUsd.toFixed(8)),
      ledger_path: ledgerPath,
    },
    container_stderr_tail: containerResult.stderr.slice(-2000),
  }));
  if (nativeResult.status !== 'passed' || containerExitCode !== 0) process.exitCode = 1;
} finally {
  await stopProxy();
  if (containerId) await dockerExec(['rm', '-f', containerId]).catch(() => {});
}
