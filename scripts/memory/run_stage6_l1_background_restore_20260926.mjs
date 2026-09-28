import { randomBytes } from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const root = path.resolve(new URL('../..', import.meta.url).pathname);
const dir = path.join(root, 'docs/memory/stage6_content_correction_20260926_v1');
const spec = path.join(dir, 'CORRECTION_SPEC.json');
const containerScript = path.join(root, 'scripts/memory/stage6_l1_background_restore_container_20260926.mjs');
const receipt = path.join(dir, 'L1_BACKGROUND_RESTORE_RECEIPT.json');
const docker = '/opt/homebrew/bin/docker';
const context = 'colima-memory-pilot';
const image = 'sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const volume = 'tdai-ramp-metering-memory-v1';
const name = `tdai-ramp-background-restore-${randomBytes(5).toString('hex')}`;
async function run(args) {
  return execFile(docker, ['--context', context, ...args], { maxBuffer: 5 * 1024 * 1024, timeout: 180000 });
}
try { await readFile(receipt); throw new Error('Restore receipt exists; refusing replay'); }
catch (error) { if (error.code !== 'ENOENT') throw error; }
let created = false;
let result;
let error;
try {
  await run(['volume', 'inspect', volume]);
  await run(['create', '--name', name, '--pull=never', '--network', 'none', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,size=16m',
    '--mount', `type=volume,source=${volume},target=/data`, '--entrypoint', 'node', image, '/stage6_l1_background_restore_container.mjs']);
  created = true;
  await run(['cp', containerScript, `${name}:/stage6_l1_background_restore_container.mjs`]);
  await run(['cp', spec, `${name}:/correction_spec.json`]);
  let executed;
  try { executed = await run(['start', '--attach', name]); }
  catch (cause) { executed = { stdout: cause.stdout ?? '', stderr: cause.stderr ?? '' }; }
  const last = executed.stdout.trim().split('\n').filter(Boolean).at(-1);
  if (!last) throw new Error(`No container JSON: ${executed.stderr.slice(-1500)}`);
  result = JSON.parse(last);
  if (result.status !== 'passed') throw new Error(result.error ?? 'Restore container failed');
} catch (cause) { error = cause instanceof Error ? cause.message : String(cause); }
finally { if (created) await run(['rm', '-f', name]).catch(() => {}); }
const record = { status: error ? 'failed' : 'passed', created_at: new Date().toISOString(), network: 'none', model_calls: 0, result: result ?? null, error: error ?? null };
await writeFile(receipt, `${JSON.stringify(record, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ status: record.status, receipt_path: path.relative(root, receipt), result, error }));
if (error) process.exitCode = 1;
