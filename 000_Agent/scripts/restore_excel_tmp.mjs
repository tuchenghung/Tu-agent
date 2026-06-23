import 'dotenv/config';

const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = process.env.DROPBOX_APP_SECRET;
const DROPBOX_REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;

const FILE_PATH = '/宏祐/規劃中案件/20260611-羅東聖母醫院AB1機房及S11簡報室隔音工程/D預算報價/20260612-羅東聖母醫院AB1機房及S11簡報室隔音工程.xlsx';

// 取得 access token
const tokenResp = await fetch('https://api.dropboxapi.com/oauth2/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: DROPBOX_REFRESH_TOKEN,
    client_id: DROPBOX_APP_KEY,
    client_secret: DROPBOX_APP_SECRET,
  })
});
const tokenData = await tokenResp.json();
if (!tokenData.access_token) { console.error('token 失敗:', JSON.stringify(tokenData)); process.exit(1); }
const token = tokenData.access_token;

// 列出版本歷史
const revResp = await fetch('https://api.dropboxapi.com/2/files/list_revisions', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
  body: JSON.stringify({ path: FILE_PATH, limit: 10 })
});
const revData = await revResp.json();

if (!revData.entries) {
  console.error('取得版本失敗:', JSON.stringify(revData));
  process.exit(1);
}

console.log('=== 版本歷史 ===');
revData.entries.forEach((e, i) => {
  console.log(`[${i}] rev=${e.rev} | ${e.client_modified} | size=${e.size} bytes`);
});
