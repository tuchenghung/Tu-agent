// Session start warm-up: primes Node module cache before Claude Code initializes MCPs.
// Runs in parallel so max wait = slowest single MCP (~3-5s cold start).
import { spawn } from 'child_process';

const NODE = 'C:\\Users\\deco01\\nodejs\\node.exe';
const INIT_MSG = JSON.stringify({
  jsonrpc: '2.0', id: 1, method: 'initialize',
  params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'warmup', version: '1' } }
}) + '\n';

function warmup(script, env = {}) {
  return new Promise((resolve) => {
    const proc = spawn(NODE, [script], { env: { ...process.env, ...env } });
    let done = false;
    const finish = () => { if (!done) { done = true; try { proc.kill(); } catch (_) {} resolve(); } };
    proc.stdout.once('data', finish);
    proc.stderr.once('data', finish); // calendar prints to stderr on init
    proc.on('error', finish);
    proc.on('exit', finish);
    setTimeout(finish, 6000);
    proc.stdin.write(INIT_MSG);
    proc.stdin.end();
  });
}

await Promise.all([
  warmup('C:\\Users\\deco01\\nodejs\\node_modules\\@gongrzhe\\server-gmail-autoauth-mcp\\dist\\index.js'),
  warmup('C:\\Users\\deco01\\nodejs\\node_modules\\@cocal\\google-calendar-mcp\\build\\index.js', {
    GOOGLE_OAUTH_CREDENTIALS: 'C:\\Users\\deco01\\.google-mcp\\gcp-oauth.keys.json'
  }),
  warmup('C:\\Users\\deco01\\nodejs\\node_modules\\@modelcontextprotocol\\server-filesystem\\dist\\index.js'),
  warmup('C:\\Users\\deco01\\nodejs\\node_modules\\@playwright\\mcp\\cli.js'),
  warmup('C:\\Users\\deco01\\nodejs\\node_modules\\firecrawl-mcp\\dist\\index.js'),
  warmup('C:\\Users\\deco01\\nodejs\\node_modules\\@notionhq\\notion-mcp-server\\bin\\cli.mjs'),
]);
