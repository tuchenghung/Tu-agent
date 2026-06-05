// Session start warm-up: primes Node module cache before Claude Code initializes MCPs.
// Warms both direct servers AND proxy chains for calendar/gmail.
import { spawn } from 'child_process';

const NODE = 'C:\\Users\\deco01\\nodejs\\node.exe';
const PROXY = 'D:\\Dropbox\\Tu-agent\\000_Agent\\scripts\\mcp-proxy.mjs';

const INIT_MSG = JSON.stringify({
  jsonrpc: '2.0', id: 1, method: 'initialize',
  params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'warmup', version: '1' } }
}) + '\n';

function warmup(args, env = {}) {
  return new Promise((resolve) => {
    const proc = spawn(NODE, args, { env: { ...process.env, ...env } });
    let done = false;
    const finish = () => { if (!done) { done = true; try { proc.kill(); } catch (_) {} resolve(); } };
    proc.stdout.once('data', finish);
    proc.stderr.once('data', finish);
    proc.on('error', finish);
    proc.on('exit', finish);
    setTimeout(finish, 6000);
    proc.stdin.write(INIT_MSG);
    proc.stdin.end();
  });
}

await Promise.all([
  // Direct servers (non-proxy) — warmed as before
  warmup(['C:\\Users\\deco01\\nodejs\\node_modules\\@modelcontextprotocol\\server-filesystem\\dist\\index.js']),
  warmup(['C:\\Users\\deco01\\nodejs\\node_modules\\@playwright\\mcp\\cli.js']),
  warmup(['C:\\Users\\deco01\\nodejs\\node_modules\\firecrawl-mcp\\dist\\index.js']),
  warmup(['C:\\Users\\deco01\\nodejs\\node_modules\\@notionhq\\notion-mcp-server\\bin\\cli.mjs']),

  // Proxy chains — warm the FULL chain (proxy + child) to prime both processes
  warmup([
    PROXY,
    'C:\\Users\\deco01\\nodejs\\node_modules\\@cocal\\google-calendar-mcp\\build\\index.js',
    'GOOGLE_OAUTH_CREDENTIALS=C:\\Users\\deco01\\.google-mcp\\gcp-oauth.keys.json'
  ]),
  warmup([
    PROXY,
    'C:\\Users\\deco01\\nodejs\\node_modules\\@gongrzhe\\server-gmail-autoauth-mcp\\dist\\index.js'
  ]),
]);
