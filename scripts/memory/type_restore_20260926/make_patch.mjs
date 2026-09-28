import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';

const base = new URL('./v2-router.original.ts', import.meta.url);
const output = new URL('./v2-router.type-restore.ts', import.meta.url);
const source = await readFile(base, 'utf8');
const sha = value => createHash('sha256').update(value).digest('hex');

const oldBlock = `  // Read existing record by primary key
  const existing = await store.queryL1Records({ recordIds: [id] });
  if (!existing || existing.length === 0) {
    return errorEnvelope(404, \`Atomic note not found: \${id}\`, requestId);
  }

  const now = new Date().toISOString();
  const record = existing[0];`;

const newBlock = `  // One-use, network-isolated type restoration. The installed SQLite store's
  // queryL1Records ignores recordIds, so the upstream handler used row zero.
  // Resolve by exact ID and fail closed on the complete expected state.
  if (process.env.TDAI_TYPE_RESTORE_MODE !== "stage6-l1-type-restore-20260926-v1") {
    return errorEnvelope(403, "Type-restore mode is disabled", requestId);
  }
  const digest = (value: string) => createHash("sha256").update(value).digest("hex");
  const request = body as Record<string, unknown>;
  const expectedKeys = ["team_id", "agent_id", "user_id", "id", "content", "background", "restore_type", "expected_type", "expected_version"];
  if (!request || typeof request !== "object" || Array.isArray(request) ||
      Object.keys(request).sort().join("|") !== expectedKeys.sort().join("|") ||
      request.team_id !== "team-masterarbeit-ramp-metering" ||
      request.agent_id !== "agent-project-memory" ||
      request.user_id !== "user-yuhong-zhang" ||
      id !== "m_1790425813551_503da35b" ||
      request.restore_type !== "episodic" ||
      request.expected_type !== "persona" ||
      request.expected_version !== 1 ||
      digest(content) !== "126ef8b51f4d949a67f0c417e7de5e912631abe0c78a0987c113cc4a2e6aa67f" ||
      background !== "我在和用户做增量项目记忆阶段6审查和更新") {
    return errorEnvelope(400, "Type-restore request contract mismatch", requestId);
  }
  const existing = await store.queryL1Records();
  const matching = existing.filter((row) => row.record_id === id);
  if (matching.length !== 1) {
    return errorEnvelope(409, "Target ID is missing or ambiguous", requestId);
  }
  const record = matching[0];
  if (record.type !== "persona" || record.version !== 1 ||
      digest(record.content) !== "126ef8b51f4d949a67f0c417e7de5e912631abe0c78a0987c113cc4a2e6aa67f" ||
      record.scene_name !== background ||
      record.team_id !== request.team_id ||
      record.agent_id !== request.agent_id ||
      record.user_id !== request.user_id) {
    return errorEnvelope(409, "Target record changed; refusing type restore", requestId);
  }
  const now = new Date().toISOString();`;

if (!source.includes(oldBlock) || source.split(oldBlock).length !== 2) {
  throw new Error('Pinned upstream handler does not match the reviewed source');
}
const first = source.replace(oldBlock, newBlock);
const oldType = '    type: record.type as any,';
if (!first.includes(oldType) || first.split(oldType).length !== 2) {
  throw new Error('Pinned upstream type assignment does not match');
}
const patched = first.replace(oldType, '    type: "episodic",');
await writeFile(output, patched, { flag: 'wx' });
console.log(JSON.stringify({ original_sha256: sha(source), patched_sha256: sha(patched), output: output.pathname }));
