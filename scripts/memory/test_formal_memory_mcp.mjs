import assert from 'node:assert/strict';
import { createHandler } from './formal_memory_mcp.mjs';

const expected = { project: 'Masterarbeit-Ramp-Metering', status: 'passed', memory: { l3: { content: 'fixture' } } };
const handler = createHandler(async () => expected);

const initialized = await handler({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-06-18' } });
assert.equal(initialized.result.serverInfo.name, 'ramp-metering-formal-memory');

const listed = await handler({ jsonrpc: '2.0', id: 2, method: 'tools/list' });
assert.deepEqual(listed.result.tools.map(tool => tool.name), ['read_project_memory']);
assert.equal(listed.result.tools[0].inputSchema.additionalProperties, false);

const rejected = await handler({ jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'read_project_memory', arguments: { volume: 'other' } } });
assert.equal(rejected.error.code, -32602);

const recalled = await handler({ jsonrpc: '2.0', id: 4, method: 'tools/call', params: { name: 'read_project_memory', arguments: {} } });
assert.equal(recalled.result.isError, false);
assert.deepEqual(JSON.parse(recalled.result.content[0].text), expected);

console.log('[ok] formal memory MCP protocol tests passed');
