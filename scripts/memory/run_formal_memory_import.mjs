import { randomBytes } from 'node:crypto';
import { execFile as execFileCallback, spawn } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const root = path.resolve(new URL('../..', import.meta.url).pathname);
const docker = '/opt/homebrew/bin/docker';
const dockerContext = 'colima-memory-pilot';
const image = 'sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const volume = 'tdai-ramp-metering-memory-v1';
const containerScript = path.join(root, 'scripts/memory/formal_import_container.mjs');
const probeScript = path.join(root, 'scripts/memory/formal_persistence_probe.mjs');
const bundlePath = path.join(root, 'docs/memory/formal_import_bundle_20260909.md');
const legacyLedgerPath = path.join(root, 'data/processed/memory_paid_synthetic_20260909/ledger.json');
const ledgerPath = path.join(root, 'data/processed/memory_formal_import_20260909/ledger_gpt-4.1-mini.json');
const resultDir = path.join(root, 'data/processed/memory_formal_import_20260909');
const receiptPath = path.join(resultDir, 'receipt_alias_attempt2.json');
const proxyScript = path.join(root, 'scripts/memory/openai_budget_proxy.mjs');
const clientKey = randomBytes(32).toString('hex');
let proxy;
let containerId;
let proxyStderr = '';

async function dockerExec(args, options = {}) {
  return execFile(docker, ['--context', dockerContext, ...args], {
    maxBuffer: 10 * 1024 * 1024,
    timeout: 12 * 60 * 1000,
    ...options,
  });
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

function parseLastJson(stdout) {
  const lines = stdout.trim().split('\n').filter(Boolean);
  return JSON.parse(lines.at(-1) || '{}');
}

const bundle = await readFile(bundlePath, 'utf8');
if (Buffer.byteLength(bundle) > 12000) throw new Error('Formal import bundle exceeds the reviewed 12,000-byte ceiling');
console.error('[formal-memory] bundle and source paths validated');

const legacyLedger = JSON.parse(await readFile(legacyLedgerPath, 'utf8'));
if (legacyLedger.claimed_attempts !== 4 || legacyLedger.attempts?.length !== 4
  || legacyLedger.attempts.some(item => Number(item.usage?.total_tokens) > 0)) {
  throw new Error('Legacy fixed-snapshot ledger is not at the reviewed four zero-token attempts');
}
let ledgerBefore;
try {
  ledgerBefore = JSON.parse(await readFile(ledgerPath, 'utf8'));
} catch (error) {
  if (error?.code !== 'ENOENT') throw error;
  ledgerBefore = { claimed_attempts: 0, attempts: [] };
}
if (!Number.isSafeInteger(ledgerBefore.claimed_attempts)
  || ledgerBefore.claimed_attempts < 0 || ledgerBefore.claimed_attempts >= 37
  || ledgerBefore.attempts?.length !== ledgerBefore.claimed_attempts) {
  throw new Error('Alias-model ledger state is incompatible or exhausted');
}
console.error(`[formal-memory] combined budget restored at ${4 + ledgerBefore.claimed_attempts}/41`);

console.error('[formal-memory] requesting project key from macOS Keychain');
const keyResult = await execFile('/usr/bin/security', [
  'find-generic-password', '-w',
  '-a', 'ramp-metering-memory',
  '-s', 'openai-api-key-ramp-metering-memory',
], { maxBuffer: 1024 * 1024 });
const upstreamApiKey = keyResult.stdout.trim();
if (!upstreamApiKey.startsWith('sk-') || upstreamApiKey.length < 150
  || /\s/.test(upstreamApiKey) || (upstreamApiKey.match(/sk-/g) ?? []).length !== 1) {
  throw new Error('Keychain secret metadata does not match one complete project API key');
}
console.error('[formal-memory] Keychain metadata validation passed');

const volumeList = (await dockerExec(['volume', 'ls', '--format', '{{.Name}}'])).stdout.trim().split('\n');
const reuseInitializedVolume = volumeList.includes(volume);
await dockerExec(['image', 'inspect', image]);
console.error(`[formal-memory] Docker preflight passed; reuse_initialized_volume=${reuseInitializedVolume}`);

proxy = spawn(process.execPath, [proxyScript], {
  cwd: root,
  env: {
    ...process.env,
    BUDGET_PROXY_HOST: '0.0.0.0',
    BUDGET_PROXY_PORT: '18430',
    BUDGET_PROXY_UPSTREAM_BASE_URL: 'https://api.openai.com/v1',
    BUDGET_PROXY_UPSTREAM_API_KEY: upstreamApiKey,
    BUDGET_PROXY_CLIENT_API_KEY: clientKey,
    BUDGET_PROXY_MODEL: 'gpt-4.1-mini',
    BUDGET_PROXY_MAX_ATTEMPTS: '37',
    BUDGET_PROXY_MAX_REQUEST_BYTES: '20000',
    BUDGET_PROXY_MAX_OUTPUT_TOKENS: '4096',
    BUDGET_PROXY_STATE_PATH: ledgerPath,
  },
  stdio: ['ignore', 'ignore', 'pipe'],
});
proxy.stderr.on('data', chunk => { proxyStderr += chunk; });

let nativeResult;
let persistenceResult;
let importError;
try {
  const health = await waitForProxy();
  if (health.claimed_attempts !== ledgerBefore.claimed_attempts
    || health.remaining_attempts !== 37 - ledgerBefore.claimed_attempts) {
    throw new Error('Budget proxy did not restore the reviewed ledger state');
  }
  console.error(`[formal-memory] paid proxy ready; combined remaining=${37 - ledgerBefore.claimed_attempts}`);
  if (!reuseInitializedVolume) {
    await dockerExec(['volume', 'create', '--label', 'project=Masterarbeit-Ramp-Metering', '--label', 'purpose=formal-layered-memory', volume]);
  }

  const created = await dockerExec([
    'create', '--pull=never', '--network', 'bridge', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,size=32m',
    '--mount', `type=volume,source=${volume},target=/data`,
    '--env', 'MEMORY_PROXY_BASE_URL=http://host.docker.internal:18430/v1',
    '--env', `MEMORY_PROXY_CLIENT_KEY=${clientKey}`,
    '--entrypoint', 'node', image, '/formal_import_container.mjs',
  ]);
  containerId = created.stdout.trim();
  if (!/^[a-f0-9]{64}$/.test(containerId)) throw new Error('Unexpected Docker container id');
  await dockerExec(['cp', containerScript, `${containerId}:/formal_import_container.mjs`]);
  await dockerExec(['cp', bundlePath, `${containerId}:/formal_import_bundle.md`]);
  console.error('[formal-memory] starting native L0-L3 import');

  let runResult;
  try {
    runResult = await dockerExec(['start', '--attach', containerId]);
  } catch (error) {
    runResult = { stdout: error.stdout || '', stderr: error.stderr || '' };
  }
  nativeResult = parseLastJson(runResult.stdout);
  if (nativeResult.status !== 'passed') {
    throw new Error(`Native formal import failed: ${JSON.stringify(nativeResult)} ${runResult.stderr.slice(-2000)}`);
  }
  console.error('[formal-memory] native L0-L3 import passed; stopping network proxy');

  await dockerExec(['rm', '-f', containerId]);
  containerId = undefined;
  await stopProxy();

  const probeCreated = await dockerExec([
    'create', '--pull=never', '--network', 'none', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,size=16m',
    '--mount', `type=volume,source=${volume},target=/data`,
    '--entrypoint', 'node', image, '/formal_persistence_probe.mjs',
  ]);
  containerId = probeCreated.stdout.trim();
  await dockerExec(['cp', probeScript, `${containerId}:/formal_persistence_probe.mjs`]);
  console.error('[formal-memory] starting network-disabled restart probe');
  let probeRun;
  try {
    probeRun = await dockerExec(['start', '--attach', containerId]);
  } catch (error) {
    probeRun = { stdout: error.stdout || '', stderr: error.stderr || '' };
  }
  persistenceResult = parseLastJson(probeRun.stdout);
  if (persistenceResult.status !== 'passed') {
    throw new Error(`Restart persistence probe failed: ${JSON.stringify(persistenceResult)} ${probeRun.stderr.slice(-2000)}`);
  }
} catch (error) {
  importError = error;
} finally {
  await stopProxy();
  if (containerId) await dockerExec(['rm', '-f', containerId]).catch(() => {});
}

const ledgerAfter = JSON.parse(await readFile(ledgerPath, 'utf8'));
const newAttempts = ledgerAfter.attempts.slice(ledgerBefore.claimed_attempts);
const promptTokens = newAttempts.reduce((sum, item) => sum + (Number(item.usage?.prompt_tokens) || 0), 0);
const completionTokens = newAttempts.reduce((sum, item) => sum + (Number(item.usage?.completion_tokens) || 0), 0);
const estimatedUsd = promptTokens * 0.40 / 1_000_000 + completionTokens * 1.60 / 1_000_000;
const receipt = {
  status: importError ? 'failed' : 'passed',
  created_at: new Date().toISOString(),
  project: 'Masterarbeit-Ramp-Metering',
  volume,
  image,
  model: 'gpt-4.1-mini',
  source_bundle: path.relative(root, bundlePath),
  reused_initialized_volume: reuseInitializedVolume,
  native_result: nativeResult ?? null,
  restart_persistence_probe: persistenceResult ?? null,
  budget: {
    prior_claimed_attempts: ledgerBefore.claimed_attempts,
    new_claimed_attempts: newAttempts.length,
    legacy_claimed_attempts: legacyLedger.claimed_attempts,
    alias_claimed_attempts: ledgerAfter.claimed_attempts,
    total_claimed_attempts: legacyLedger.claimed_attempts + ledgerAfter.claimed_attempts,
    remaining_attempts: 41 - legacyLedger.claimed_attempts - ledgerAfter.claimed_attempts,
    prompt_tokens: promptTokens,
    completion_tokens: completionTokens,
    total_tokens: promptTokens + completionTokens,
    estimated_usd_at_published_text_rates: Number(estimatedUsd.toFixed(8)),
    ledger_path: path.relative(root, ledgerPath),
  },
  error: importError instanceof Error ? importError.message : importError ? String(importError) : null,
};
await mkdir(resultDir, { recursive: true });
await writeFile(receiptPath, `${JSON.stringify(receipt, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ ...receipt, receipt_path: path.relative(root, receiptPath) }));
if (importError) process.exitCode = 1;
