import { createHash } from 'node:crypto';
import { copyFile } from 'node:fs/promises';
import { DatabaseSync } from 'node:sqlite';

const beforeSource = '/before/tdai-memory/instances/ramp-metering-formal-memory-v1/vectors.db';
const afterSource = '/after/tdai-memory/instances/ramp-metering-formal-memory-v1/vectors.db';
const beforeCopy = '/tmp/type-restore-before.db';
const afterCopy = '/tmp/type-restore-after.db';
const targetId = 'm_1790425813551_503da35b';
const sha = value => createHash('sha256').update(value).digest('hex');
let beforeDb;
let afterDb;
try {
  await copyFile(beforeSource, beforeCopy);
  await copyFile(afterSource, afterCopy);
  beforeDb = new DatabaseSync(beforeCopy, { readOnly: true });
  afterDb = new DatabaseSync(afterCopy, { readOnly: true });
  const beforeRows = beforeDb.prepare('SELECT * FROM l1_records ORDER BY record_id').all();
  const afterRows = afterDb.prepare('SELECT * FROM l1_records ORDER BY record_id').all();
  if (beforeRows.length !== 13 || afterRows.length !== 13) throw new Error('L1 table count mismatch');
  const oldTarget = beforeRows.find(row => row.record_id === targetId);
  const newTarget = afterRows.find(row => row.record_id === targetId);
  if (!oldTarget || !newTarget) throw new Error('Target row missing');
  const oldOthers = beforeRows.filter(row => row.record_id !== targetId);
  const newOthers = afterRows.filter(row => row.record_id !== targetId);
  if (JSON.stringify(oldOthers) !== JSON.stringify(newOthers)) throw new Error('Unrelated L1 database rows changed');
  const changedColumns = Object.keys(oldTarget).filter(key => JSON.stringify(oldTarget[key]) !== JSON.stringify(newTarget[key]));
  const expected = ['type', 'version', 'updated_time'];
  if (changedColumns.slice().sort().join('|') !== expected.sort().join('|')) {
    throw new Error(`Unexpected target columns changed: ${changedColumns.join(',')}`);
  }
  if (oldTarget.type !== 'persona' || newTarget.type !== 'episodic' ||
      oldTarget.version !== 1 || newTarget.version !== 2 ||
      oldTarget.content !== newTarget.content ||
      sha(newTarget.content) !== '126ef8b51f4d949a67f0c417e7de5e912631abe0c78a0987c113cc4a2e6aa67f') {
    throw new Error('Target row semantics mismatch');
  }
  console.log(JSON.stringify({ status: 'passed', source_mounts: 'readonly', database_copies: 'tmpfs',
    rows_before: beforeRows.length, rows_after: afterRows.length,
    target_id: targetId, changed_columns: changedColumns,
    type_before: oldTarget.type, type_after: newTarget.type,
    version_before: oldTarget.version, version_after: newTarget.version,
    content_sha256: sha(newTarget.content), unrelated_rows_unchanged: true,
    before_db_sha256: sha(await (await import('node:fs/promises')).readFile(beforeCopy)),
    after_db_sha256: sha(await (await import('node:fs/promises')).readFile(afterCopy)) }));
} catch (error) {
  console.log(JSON.stringify({ status: 'failed', error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
} finally {
  beforeDb?.close();
  afterDb?.close();
}
