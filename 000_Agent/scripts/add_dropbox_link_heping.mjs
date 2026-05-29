import 'dotenv/config';
const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = process.env.DROPBOX_APP_SECRET;
const DROPBOX_REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;
const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_PAGE_ID = '36c7aebd-089f-812c-a82f-e73a399aefa6';
const FILE_PATH = '/宏祐/規劃中案件/202605-市醫和平院區醫療大樓8樓婦兒科病房整修/廠商報價/20260408-川游-系統櫃工程.pdf';
const FILE_NAME = '20260408-川游-系統櫃工程.pdf';
const ARCHIVED_PATH = 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\\廠商報價\\20260408-川游-系統櫃工程.pdf';

const tokenResp = await fetch('https://api.dropboxapi.com/oauth2/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ grant_type: 'refresh_token', refresh_token: DROPBOX_REFRESH_TOKEN, client_id: DROPBOX_APP_KEY, client_secret: DROPBOX_APP_SECRET })
});
const tokenData = await tokenResp.json();
if (!tokenData.access_token) { console.error('token失敗:', JSON.stringify(tokenData)); process.exit(1); }
const token = tokenData.access_token;
console.log('✅ Dropbox token 取得');

let shareUrl;
const shareResp = await fetch('https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
  body: JSON.stringify({ path: FILE_PATH, settings: { requested_visibility: 'public' } })
});
const shareData = await shareResp.json();
if (shareData.url) {
  shareUrl = shareData.url;
} else if (shareData.error && shareData.error['.tag'] === 'shared_link_already_exists') {
  const listResp = await fetch('https://api.dropboxapi.com/2/sharing/list_shared_links', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: FILE_PATH, direct_only: true })
  });
  const listData = await listResp.json();
  shareUrl = listData.links && listData.links[0] && listData.links[0].url;
} else {
  console.error('分享連結失敗:', JSON.stringify(shareData));
  process.exit(1);
}
console.log('✅ 分享連結:', shareUrl);

const notionResp = await fetch('https://api.notion.com/v1/blocks/' + NOTION_PAGE_ID + '/children', {
  method: 'PATCH',
  headers: { 'Authorization': 'Bearer ' + NOTION_TOKEN, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    children: [
      { type: 'callout', callout: { rich_text: [{ type: 'text', text: { content: '📎 原始報價單檔案' } }], icon: { emoji: '📎' }, color: 'gray_background' } },
      { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '檔案名稱：' + FILE_NAME } }] } },
      { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '歸檔路徑：' + ARCHIVED_PATH } }] } },
      { type: 'bookmark', bookmark: { url: shareUrl, caption: [{ type: 'text', text: { content: '點此開啟 Dropbox 檔案' } }] } }
    ]
  })
});
const notionData = await notionResp.json();
if (notionData.results) {
  console.log('✅ Notion 頁面已更新，加入', notionData.results.length, '個區塊');
} else {
  console.error('Notion 失敗:', JSON.stringify(notionData));
}
