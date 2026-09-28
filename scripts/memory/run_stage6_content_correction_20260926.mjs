import { createHash, randomBytes } from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

// One-use official-API correction. Never replays the incremental pipeline.
const execFile = promisify(execFileCallback);
const root = path.resolve(new URL('../..', import.meta.url).pathname);
const packageDir = path.join(root, 'docs/memory/stage6_content_correction_20260926_v1');
const receiptPath = path.join(packageDir, 'EXECUTION_RECEIPT.json');
const specPath = path.join(packageDir, 'CORRECTION_SPEC.json');
const l2Path = path.join(packageDir, 'SCENARIO_BODY_CORRECTED.md');
const l3Path = path.join(packageDir, 'CORE_CORRECTED.md');
const sourceReceiptPath = path.join(root, 'data/processed/memory_incremental_stage6-partial-pairability-20260926-v1/receipt.json');
const containerScript = path.join(root, 'scripts/memory/stage6_content_correction_container_20260926.mjs');
const docker = '/opt/homebrew/bin/docker';
const context = 'colima-memory-pilot';
const image = 'sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const volume = 'tdai-ramp-metering-memory-v1';
const sha = value => createHash('sha256').update(value).digest('hex');

async function run(args) {
  return execFile(docker, ['--context', context, ...args], { maxBuffer: 20 * 1024 * 1024, timeout: 180000 });
}
async function absent(file) {
  try { await readFile(file); } catch (error) { if (error.code === 'ENOENT') return; throw error; }
  throw new Error(`Correction already has a receipt; refusing replay: ${file}`);
}

const [specRaw, l2Body, l3Text, sourceReceipt] = await Promise.all([
  readFile(specPath, 'utf8'), readFile(l2Path, 'utf8'), readFile(l3Path, 'utf8'), readFile(sourceReceiptPath),
]);
const spec = JSON.parse(specRaw);
if (spec.correction_id !== 'stage6-content-correction-20260926-v1'
  || spec.volume !== volume || spec.source_receipt_sha256 !== sha(sourceReceipt)
  || spec.scenario.new_body_sha256 !== sha(l2Body)
  || spec.core.new_content_sha256 !== sha(l3Text)
  || spec.atomic.new_content_sha256 !== sha(spec.atomic.new_content)
  || !spec.no_model_calls) {
  throw new Error('Correction package, source receipt, or model-free guard mismatch');
}
await absent(receiptPath);

const name = `tdai-ramp-content-fix-${randomBytes(5).toString('hex')}`;
let created = false;
let result;
let error;
try {
  await run(['volume', 'inspect', volume]);
  await run(['image', 'inspect', image]);
  await run([
    'create', '--name', name, '--pull=never', '--network', 'none', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,size=32m',
    '--mount', `type=volume,source=${volume},target=/data`,
    '--entrypoint', 'node', image, '/stage6_content_correction_container.mjs',
  ]);
  created = true;
  await run(['cp', containerScript, `${name}:/stage6_content_correction_container.mjs`]);
  await run(['cp', specPath, `${name}:/correction_spec.json`]);
  await run(['cp', l2Path, `${name}:/scenario_body_corrected.md`]);
  await run(['cp', l3Path, `${name}:/core_corrected.md`]);
  let execution;
  try { execution = await run(['start', '--attach', name]); }
  catch (cause) { execution = { stdout: cause.stdout ?? '', stderr: cause.stderr ?? '' }; }
  const last = execution.stdout.trim().split('\n').filter(Boolean).at(-1);
  if (!last) throw new Error(`Correction container produced no JSON: ${execution.stderr.slice(-1500)}`);
  result = JSON.parse(last);
  if (result.status !== 'passed') throw new Error(`Correction container failed: ${result.error ?? 'unknown'}`);
} catch (cause) {
  error = cause instanceof Error ? cause.message : String(cause);
} finally {
  if (created) await run(['rm', '-f', name]).catch(() => {});
}

const receipt = {
  correction_id: spec.correction_id,
  created_at: new Date().toISOString(),
  status: error ? 'failed' : 'passed',
  network: 'none', model_calls: 0,
  source_receipt_sha256: spec.source_receipt_sha256,
  correction_spec_sha256: sha(specRaw),
  candidate_hashes: { l1: spec.atomic.new_content_sha256, l2_body: spec.scenario.new_body_sha256, l3: spec.core.new_content_sha256 },
  result: result ?? null,
  error: error ?? null,
};
await writeFile(receiptPath, `${JSON.stringify(receipt, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ status: receipt.status, receipt_path: path.relative(root, receiptPath), result: result ?? null, error: error ?? null }));
if (error) process.exitCode = 1;
