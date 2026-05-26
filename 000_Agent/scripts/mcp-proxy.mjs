#!/usr/bin/env node
/**
 * MCP stdio proxy for Windows compatibility.
 * Spawns the target MCP server and proxies stdin/stdout.
 * Ensures stdin starts in flowing mode immediately so no data
 * is lost before the target server sets up its listener.
 *
 * Usage: node mcp-proxy.mjs <server-script> [env KEY=VALUE ...]
 */
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const NODE = process.execPath;
const [serverScript, ...envArgs] = process.argv.slice(2);

if (!serverScript) {
  process.stderr.write('Usage: mcp-proxy.mjs <server-script>\n');
  process.exit(1);
}

// Parse extra env vars passed as KEY=VALUE args
const extraEnv = {};
for (const arg of envArgs) {
  const idx = arg.indexOf('=');
  if (idx > 0) {
    extraEnv[arg.slice(0, idx)] = arg.slice(idx + 1);
  }
}

// Immediately buffer stdin so no data is lost during child startup
const stdinBuffer = [];
let childReady = false;
let childStdin = null;

process.stdin.on('data', (chunk) => {
  if (childReady && childStdin) {
    childStdin.write(chunk);
  } else {
    stdinBuffer.push(chunk);
  }
});
process.stdin.on('end', () => {
  if (childStdin) childStdin.end();
});

const child = spawn(NODE, [serverScript], {
  stdio: ['pipe', 'pipe', 'inherit'],
  windowsHide: true,
  env: { ...process.env, ...extraEnv },
});

childStdin = child.stdin;
child.stdout.pipe(process.stdout);

// Flush buffered stdin to child
childReady = true;
for (const chunk of stdinBuffer) {
  child.stdin.write(chunk);
}

child.on('error', (err) => {
  process.stderr.write(`[mcp-proxy] Error: ${err.message}\n`);
  process.exit(1);
});

child.on('exit', (code) => process.exit(code ?? 0));
process.on('SIGTERM', () => child.kill('SIGTERM'));
process.on('SIGINT', () => child.kill('SIGINT'));
