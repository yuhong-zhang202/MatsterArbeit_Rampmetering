import { execFile as execFileCallback } from 'node:child_process';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const keyResult = await execFile('/usr/bin/security', [
  'find-generic-password', '-w',
  '-a', 'ramp-metering-memory',
  '-s', 'openai-api-key-ramp-metering-memory',
], { maxBuffer: 1024 * 1024 });
const key = keyResult.stdout.trim();
if (!key.startsWith('sk-') || key.length < 150 || /\s/.test(key)) {
  throw new Error('Keychain secret metadata is invalid');
}

const model = 'gpt-4.1-mini';
const response = await fetch(`https://api.openai.com/v1/models/${model}`, {
  headers: { authorization: `Bearer ${key}` },
  signal: AbortSignal.timeout(30000),
});
let body;
try { body = await response.json(); } catch { body = { error: { message: 'Non-JSON response' } }; }
const safe = response.ok
  ? { id: body.id ?? null, object: body.object ?? null, owned_by: body.owned_by ?? null }
  : {
      error: {
        message: body?.error?.message ?? null,
        type: body?.error?.type ?? null,
        code: body?.error?.code ?? null,
        param: body?.error?.param ?? null,
      },
    };
console.log(JSON.stringify({ model, status: response.status, ok: response.ok, result: safe }));
if (!response.ok) process.exitCode = 1;
