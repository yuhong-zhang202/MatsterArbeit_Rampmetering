import { createHash, randomBytes } from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const phase = process.argv[2];
if (!['test', 'production'].includes(phase)) throw new Error('Pass exactly test or production');
const root = path.resolve(new URL('../../..', import.meta.url).pathname);
const dir = path.join(root, 'docs/memory/stage6_l1_type_restore_20260926_v1');
const scriptDir = path.join(root, 'scripts/memory/type_restore_20260926');
const receiptPath = path.join(dir, phase === 'test' ? 'ISOLATED_TEST_RECEIPT.json' : 'PRODUCTION_RESTORE_RECEIPT.json');
const testReceiptPath = path.join(dir, 'ISOLATED_TEST_RECEIPT.json');
const specPath = path.join(root, 'docs/memory/stage6_content_correction_20260926_v1/CORRECTION_SPEC.json');
const baselinePath = path.join(root, 'docs/memory/stage6_content_correction_20260926_v1/FINAL_VERIFICATION_RECEIPT.json');
const sourcePath = path.join(scriptDir, 'v2-router.original.ts');
const patchedPath = path.join(scriptDir, 'v2-router.type-restore.ts');
const scriptPath = path.join(scriptDir, 'restore_container.mjs');
const image = 'sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const volume = phase === 'test' ? 'tdai-ramp-memory-type-restore-test-20260926-v1' : 'tdai-ramp-metering-memory-v1';
const sha = value => createHash('sha256').update(value).digest('hex');
const run = args => execFile('/opt/homebrew/bin/docker', ['--context', 'colima-memory-pilot', ...args],
  { maxBuffer: 12 * 1024 * 1024, timeout: 180000 });

async function mustNotExist(file) {
  try { await readFile(file); } catch (error) { if (error.code === 'ENOENT') return; throw error; }
  throw new Error(`Receipt exists; refusing replay: ${file}`);
}
await mustNotExist(receiptPath);
const [source, patched, specRaw, baselineRaw] = await Promise.all([
  readFile(sourcePath), readFile(patchedPath), readFile(specPath), readFile(baselinePath),
]);
if (sha(source) !== '6ed07380b9a1559c2184c05942aadeba4d906cf665cfdf61b794d2fcf878e36c'
  || sha(patched) !== 'ace9b8d1c87aace56ad0be506ddbad6cab0db066477fdfaa04795f195f0366b0') {
  throw new Error('Reviewed source or one-use patch hash mismatch');
}
const spec = JSON.parse(specRaw);
const baseline = JSON.parse(baselineRaw);
if (spec.atomic.id !== 'm_1790425813551_503da35b' ||
  spec.atomic.new_content_sha256 !== '126ef8b51f4d949a67f0c417e7de5e912631abe0c78a0987c113cc4a2e6aa67f' ||
  baseline.status !== 'CONTENT_ACCEPTANCE_FAILED' || baseline.targets.l1.current_type !== 'persona') {
  throw new Error('Correction target or baseline mismatch');
}
if (phase === 'production') {
  const tested = JSON.parse(await readFile(testReceiptPath, 'utf8'));
  if (tested.status !== 'passed' || tested.result?.status !== 'passed' ||
    tested.result.after?.target?.type !== 'episodic' ||
    tested.result.unrelated_l1_unchanged !== true || tested.result.l0_l2_l3_unchanged !== true) {
    throw new Error('Isolated test did not establish a safe restoration');
  }
}

const name = `tdai-type-restore-${phase}-${randomBytes(5).toString('hex')}`;
let created = false;
let result;
let error;
try {
  await run(['volume', 'inspect', volume]);
  await run(['image', 'inspect', image]);
  await run(['create', '--name', name, '--pull=never', '--network', 'none', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,size=32m',
    '--mount', `type=volume,source=${volume},target=/data`,
    '--env', 'TDAI_TYPE_RESTORE_MODE=stage6-l1-type-restore-20260926-v1',
    '--entrypoint', 'node', image, '/type_restore_container.mjs']);
  created = true;
  await run(['cp', patchedPath, `${name}:/app/src/gateway/v2-router.ts`]);
  await run(['cp', scriptPath, `${name}:/type_restore_container.mjs`]);
  await run(['cp', specPath, `${name}:/correction_spec.json`]);
  await run(['cp', baselinePath, `${name}:/baseline_receipt.json`]);
  let executed;
  try { executed = await run(['start', '--attach', name]); }
  catch (cause) { executed = { stdout: cause.stdout ?? '', stderr: cause.stderr ?? '' }; }
  const last = executed.stdout.trim().split('\n').filter(Boolean).at(-1);
  if (!last) throw new Error(`No container JSON: ${executed.stderr.slice(-1500)}`);
  result = JSON.parse(last);
  if (result.status !== 'passed') throw new Error(result.error ?? 'Restoration container failed');
} catch (cause) {
  error = cause instanceof Error ? cause.message : String(cause);
} finally {
  if (created) await run(['rm', '-f', name]).catch(() => {});
}
const receipt = { status: error ? 'failed' : 'passed', phase, created_at: new Date().toISOString(),
  volume, image, network: 'none', model_calls: 0,
  source_sha256: sha(source), patch_sha256: sha(patched), spec_sha256: sha(specRaw),
  baseline_receipt_sha256: sha(baselineRaw), result: result ?? null, error: error ?? null };
await writeFile(receiptPath, `${JSON.stringify(receipt, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ status: receipt.status, phase, receipt_path: path.relative(root, receiptPath),
  before: result?.before?.target, after: result?.after?.target, error }));
if (error) process.exitCode = 1;
