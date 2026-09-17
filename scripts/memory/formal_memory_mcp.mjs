import { execFile as execFileCallback } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { promisify } from 'node:util';

const execFile = promisify(execFileCallback);
const root = '/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering';
const reader = `${root}/scripts/memory/read_formal_memory.mjs`;
const limit = 64 * 1024;
const notice = '读取项目隔离的腾讯 MemoryCore L1/L2/L3。它是辅助背景；当前仓库文档和原始证据始终更权威。';

function isObject(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export async function readProjectMemory() {
  const { stdout } = await execFile('/usr/local/bin/node', [reader, '--full'], {
    cwd: root,
    timeout: 180000,
    maxBuffer: 1024 * 1024,
    encoding: 'utf8',
    env: {
      PATH: '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
      HOME: '/Users/yuhongzhang',
      LC_ALL: 'C',
    },
  });
  const last = stdout.trim().split('\n').filter(Boolean).at(-1);
  if (!last) throw new Error('正式项目记忆读取器没有返回结果。');
  const value = JSON.parse(last);
  if (value.status !== 'passed' || value.project !== 'Masterarbeit-Ramp-Metering') {
    throw new Error('正式项目记忆身份或完整性检查失败。');
  }
  value.notice = `${notice} 若记忆与项目文档冲突，以项目文档为准。`;
  return value;
}

export function createHandler(memoryReader = readProjectMemory) {
  let busy = false;
  return async request => {
    const id = isObject(request) && (typeof request.id === 'string' || typeof request.id === 'number')
      ? request.id : null;
    const error = (code, message) => ({ jsonrpc: '2.0', id, error: { code, message } });
    const result = value => ({ jsonrpc: '2.0', id, result: value });
    if (!isObject(request) || request.jsonrpc !== '2.0' || typeof request.method !== 'string') {
      return error(-32600, '请求格式无效。');
    }
    if (!Object.hasOwn(request, 'id')) return null;
    if (id === null) return error(-32600, '请求 ID 无效。');
    if (request.method === 'initialize') {
      const requested = isObject(request.params) ? request.params.protocolVersion : undefined;
      const protocolVersion = ['2024-11-05', '2025-03-26', '2025-06-18'].includes(String(requested))
        ? requested : '2025-06-18';
      return result({
        protocolVersion,
        capabilities: { tools: {} },
        serverInfo: { name: 'ramp-metering-formal-memory', version: '1.0.0' },
        instructions: notice,
      });
    }
    if (request.method === 'ping') return result({});
    if (request.method === 'tools/list') {
      return result({ tools: [{
        name: 'read_project_memory',
        description: notice,
        inputSchema: { type: 'object', properties: {}, additionalProperties: false },
        annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
      }] });
    }
    if (request.method !== 'tools/call') return error(-32601, '不支持此方法。');
    const params = request.params;
    if (!isObject(params) || params.name !== 'read_project_memory'
      || Object.keys(params).some(key => !['name', 'arguments', '_meta'].includes(key))
      || (params.arguments !== undefined && (!isObject(params.arguments) || Object.keys(params.arguments).length))) {
      return error(-32602, '唯一工具 read_project_memory 不接受参数。');
    }
    if (busy) return error(-32000, '已有项目记忆读取正在执行。');
    busy = true;
    try {
      const memory = await memoryReader();
      const text = JSON.stringify(memory);
      if (Buffer.byteLength(text) > limit) throw new Error('项目记忆响应超过 64 KiB；拒绝静默截断。');
      return result({ content: [{ type: 'text', text }], isError: false });
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : '项目记忆读取失败。';
      return result({ content: [{ type: 'text', text: message }], isError: true });
    } finally {
      busy = false;
    }
  };
}

export function serve(input = process.stdin, output = process.stdout, handler = createHandler()) {
  let pending = '';
  input.setEncoding('utf8');
  input.on('data', chunk => {
    pending += chunk;
    if (Buffer.byteLength(pending) > limit) {
      output.write(`${JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32600, message: '请求超过 64 KiB。' } })}\n`);
      pending = '';
      return;
    }
    let newline;
    while ((newline = pending.indexOf('\n')) >= 0) {
      const line = pending.slice(0, newline);
      pending = pending.slice(newline + 1);
      if (!line.trim()) continue;
      try {
        const request = JSON.parse(line);
        void handler(request).then(response => {
          if (response) output.write(`${JSON.stringify(response)}\n`);
        });
      } catch {
        output.write(`${JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'JSON 解析失败。' } })}\n`);
      }
    }
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) serve();
