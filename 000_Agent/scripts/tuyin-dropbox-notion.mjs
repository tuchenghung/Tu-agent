const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = '94re6pu3w7da7ai';
const DROPBOX_REFRESH_TOKEN = 'LuH8PZgPJFMAAAAAAAAAAdr6cHmLKVVJlbIMEuT134q6eRdGp7H9rh8Niq_UBsbh';
const NOTION_TOKEN = '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';

// 取得 Dropbox access token
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

async function addNotionBlocks(pageId, children) {
  const resp = await fetch('https://api.notion.com/v1/blocks/' + pageId + '/children', {
    method: 'PATCH',
    headers: {
      'Authorization': 'Bearer ' + NOTION_TOKEN,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ children })
  });
  const data = await resp.json();
  if (!data.results) throw new Error('Notion 失敗: ' + JSON.stringify(data));
  return data.results.length;
}

// 1. 報價單連結
const reportPath = '/宏祐/舊案件/土銀大樓裝修/詢價資料/搗擺/廠商報價/20240604-祐明-導擺工程.pdf';
const reportUrl = await getShareLink(reportPath);
console.log('✅ 報價單連結:', reportUrl);

// 2. 圖說1 連結
const plan1Path = '/宏祐/舊案件/土銀大樓裝修/詢價資料/搗擺/廠商報價/20240604-祐明-導擺隔間施工詳圖.pdf';
const plan1Url = await getShareLink(plan1Path);
console.log('✅ 圖說1 連結:', plan1Url);

// 3. 圖說2 連結
const plan2Path = '/宏祐/舊案件/土銀大樓裝修/詢價資料/搗擺/20240603大樓廁所及樓梯間整修工程搗擺圖面.pdf';
const plan2Url = await getShareLink(plan2Path);
console.log('✅ 圖說2 連結:', plan2Url);

// 4. 報價單 Notion 頁面加入檔案資訊 + 圖說依據區塊
const QUOTE_PAGE = '36e7aebd-089f-81fd-a780-ec7b9f4a5577';
const n1 = await addNotionBlocks(QUOTE_PAGE, [
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📎 原始報價單檔案' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '檔案名稱：20240604-祐明-導擺工程.pdf' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '歸檔路徑：D:\\Dropbox\\宏祐\\舊案件\\土銀大樓裝修\\詢價資料\\搗擺\\廠商報價\\20240604-祐明-導擺工程.pdf' } }] } },
  { type: 'bookmark', bookmark: { url: reportUrl, caption: [{ type: 'text', text: { content: '點此開啟 Dropbox 報價單' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📐 報價圖說依據' } }] } },
  { type: 'bulleted_list_item', bulleted_list_item: { rich_text: [
    { type: 'text', text: { content: '廁所搗擺隔間詳圖（施工詳圖）：' } },
    { type: 'text', text: { content: '開啟 Dropbox 檔案', link: { url: plan1Url } } }
  ]}},
  { type: 'bulleted_list_item', bulleted_list_item: { rich_text: [
    { type: 'text', text: { content: '20240603大樓廁所及樓梯間整修工程搗擺圖面（38頁）：' } },
    { type: 'text', text: { content: '開啟 Dropbox 檔案', link: { url: plan2Url } } }
  ]}},
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📊 報價合理性分析：400_Knowledge/工程/2024-06-04_基隆土銀大樓廁所樓梯間整修_導擺工程報價合理性分析.md' } }] } },
]);
console.log('✅ 報價單頁面已加入', n1, '個區塊');

// 5. 圖說1 Notion 頁面加入檔案資訊
const PLAN1_PAGE = '36e7aebd-089f-8166-8515-e00fb6bd37b1';
const n2 = await addNotionBlocks(PLAN1_PAGE, [
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📎 原始圖說檔案' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '檔案名稱：20240604-祐明-導擺隔間施工詳圖.pdf' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '歸檔路徑：D:\\Dropbox\\宏祐\\舊案件\\土銀大樓裝修\\詢價資料\\搗擺\\廠商報價\\20240604-祐明-導擺隔間施工詳圖.pdf' } }] } },
  { type: 'bookmark', bookmark: { url: plan1Url, caption: [{ type: 'text', text: { content: '點此開啟 Dropbox 檔案' } }] } },
]);
console.log('✅ 圖說1 頁面已加入', n2, '個區塊');

// 6. 圖說2 Notion 頁面加入檔案資訊
const PLAN2_PAGE = '36e7aebd-089f-8131-a9cd-f94cdf4764e9';
const n3 = await addNotionBlocks(PLAN2_PAGE, [
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '📎 原始圖說檔案' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '檔案名稱：20240603大樓廁所及樓梯間整修工程搗擺圖面.pdf（38頁）' } }] } },
  { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: '歸檔路徑：D:\\Dropbox\\宏祐\\舊案件\\土銀大樓裝修\\詢價資料\\搿擺\\20240603大樓廁所及樓梯間整修工程搿擺圖面.pdf' } }] } },
  { type: 'bookmark', bookmark: { url: plan2Url, caption: [{ type: 'text', text: { content: '點此開啟 Dropbox 檔案' } }] } },
]);
console.log('✅ 圖說2 頁面已加入', n3, '個區塊');

console.log('\n🎉 全部完成！');
