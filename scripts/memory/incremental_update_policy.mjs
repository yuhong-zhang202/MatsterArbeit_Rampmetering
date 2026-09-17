import { createHash } from 'node:crypto';
import { readFile, realpath } from 'node:fs/promises';
import path from 'node:path';

export const FIXED_MEMORY_POLICY = Object.freeze({
  project: 'Masterarbeit-Ramp-Metering',
  model: 'gpt-4.1-mini',
  volume: 'tdai-ramp-metering-memory-v1',
  service_id: 'ramp-metering-formal-memory-v1',
  team_id: 'team-masterarbeit-ramp-metering',
  agent_id: 'agent-project-memory',
  user_id: 'user-yuhong-zhang',
  max_request_bytes: 20000,
  max_output_tokens: 4096,
  combined_historical_attempt_ceiling: 41,
  legacy_attempts: 4,
  alias_attempt_ceiling: 37,
});

const sha256 = value => createHash('sha256').update(value).digest('hex');
const secretPatterns = [
  /\bsk-[A-Za-z0-9_-]{20,}\b/,
  /\b(?:OPENAI|TENCENT|RAMP_MEMORY)[A-Z0-9_]*API[_ -]?KEY\b\s*[:=]\s*\S+/i,
  /\bBearer\s+[A-Za-z0-9._-]{20,}\b/i,
];

function requireExact(value, expected, label) {
  if (value !== expected) throw new Error(`${label} must be exactly ${JSON.stringify(expected)}`);
}

function validateId(value, label) {
  if (typeof value !== 'string' || !/^[a-z0-9][a-z0-9-]{5,79}$/.test(value)) {
    throw new Error(`${label} must match ^[a-z0-9][a-z0-9-]{5,79}$`);
  }
}

async function approvedFile(root, descriptor, label, maxBytes) {
  if (!descriptor || typeof descriptor !== 'object') throw new Error(`${label} descriptor is required`);
  if (typeof descriptor.path !== 'string' || !descriptor.path.startsWith('docs/memory/')) {
    throw new Error(`${label}.path must be under docs/memory/`);
  }
  if (!/^[a-f0-9]{64}$/.test(descriptor.sha256 ?? '')) throw new Error(`${label}.sha256 is invalid`);
  const allowedRoot = await realpath(path.join(root, 'docs/memory'));
  const resolved = await realpath(path.resolve(root, descriptor.path));
  if (resolved !== allowedRoot && !resolved.startsWith(`${allowedRoot}${path.sep}`)) {
    throw new Error(`${label} resolves outside docs/memory/`);
  }
  const content = await readFile(resolved, 'utf8');
  const bytes = Buffer.byteLength(content);
  if (bytes < 1 || bytes > maxBytes) throw new Error(`${label} must contain 1-${maxBytes} UTF-8 bytes`);
  if (sha256(content) !== descriptor.sha256) throw new Error(`${label} SHA-256 does not match approval manifest`);
  for (const pattern of secretPatterns) {
    if (pattern.test(content)) throw new Error(`${label} contains a likely credential and cannot be approved`);
  }
  return { path: resolved, relative_path: descriptor.path, content, bytes, sha256: descriptor.sha256 };
}

export async function validateIncrementalApproval({ root, manifestPath, dryRun = false }) {
  const repositoryRoot = await realpath(root);
  const manifestResolved = await realpath(path.resolve(repositoryRoot, manifestPath));
  const manifestRoot = await realpath(path.join(repositoryRoot, 'docs/memory'));
  if (!manifestResolved.startsWith(`${manifestRoot}${path.sep}`)) {
    throw new Error('Approval manifest must be stored under docs/memory/');
  }
  const manifestRaw = await readFile(manifestResolved, 'utf8');
  if (Buffer.byteLength(manifestRaw) > 20000) throw new Error('Approval manifest exceeds 20,000 bytes');
  const manifest = JSON.parse(manifestRaw);
  requireExact(manifest.schema_version, 1, 'schema_version');
  const allowedStatus = dryRun ? ['dry-run-authorized', 'user-approved'] : ['user-approved'];
  if (!allowedStatus.includes(manifest.status)) {
    throw new Error(`status must be exactly ${dryRun ? '"dry-run-authorized" or "user-approved"' : '"user-approved"'}`);
  }
  requireExact(manifest.project, FIXED_MEMORY_POLICY.project, 'project');
  requireExact(manifest.model, FIXED_MEMORY_POLICY.model, 'model');
  requireExact(manifest.max_request_bytes, FIXED_MEMORY_POLICY.max_request_bytes, 'max_request_bytes');
  requireExact(manifest.max_output_tokens, FIXED_MEMORY_POLICY.max_output_tokens, 'max_output_tokens');
  validateId(manifest.update_id, 'update_id');
  validateId(manifest.session_id, 'session_id');
  if (manifest.update_id !== manifest.session_id) throw new Error('update_id and session_id must be identical');
  if (typeof manifest.approved_at !== 'string' || !Number.isFinite(Date.parse(manifest.approved_at))) {
    throw new Error('approved_at must be an ISO date-time');
  }
  if (typeof manifest.approval_quote !== 'string' || manifest.approval_quote.trim().length < 8) {
    throw new Error('approval_quote must contain the explicit user authorization');
  }
  if (!Number.isSafeInteger(manifest.max_new_attempts) || manifest.max_new_attempts < 1 || manifest.max_new_attempts > 35) {
    throw new Error('max_new_attempts must be an explicitly approved integer in [1, 35]');
  }
  for (const field of ['input_rate_usd_per_million', 'output_rate_usd_per_million', 'approved_cost_ceiling_usd']) {
    if (typeof manifest[field] !== 'number' || !Number.isFinite(manifest[field]) || manifest[field] <= 0) {
      throw new Error(`${field} must be an explicitly approved positive number`);
    }
  }
  const conservativeCostCeiling = manifest.max_new_attempts * (
    FIXED_MEMORY_POLICY.max_request_bytes * manifest.input_rate_usd_per_million
    + FIXED_MEMORY_POLICY.max_output_tokens * manifest.output_rate_usd_per_million
  ) / 1_000_000;
  if (manifest.approved_cost_ceiling_usd + Number.EPSILON < conservativeCostCeiling) {
    throw new Error(`approved_cost_ceiling_usd must cover the conservative per-run bound ${conservativeCostCeiling.toFixed(8)}`);
  }
  const bundle = await approvedFile(repositoryRoot, manifest.delta_bundle, 'delta_bundle', 12000);
  const core = await approvedFile(repositoryRoot, manifest.l3_candidate, 'l3_candidate', 12000);
  if (!bundle.content.includes('Project identity: `Masterarbeit-Ramp-Metering`')) {
    throw new Error('Delta bundle project identity is missing');
  }
  if (!core.content.includes('Masterarbeit-Ramp-Metering')) throw new Error('L3 candidate project identity is missing');
  if (/scene navigation/i.test(core.content)) {
    throw new Error('L3 candidate must not contain a Scene Navigation block because core/write strips it');
  }
  return {
    manifest,
    manifest_path: manifestResolved,
    manifest_sha256: sha256(manifestRaw),
    bundle,
    core,
    fixed_policy: FIXED_MEMORY_POLICY,
    conservative_cost_ceiling_usd: conservativeCostCeiling,
  };
}
