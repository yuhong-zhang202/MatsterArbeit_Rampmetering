import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { validateIncrementalApproval } from './incremental_update_policy.mjs';

const digest = value => createHash('sha256').update(value).digest('hex');
const temp = await mkdtemp(path.join(os.tmpdir(), 'ramp-memory-policy-test-'));
const memoryDir = path.join(temp, 'docs/memory');
const bundle = '# Delta\n\nProject identity: `Masterarbeit-Ramp-Metering`\n\nObserved test-only change.';
const core = '# Masterarbeit-Ramp-Metering\n\nReviewed test-only core candidate.';
const manifestPath = path.join(memoryDir, 'approval.json');

async function writeManifest(patch = {}) {
  const manifest = {
    schema_version: 1,
    status: 'user-approved',
    project: 'Masterarbeit-Ramp-Metering',
    update_id: 'stage2-test-20260909-v1',
    session_id: 'stage2-test-20260909-v1',
    approved_at: '2026-09-09T17:00:00+02:00',
    approval_quote: '授权执行这一份测试增量。',
    model: 'gpt-4.1-mini',
    max_new_attempts: 3,
    max_request_bytes: 20000,
    max_output_tokens: 4096,
    input_rate_usd_per_million: 0.4,
    output_rate_usd_per_million: 1.6,
    approved_cost_ceiling_usd: 0.0436608,
    delta_bundle: { path: 'docs/memory/delta.md', sha256: digest(bundle) },
    l3_candidate: { path: 'docs/memory/core.md', sha256: digest(core) },
    ...patch,
  };
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
}

async function rejects(patch, pattern) {
  await writeManifest(patch);
  try {
    await validateIncrementalApproval({ root: temp, manifestPath });
  } catch (error) {
    if (pattern.test(error.message)) return;
    throw new Error(`Expected ${pattern}, received: ${error.message}`);
  }
  throw new Error(`Validation unexpectedly accepted ${JSON.stringify(patch)}`);
}

try {
  await mkdir(memoryDir, { recursive: true });
  await writeFile(path.join(memoryDir, 'delta.md'), bundle);
  await writeFile(path.join(memoryDir, 'core.md'), core);
  await writeManifest();
  const accepted = await validateIncrementalApproval({ root: temp, manifestPath });
  if (accepted.bundle.bytes !== Buffer.byteLength(bundle) || accepted.core.sha256 !== digest(core)) {
    throw new Error('Accepted approval did not preserve verified file metadata');
  }
  await rejects({ status: 'template-not-approved' }, /status must be exactly/);
  await writeManifest({ status: 'dry-run-authorized' });
  await validateIncrementalApproval({ root: temp, manifestPath, dryRun: true });
  try {
    await validateIncrementalApproval({ root: temp, manifestPath });
    throw new Error('Execute validation unexpectedly accepted a dry-run-only manifest');
  } catch (error) {
    if (!/status must be exactly/.test(error.message)) throw error;
  }
  await rejects({ update_id: 'bad id', session_id: 'bad id' }, /update_id must match/);
  await rejects({ max_new_attempts: 36 }, /max_new_attempts/);
  await rejects({ approved_cost_ceiling_usd: 0.001 }, /conservative per-run bound/);
  await rejects({ delta_bundle: { path: 'docs/memory/delta.md', sha256: '0'.repeat(64) } }, /SHA-256/);

  const secretBundle = `${bundle}\n\nsk-exampleCredentialThatMustBeRejected123456789`;
  await writeFile(path.join(memoryDir, 'delta.md'), secretBundle);
  await rejects({ delta_bundle: { path: 'docs/memory/delta.md', sha256: digest(secretBundle) } }, /credential/);
  await writeFile(path.join(memoryDir, 'delta.md'), bundle);

  const outside = path.join(temp, 'outside.md');
  await writeFile(outside, bundle);
  await rejects({ delta_bundle: { path: 'docs/memory/../outside.md', sha256: digest(bundle) } }, /under docs\/memory|outside/);
  console.log(JSON.stringify({ status: 'passed', valid_manifest_accepted: true, dry_run_only_status_guarded: true, rejected_cases: 7 }));
} finally {
  await rm(temp, { recursive: true, force: true });
}
