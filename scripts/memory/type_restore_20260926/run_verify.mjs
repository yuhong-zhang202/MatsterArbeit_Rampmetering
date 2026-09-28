import { createHash, randomBytes } from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const snapshotMode = process.argv[2] === '--snapshot-after-readonly-failure' && process.argv.length === 3;
if (process.argv.length > 2 && !snapshotMode) throw new Error('Unknown verification mode');
const root = path.resolve(new URL('../../..', import.meta.url).pathname);
const dir = path.join(root, 'docs/memory/stage6_l1_type_restore_20260926_v1');
const specPath = path.join(root, 'docs/memory/stage6_content_correction_20260926_v1/CORRECTION_SPEC.json');
const writeReceiptPath = path.join(dir, 'PRODUCTION_RESTORE_RECEIPT.json');
const readReceiptPath = path.join(dir, snapshotMode ? 'FRESH_UNPATCHED_SNAPSHOT_READ_RECEIPT.json' : 'FRESH_UNPATCHED_READ_RECEIPT.json');
const probePath = path.join(root, 'scripts/memory/type_restore_20260926/verify_container.mjs');
const image = 'sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const volume = snapshotMode ? 'tdai-ramp-memory-type-restore-postread-20260926-v1' : 'tdai-ramp-metering-memory-v1';
const sha = value => createHash('sha256').update(value).digest('hex');
const run = args => execFile('/opt/homebrew/bin/docker', ['--context', 'colima-memory-pilot', ...args],
  { maxBuffer: 12 * 1024 * 1024, timeout: 180000 });
try { await readFile(readReceiptPath); throw new Error('Readback receipt exists; refusing overwrite'); }
catch (error) { if (error.code !== 'ENOENT') throw error; }
const writeReceipt = await readFile(writeReceiptPath);
if (JSON.parse(writeReceipt).status !== 'passed') throw new Error('Production restore did not pass');
if (snapshotMode) {
  const failedReadonly = JSON.parse(await readFile(path.join(dir, 'FRESH_UNPATCHED_READ_RECEIPT.json'), 'utf8'));
  if (failedReadonly.status !== 'failed' || !failedReadonly.error?.includes('conversation/query: 500 500')) {
    throw new Error('Snapshot fallback requires the recorded read-only SQLite failure');
  }
}
const name = `tdai-type-restore-verify-${randomBytes(5).toString('hex')}`;
let created = false;
let result;
let error;
try {
  await run(['create', '--name', name, '--pull=never', '--network', 'none', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,size=32m',
    '--mount', `type=volume,source=${volume},target=/data${snapshotMode ? '' : ',readonly'}`,
    '--entrypoint', 'node', image, '/type_restore_verify_container.mjs']);
  created = true;
  await run(['cp', probePath, `${name}:/type_restore_verify_container.mjs`]);
  await run(['cp', specPath, `${name}:/correction_spec.json`]);
  await run(['cp', writeReceiptPath, `${name}:/restore_receipt.json`]);
  let executed;
  try { executed = await run(['start', '--attach', name]); }
  catch (cause) { executed = { stdout: cause.stdout ?? '', stderr: cause.stderr ?? '' }; }
  const last = executed.stdout.trim().split('\n').filter(Boolean).at(-1);
  if (!last) throw new Error(`No verification JSON: ${executed.stderr.slice(-1500)}`);
  result = JSON.parse(last);
  if (result.status !== 'passed') throw new Error(result.error ?? 'Fresh verification failed');
} catch (cause) { error = cause instanceof Error ? cause.message : String(cause); }
finally { if (created) await run(['rm', '-f', name]).catch(() => {}); }
const receipt = { status: error ? 'failed' : 'passed', created_at: new Date().toISOString(),
  image, volume, network: 'none', mount: snapshotMode ? 'isolated-snapshot-readwrite-for-sqlite' : 'readonly', model_calls: 0,
  production_receipt_sha256: sha(writeReceipt), result: result ?? null, error: error ?? null };
await writeFile(readReceiptPath, `${JSON.stringify(receipt, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ status: receipt.status, receipt_path: path.relative(root, readReceiptPath),
  target: result?.target, error }));
if (error) process.exitCode = 1;
