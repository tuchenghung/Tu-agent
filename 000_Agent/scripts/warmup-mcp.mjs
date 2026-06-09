// Session start warm-up: primes Node module cache before Claude Code initializes MCPs.
// Warms both direct servers AND proxy chains for calendar/gmail.
// Also pre-refreshes Google Calendar OAuth token if expired or expiring soon,
// so the calendar MCP does not need to do a network round-trip during initialization.
import { spawn } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import { request } from 'https';

const NODE = 'C:\\Users\\deco01\\nodejs\\node.exe';
const PROXY = 'D:\\Dropbox\\Tu-agent\\000_Agent\\scripts\\mcp-proxy.mjs';
const TOKENS_FILE = 'C:\\Users\\deco01\\.config\\google-calendar-mcp\\tokens.json';
const CREDENTIALS_FILE = 'C:\\Users\\deco01\\.google-mcp\\gcp-oauth.keys.json';
// Refresh if token expires within 10 minutes
const REFRESH_THRESHOLD_MS = 10 * 60 * 1000;

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

function httpsPost(hostname, path, data) {
  return new Promise((resolve, reject) => {
    const body = new URLSearchParams(data).toString();
    const req = request({
      hostname, path, method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) }
    }, (res) => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => {
        try { resolve(JSON.parse(raw)); } catch { reject(new Error('Bad JSON: ' + raw)); }
      });
    });
    req.on('error', reject);
    req.setTimeout(8000, () => { req.destroy(); reject(new Error('timeout')); });
    req.write(body);
    req.end();
  });
}

async function refreshCalendarToken() {
  try {
    const tokens = JSON.parse(readFileSync(TOKENS_FILE, 'utf8'));
    const account = tokens.normal;
    if (!account?.refresh_token) return;

    const needsRefresh = !account.expiry_date || (account.expiry_date - Date.now()) < REFRESH_THRESHOLD_MS;
    if (!needsRefresh) return;

    const creds = JSON.parse(readFileSync(CREDENTIALS_FILE, 'utf8'));
    const { client_id, client_secret } = creds.installed ?? creds.web ?? {};
    if (!client_id || !client_secret) return;

    const result = await httpsPost('oauth2.googleapis.com', '/token', {
      client_id, client_secret,
      refresh_token: account.refresh_token,
      grant_type: 'refresh_token',
    });

    if (!result.access_token) return;

    tokens.normal = {
      ...account,
      access_token: result.access_token,
      expiry_date: Date.now() + (result.expires_in ?? 3599) * 1000,
    };
    writeFileSync(TOKENS_FILE, JSON.stringify(tokens, null, 2), 'utf8');
    process.stderr.write('[warmup] Calendar token refreshed OK\n');
  } catch (err) {
    // Non-fatal: log and continue. MCP will retry its own refresh.
    process.stderr.write(`[warmup] Calendar token refresh skipped: ${err.message}\n`);
  }
}

// Refresh token FIRST, then warm all MCP servers in parallel
await refreshCalendarToken();

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
