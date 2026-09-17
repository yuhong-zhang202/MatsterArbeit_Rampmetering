import { randomBytes } from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import path from 'node:path';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const root = path.resolve(new URL('../..', import.meta.url).pathname);
const docker = '/opt/homebrew/bin/docker';
const context = 'colima-memory-pilot';
const image = 'sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11';
const volume = 'tdai-ramp-metering-memory-v1';
const probe = path.join(root, 'scripts/memory/formal_persistence_probe.mjs');
const mode = process.argv[2];
if (process.argv.length > 3 || (mode && mode !== '--full')) {
  throw new Error('Usage: node scripts/memory/read_formal_memory.mjs [--full]');
}
const name = `tdai-ramp-memory-read-${randomBytes(5).toString('hex')}`;
async function run(args, options = {}) {
  return execFile(docker, ['--context', context, ...args], { maxBuffer: 20 * 1024 * 1024, timeout: 180000, ...options });
}
let created = false;
try {
  await run(['volume', 'inspect', volume]);
  const args = [
    'create', '--name', name, '--pull=never', '--network', 'none', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,size=16m',
    '--mount', `type=volume,source=${volume},target=/data`,
  ];
  if (mode === '--full') args.push('--env', 'FORMAL_MEMORY_OUTPUT=full');
  args.push('--entrypoint', 'node', image, '/formal_persistence_probe.mjs');
  await run(args);
  created = true;
  await run(['cp', probe, `${name}:/formal_persistence_probe.mjs`]);
  const result = await run(['start', '--attach', name]);
  const last = result.stdout.trim().split('\n').filter(Boolean).at(-1) || '{}';
  const parsed = JSON.parse(last);
  if (parsed.status !== 'passed') throw new Error(`Formal memory read failed: ${last}`);
  console.log(JSON.stringify({ project: 'Masterarbeit-Ramp-Metering', volume, network: 'none', ...parsed }));
} finally {
  if (created) await run(['rm', '-f', name]).catch(() => {});
}
