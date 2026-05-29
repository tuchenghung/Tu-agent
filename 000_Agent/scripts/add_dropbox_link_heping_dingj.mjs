import 'dotenv/config';
const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = process.env.DROPBOX_APP_SECRET;
const DROPBOX_REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;
const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_PAGE_ID = '36f7aebd-089f-81ce-a65b-e23a38e764e6';

const FILES = [
  {
    path: '/宏祐/規劃中案件/202605-市醫和平院區醫療大樓8樓婦兒科病房整修/F供應商報價與資料/廠商報價/20260525-鼎堅-鐵工工程-p1.jpg',
    name: '20260525-鼎堅-鐵工工程-p1.jpg',
    archived: 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\\F供應商報價與資料\\廠商報價\\20260525-鼎堅-鐵工工程-p1.jpg'
  },
  {
    path: '/宏祐/規劃中案件/202605-市醫和平院區醫療大樓8樓婦兒科病房整修/F供應商報價與資料/廠商報價/20260525-鼎堅-鐵工工程-p2.jpg',
    name: '20260525-鼎堅-鐵工工程-p2.jpg',
    archived: 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\\F供應商報價與資料\\廠商報價\\20260525-鼎堅-鐵工工程-p2.jpg'
  }
];

const tokenResp = await fetch('https://api.dropboxapi.com/oauth2/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ grant_type: 'refresh_token', refresh_token: DROPBOX_REFRESH_TOKEN, client_id: DROPBOX_APP_KEY, client_secret: DROPBOX_APP_SECRET })
});
const tokenData = await tokenResp.json();
if (!tokenData.access_token) { console.error('token失敗:', JSON.stringify(tokenData)); process.exit(1); }
const token = tokenData.access_token;
console.log('✅ Dropbox token 取得');

async function getShareUrl(filePath) {
  const shareResp = await fetch('https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: filePath, settings: { requested_visibility: 'public' } })
  });
  const shareData = await shareResp.json();
  if (shareData.url) return shareData.url;
  if (shareData.error && shareData.error['.tag'] === 'shared_link_already_exists') {
    const listResp = await fetch('https://api.dropboxapi.com/2/sharing/list_shared_links', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: filePath, direct_only: true })
    });
    const listData = await listResp.json();
    return listData.links && listData.links[0] && listData.links[0].url;
  }
  console.error('分享連結失敗:', JSON.stringify(shareData));
  return null;
}

const urls = [];
for (const f of FILES) {
  const url = await getShareUrl(f.path);
  console.log(`✅ ${f.name}: ${url}`);
  urls.push({ ...f, url });
}

const blocks = [
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📎 原始報價單檔案' } }] } },
];
for (const f of urls) {
  blocks.push({ type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: `檔案名稱：${f.name}` } }] } });
  blocks.push({ type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: `歸檔路徑：${f.archived}` } }] } });
  blocks.push({ type: 'bookmark', bookmark: { url: f.url, caption: [{ type: 'text', text: { content: `點此開啟 Dropbox 檔案（${f.name}）` } }] } });
}

const notionResp = await fetch('https://api.notion.com/v1/blocks/' + NOTION_PAGE_ID + '/children', {
  method: 'PATCH',
  headers: { 'Authorization': 'Bearer ' + NOTION_TOKEN, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
  body: JSON.stringify({ children: blocks })
});
const notionData = await notionResp.json();
if (notionData.results) {
  console.log('✅ Notion 頁面已更新，加入', notionData.results.length, '個區塊');
} else {
  console.error('Notion 失敗:', JSON.stringify(notionData));
}
