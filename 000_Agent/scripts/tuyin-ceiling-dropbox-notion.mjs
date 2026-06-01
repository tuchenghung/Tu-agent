import 'dotenv/config';
const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = process.env.DROPBOX_APP_SECRET;
const DROPBOX_REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;
const NOTION_TOKEN = process.env.NOTION_TOKEN;

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

async function getShareLink(filePath) {
  const resp = await fetch('https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: filePath, settings: { requested_visibility: 'public' } })
  });
  const data = await resp.json();
  if (data.url) return data.url;
  if (data.error?.['.tag'] === 'shared_link_already_exists') {
    const listResp = await fetch('https://api.dropboxapi.com/2/sharing/list_shared_links', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: filePath, direct_only: true })
    });
    const listData = await listResp.json();
    return listData.links?.[0]?.url;
  }
  throw new Error('分享連結失敗: ' + JSON.stringify(data));
}

async function addBlocks(pageId, children) {
  const resp = await fetch('https://api.notion.com/v1/blocks/' + pageId + '/children', {
    method: 'PATCH',
    headers: { 'Authorization': 'Bearer ' + NOTION_TOKEN, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
    body: JSON.stringify({ children })
  });
  const data = await resp.json();
  if (!data.results) throw new Error('Notion 失敗: ' + JSON.stringify(data));
  return data.results.length;
}

// 取連結
const reportPath = '/宏祐/舊案件/土銀大樓裝修/詢價資料/輕鋼架/20240617台大天花板報價單(懷湘).pdf';
const boqPath = '/宏祐/舊案件/土銀大樓裝修/詢價資料/輕鋼架/20240529大樓廁所及樓梯間整修工程輕鋼架標單.pdf';

const reportUrl = await getShareLink(reportPath);
console.log('✅ 報價單:', reportUrl);

const boqUrl = await getShareLink(boqPath);
console.log('✅ 標單:', boqUrl);

// 報價單頁面加入檔案資訊 + 圖說依據
const QUOTE_PAGE = '36e7aebd-089f-8183-b2f9-c41c09471f71';
const n1 = await addBlocks(QUOTE_PAGE, [
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📎 原始報價單檔案' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '檔案名稱：20240615-懷湘-天花板工程.pdf' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '歸檔路徑：D:\\Dropbox\\宏祐\\舊案件\\土銀大樓裝修\\詢價資料\\輕鋼架\\20240615-懷湘-天花板工程.pdf' } }] } },
  { type: 'bookmark', bookmark: { url: reportUrl, caption: [{ type: 'text', text: { content: '點此開啟 Dropbox 報價單' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📐 報價圖說依據' } }] } },
  { type: 'bulleted_list_item', bulleted_list_item: { rich_text: [
    { type: 'text', text: { content: '輕鋼架天花板工程標單（BOQ）：' } },
    { type: 'text', text: { content: '開啟 Dropbox 檔案', link: { url: boqUrl } } }
  ]}},
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📊 報價合理性分析：400_Knowledge/工程/2024-06-15_基隆土銀大樓廁所樓梯間整修_天花板工程報價合理性分析.md' } }] } },
]);
console.log('✅ 報價單頁面加入', n1, '個區塊');

// 標單頁面加入檔案資訊
const BOQ_PAGE = '36e7aebd-089f-81d1-aa22-d5a73397f08f';
const n2 = await addBlocks(BOQ_PAGE, [
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📎 原始標單檔案' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '檔案名稱：20240529-土銀大樓-天花板工程標單.pdf' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '歸檔路徑：D:\\Dropbox\\宏祐\\舊案件\\土銀大樓裝修\\詢價資料\\輕鋼架\\20240529-土銀大樓-天花板工程標單.pdf' } }] } },
  { type: 'bookmark', bookmark: { url: boqUrl, caption: [{ type: 'text', text: { content: '點此開啟 Dropbox 檔案' } }] } },
]);
console.log('✅ 標單頁面加入', n2, '個區塊');

console.log('\n🎉 全部完成！');
