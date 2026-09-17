import { randomBytes } from 'node:crypto';
import { execFile as execFileCallback, spawn } from 'node:child_process';
import { access, mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';
import { FIXED_MEMORY_POLICY, validateIncrementalApproval } from './incremental_update_policy.mjs';

const execFile = promisify(execFileCallback);
const root = path.resolve(new URL('../..', import.meta.url).pathname);
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const approvalIndex = args.indexOf('--approval');
if (approvalIndex < 0 || !args[approvalIndex + 1] || args.length !== (dryRun ? 3 : 2)
  || args.filter(item => item === '--approval').length !== 1 || args.filter(item => item === '--dry-run').length > 1) {
  throw new Error('Usage: node scripts/memory/run_incremental_memory_update.mjs --approval docs/memory/<approved.json> [--dry-run]');
}

const approval = await validateIncrementalApproval({ root, manifestPath: args[approvalIndex + 1], dryRun });
const { manifest, fixed_policy: fixed } = approval;
const docker = '/opt/homebrew/bin/docker';
const dockerContext = 'colima-memory-pilot';
const image = 'sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const legacyLedgerPath = path.join(root, 'data/processed/memory_paid_synthetic_20260909/ledger.json');
const ledgerPath = path.join(root, 'data/processed/memory_formal_import_20260909/ledger_gpt-4.1-mini.json');
const resultDir = path.join(root, `data/processed/memory_incremental_${manifest.update_id}`);
const receiptPath = path.join(resultDir, 'receipt.json');
const proxyScript = path.join(root, 'scripts/memory/openai_budget_proxy.mjs');
const containerScript = path.join(root, 'scripts/memory/incremental_update_container.mjs');
const probeScript = path.join(root, 'scripts/memory/formal_persistence_probe.mjs');

async function mustNotExist(target, label) {
  try { await access(target); } catch (error) { if (error?.code === 'ENOENT') return; throw error; }
  throw new Error(`${label} already exists; refusing replay: ${target}`);
}

const legacyLedger = JSON.parse(await readFile(legacyLedgerPath, 'utf8'));
if (legacyLedger.claimed_attempts !== fixed.legacy_attempts || legacyLedger.attempts?.length !== fixed.legacy_attempts
  || legacyLedger.attempts.some(item => Number(item.usage?.total_tokens) > 0)) {
  throw new Error('Legacy ledger is not the reviewed four zero-token attempts');
}
const ledgerBefore = JSON.parse(await readFile(ledgerPath, 'utf8'));
const expectedPolicy = {
  model: fixed.model,
  max_attempts: fixed.alias_attempt_ceiling,
  max_request_bytes: fixed.max_request_bytes,
  max_output_tokens: fixed.max_output_tokens,
  upstream_origin: 'https://api.openai.com',
  upstream_path: '/v1/chat/completions',
};
if (JSON.stringify(ledgerBefore.policy) !== JSON.stringify(expectedPolicy)
  || ledgerBefore.attempts?.length !== ledgerBefore.claimed_attempts
  || ledgerBefore.claimed_attempts < 0 || ledgerBefore.claimed_attempts >= fixed.alias_attempt_ceiling) {
  throw new Error('Persistent alias ledger does not match the fixed reviewed policy');
}
const remaining = fixed.alias_attempt_ceiling - ledgerBefore.claimed_attempts;
if (manifest.max_new_attempts > remaining) throw new Error(`Approved per-run budget ${manifest.max_new_attempts} exceeds ${remaining} remaining attempts`);
await mustNotExist(receiptPath, 'Incremental update receipt');

const plan = {
  status: 'validated', mode: dryRun ? 'dry-run' : 'execute', project: fixed.project,
  update_id: manifest.update_id, session_id: manifest.session_id,
  approval_manifest: path.relative(root, approval.manifest_path), approval_manifest_sha256: approval.manifest_sha256,
  files: {
    delta_bundle: { path: approval.bundle.relative_path, bytes: approval.bundle.bytes, sha256: approval.bundle.sha256 },
    l3_candidate: { path: approval.core.relative_path, bytes: approval.core.bytes, sha256: approval.core.sha256 },
  },
  model: fixed.model, approved_max_new_attempts: manifest.max_new_attempts,
  approved_cost: {
    input_rate_usd_per_million: manifest.input_rate_usd_per_million,
    output_rate_usd_per_million: manifest.output_rate_usd_per_million,
    conservative_cost_ceiling_usd: Number(approval.conservative_cost_ceiling_usd.toFixed(8)),
    approved_cost_ceiling_usd: manifest.approved_cost_ceiling_usd,
  },
  historical_claimed_attempts: fixed.legacy_attempts + ledgerBefore.claimed_attempts,
  historical_remaining_attempts: remaining,
  network_or_api_access_performed: false,
};
if (dryRun) {
  console.log(JSON.stringify(plan, null, 2));
  process.exit(0);
}

const clientKey = randomBytes(32).toString('hex');
let proxy;
let proxyStderr = '';
let containerId;
let nativeResult;
let persistenceResult;
let executionError;
let keychainAccessPerformed = false;
let dockerAccessPerformed = false;

async function dockerExec(dockerArgs, options = {}) {
  return execFile(docker, ['--context', dockerContext, ...dockerArgs], { maxBuffer: 20 * 1024 * 1024, timeout: 12 * 60 * 1000, ...options });
}
async function stopProxy() {
  if (!proxy || proxy.exitCode !== null) return;
  proxy.kill('SIGTERM');
  await new Promise(resolve => { proxy.once('exit', resolve); setTimeout(resolve, 3000); });
}
async function waitForProxy() {
  for (let i = 0; i < 100; i++) {
    if (proxy.exitCode !== null) throw new Error(`Budget proxy exited early: ${proxyStderr.slice(-1000)}`);
    try {
      const response = await fetch('http://127.0.0.1:18430/health', { signal: AbortSignal.timeout(300) });
      if (response.ok) return response.json();
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  throw new Error('Budget proxy startup timeout');
}
function parseLastJson(stdout) {
  const lines = stdout.trim().split('\n').filter(Boolean);
  return JSON.parse(lines.at(-1) || '{}');
}

try {
  console.error('[incremental-memory] local approval, hashes, ledger and replay guards passed');
  const keyResult = await execFile('/usr/bin/security', [
    'find-generic-password', '-w', '-a', 'ramp-metering-memory', '-s', 'openai-api-key-ramp-metering-memory',
  ], { maxBuffer: 1024 * 1024 });
  keychainAccessPerformed = true;
  const upstreamApiKey = keyResult.stdout.trim();
  if (!upstreamApiKey.startsWith('sk-') || upstreamApiKey.length < 100 || /\s/.test(upstreamApiKey)
    || (upstreamApiKey.match(/sk-/g) ?? []).length !== 1) throw new Error('Keychain entry is not one complete API key');

  dockerAccessPerformed = true;
  const volumeNames = (await dockerExec(['volume', 'ls', '--format', '{{.Name}}'])).stdout.trim().split('\n');
  if (!volumeNames.includes(fixed.volume)) throw new Error(`Formal memory volume ${fixed.volume} does not exist`);
  await dockerExec(['image', 'inspect', image]);

  proxy = spawn(process.execPath, [proxyScript], {
    cwd: root,
    env: {
      ...process.env,
      BUDGET_PROXY_HOST: '0.0.0.0', BUDGET_PROXY_PORT: '18430',
      BUDGET_PROXY_UPSTREAM_BASE_URL: 'https://api.openai.com/v1', BUDGET_PROXY_UPSTREAM_API_KEY: upstreamApiKey,
      BUDGET_PROXY_CLIENT_API_KEY: clientKey, BUDGET_PROXY_MODEL: fixed.model,
      BUDGET_PROXY_MAX_ATTEMPTS: String(fixed.alias_attempt_ceiling),
      BUDGET_PROXY_MAX_NEW_ATTEMPTS: String(manifest.max_new_attempts),
      BUDGET_PROXY_MAX_REQUEST_BYTES: String(fixed.max_request_bytes),
      BUDGET_PROXY_MAX_OUTPUT_TOKENS: String(fixed.max_output_tokens),
      BUDGET_PROXY_STATE_PATH: ledgerPath,
    },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  proxy.stderr.on('data', chunk => { proxyStderr += chunk; });
  const health = await waitForProxy();
  if (health.claimed_attempts !== ledgerBefore.claimed_attempts || health.session_max_new_attempts !== manifest.max_new_attempts) {
    throw new Error('Budget proxy did not restore the fixed global and approved per-run budgets');
  }

  const created = await dockerExec([
    'create', '--pull=never', '--network', 'bridge', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
    '--tmpfs', '/tmp:rw,size=32m', '--mount', `type=volume,source=${fixed.volume},target=/data`,
    '--env', 'MEMORY_PROXY_BASE_URL=http://host.docker.internal:18430/v1', '--env', `MEMORY_PROXY_CLIENT_KEY=${clientKey}`,
    '--env', `MEMORY_UPDATE_SESSION_ID=${manifest.session_id}`, '--entrypoint', 'node', image, '/incremental_update_container.mjs',
  ]);
  containerId = created.stdout.trim();
  if (!/^[a-f0-9]{64}$/.test(containerId)) throw new Error('Unexpected Docker container id');
  await dockerExec(['cp', containerScript, `${containerId}:/incremental_update_container.mjs`]);
  await dockerExec(['cp', approval.bundle.path, `${containerId}:/incremental_bundle.md`]);
  await dockerExec(['cp', approval.core.path, `${containerId}:/core_candidate.md`]);
  let runResult;
  try { runResult = await dockerExec(['start', '--attach', containerId]); }
  catch (error) { runResult = { stdout: error.stdout || '', stderr: error.stderr || '' }; }
  nativeResult = parseLastJson(runResult.stdout);
  if (nativeResult.status !== 'passed') throw new Error(`Native incremental update failed: ${JSON.stringify(nativeResult)} ${runResult.stderr.slice(-2000)}`);
  await dockerExec(['rm', '-f', containerId]);
  containerId = undefined;
  await stopProxy();

  const probeCreated = await dockerExec([
    'create', '--pull=never', '--network', 'none', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
    '--tmpfs', '/tmp:rw,size=16m', '--mount', `type=volume,source=${fixed.volume},target=/data`,
    '--env', 'FORMAL_MEMORY_OUTPUT=full', '--entrypoint', 'node', image, '/formal_persistence_probe.mjs',
  ]);
  containerId = probeCreated.stdout.trim();
  await dockerExec(['cp', probeScript, `${containerId}:/formal_persistence_probe.mjs`]);
  let probeRun;
  try { probeRun = await dockerExec(['start', '--attach', containerId]); }
  catch (error) { probeRun = { stdout: error.stdout || '', stderr: error.stderr || '' }; }
  persistenceResult = parseLastJson(probeRun.stdout);
  if (persistenceResult.status !== 'passed' || persistenceResult.memory?.l3?.content?.trim() !== approval.core.content.trim()) {
    throw new Error(`Network-disabled readback or exact L3 check failed: ${JSON.stringify(persistenceResult)}`);
  }
} catch (error) {
  executionError = error;
} finally {
  await stopProxy();
  if (containerId) await dockerExec(['rm', '-f', containerId]).catch(() => {});
}

const ledgerAfter = JSON.parse(await readFile(ledgerPath, 'utf8'));
const newAttempts = ledgerAfter.attempts.slice(ledgerBefore.claimed_attempts);
const promptTokens = newAttempts.reduce((sum, item) => sum + (Number(item.usage?.prompt_tokens) || 0), 0);
const completionTokens = newAttempts.reduce((sum, item) => sum + (Number(item.usage?.completion_tokens) || 0), 0);
const receipt = {
  ...plan, status: executionError ? 'failed' : 'passed', mode: 'execute', created_at: new Date().toISOString(),
  keychain_access_performed: keychainAccessPerformed,
  docker_access_performed: dockerAccessPerformed,
  paid_api_attempted: newAttempts.length > 0,
  network_or_api_access_performed: newAttempts.length > 0,
  native_result: nativeResult ?? null,
  restart_persistence_probe: persistenceResult ?? null,
  budget: {
    prior_alias_claimed_attempts: ledgerBefore.claimed_attempts, new_claimed_attempts: newAttempts.length,
    alias_claimed_attempts: ledgerAfter.claimed_attempts,
    combined_claimed_attempts: fixed.legacy_attempts + ledgerAfter.claimed_attempts,
    combined_remaining_attempts: fixed.combined_historical_attempt_ceiling - fixed.legacy_attempts - ledgerAfter.claimed_attempts,
    prompt_tokens: promptTokens, completion_tokens: completionTokens, total_tokens: promptTokens + completionTokens,
    estimated_usd_at_approved_rates: Number((promptTokens * manifest.input_rate_usd_per_million / 1_000_000
      + completionTokens * manifest.output_rate_usd_per_million / 1_000_000).toFixed(8)),
    ledger_path: path.relative(root, ledgerPath),
  },
  error: executionError instanceof Error ? executionError.message : executionError ? String(executionError) : null,
};
await mkdir(resultDir, { recursive: true });
await writeFile(receiptPath, `${JSON.stringify(receipt, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ ...receipt, receipt_path: path.relative(root, receiptPath) }));
if (executionError) process.exitCode = 1;
