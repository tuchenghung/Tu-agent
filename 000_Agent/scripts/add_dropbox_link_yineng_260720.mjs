import 'dotenv/config';
const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = process.env.DROPBOX_APP_SECRET;
const DROPBOX_REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;
const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_PAGE_ID = '3a37aebd-089f-813d-bf8f-c1524f330721';
const FILE_PATH = '/yushi/施工中案件/20260618-西湖6F辦公室空調修改工程/J供應商資料/20260720-誼能-空調280560含稅.pdf';
const FILE_NAME = '20260720-誼能-空調280560含稅.pdf';

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
} else if (shareData.error?.['.tag'] === 'shared_link_already_exists') {
  const listResp = await fetch('https://api.dropboxapi.com/2/sharing/list_shared_links', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: FILE_PATH, direct_only: true })
  });
  const listData = await listResp.json();
  shareUrl = listData.links?.[0]?.url;
} else {
  console.error('分享連結失敗:', JSON.stringify(shareData));
  process.exit(1);
}
console.log('✅ 分享連結:', shareUrl);

const notionResp = await fetch('https://api.notion.com/v1/blocks/' + NOTION_PAGE_ID + '/children', {
  method: 'PATCH',
  headers: {
    'Authorization': 'Bearer ' + NOTION_TOKEN,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    children: [
      {
        type: 'callout',
        callout: {
          rich_text: [{ type: 'text', text: { content: '📎 原始報價單檔案' } }],
          icon: { emoji: '📎' },
          color: 'gray_background'
        }
      },
      {
        type: 'paragraph',
        paragraph: {
          rich_text: [{ type: 'text', text: { content: '檔案名稱：' + FILE_NAME } }]
        }
      },
      {
        type: 'paragraph',
        paragraph: {
          rich_text: [{ type: 'text', text: { content: '歸檔路徑：D:\\Dropbox\\yushi\\施工中案件\\20260618-西湖6F辦公室空調修改工程\\J供應商資料\\' + FILE_NAME } }]
        }
      },
      {
        type: 'bookmark',
        bookmark: {
          url: shareUrl,
          caption: [{ type: 'text', text: { content: '點此開啟 Dropbox 檔案' } }]
        }
      }
    ]
  })
});
const notionData = await notionResp.json();
if (notionData.results) {
  console.log('✅ Notion 頁面已更新，加入', notionData.results.length, '個區塊');
} else {
  console.error('Notion 失敗:', JSON.stringify(notionData));
}
