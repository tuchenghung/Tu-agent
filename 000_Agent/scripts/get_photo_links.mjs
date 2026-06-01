import 'dotenv/config';
const APP_KEY = 't1n8ea51gyluo9o';
const APP_SECRET = process.env.DROPBOX_APP_SECRET;
const REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;

const DROPBOX_FOLDER = '/宏祐/20260511羅東聖母醫院防火門維修案/M  照片/2026-05-20';
const PHOTOS = [
  '552174_0.jpg','552175_0.jpg','552176_0.jpg','552177_0.jpg','552178_0.jpg',
  '552179_0.jpg','552180_0.jpg','552181_0.jpg','552182_0.jpg','552183_0.jpg'
];

async function getToken() {
  const r = await fetch('https://api.dropboxapi.com/oauth2/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'refresh_token', refresh_token: REFRESH_TOKEN, client_id: APP_KEY, client_secret: APP_SECRET })
  });
  const d = await r.json();
  if (!d.access_token) throw new Error('token 失敗: ' + JSON.stringify(d));
  return d.access_token;
}

async function getLink(token, filePath) {
  const r = await fetch('https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: filePath, settings: { requested_visibility: 'public' } })
  });
  const d = await r.json();
  if (d.url) {
    return d.url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0','').replace('&dl=0','') + '&dl=1';
  }
  if (d.error?.['.tag'] === 'shared_link_already_exists') {
    const r2 = await fetch('https://api.dropboxapi.com/2/sharing/list_shared_links', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: filePath, direct_only: true })
    });
    const url = (await r2.json()).links?.[0]?.url || '';
    return url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0','').replace('&dl=0','') + '&dl=1';
  }
  throw new Error(JSON.stringify(d));
}

const token = await getToken();
process.stderr.write('✅ Token 取得\n');

const result = {};
for (const photo of PHOTOS) {
  try {
    result[photo] = await getLink(token, DROPBOX_FOLDER + '/' + photo);
    process.stderr.write('✅ ' + photo + '\n');
  } catch(e) {
    process.stderr.write('❌ ' + photo + ': ' + e.message + '\n');
    result[photo] = null;
  }
}
console.log(JSON.stringify(result, null, 2));
