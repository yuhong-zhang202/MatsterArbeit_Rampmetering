import { createHash } from 'node:crypto';
import { execFile as execFileCallback } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const root = path.resolve(new URL('../../..', import.meta.url).pathname);
const output = path.join(root, 'docs/memory/stage6_l1_type_restore_20260926_v1/SQLITE_ROW_AUDIT_RECEIPT.json');
try { await readFile(output); throw new Error('Audit receipt exists; refusing overwrite'); }
catch (error) { if (error.code !== 'ENOENT') throw error; }
const script = await readFile(new URL('./audit_sqlite_copies.mjs', import.meta.url));
const { stdout } = await execFile('/opt/homebrew/bin/docker',
  ['--context', 'colima-memory-pilot', 'logs', 'tdai-type-restore-row-audit-20260926'],
  { maxBuffer: 1024 * 1024, timeout: 30000 });
const line = stdout.trim().split('\n').filter(Boolean).at(-1);
if (!line) throw new Error('No audit JSON in container logs');
const result = JSON.parse(line);
if (result.status !== 'passed' || result.source_mounts !== 'readonly' ||
  result.changed_columns.slice().sort().join('|') !== 'type|updated_time|version' ||
  !result.unrelated_rows_unchanged) throw new Error('Audit result did not pass');
const receipt = { status: 'passed', source_container: 'tdai-type-restore-row-audit-20260926',
  audit_script_sha256: createHash('sha256').update(script).digest('hex'), result };
await writeFile(output, `${JSON.stringify(receipt, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ status: 'passed', receipt_path: path.relative(root, output), changed_columns: result.changed_columns }));
