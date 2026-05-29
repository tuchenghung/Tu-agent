import 'dotenv/config';
// Dropbox OAuth2 設定（永久有效的 refresh token，不需要手動更新）
const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = process.env.DROPBOX_APP_SECRET;
const DROPBOX_REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;

const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_PAGE_ID = '3617aebd-089f-81ec-878a-c8b671569956'; // 修改為目標頁面 ID
const PROJECT_PATH = '/宏祐/20260331南投基督教醫院的裝修工程';  // 修改為目標專案路徑

const FOLDER_MAP = {
  A: 'A業主提供資料',
  B: 'B規劃圖面',
  C: 'C簡報資料',
  D: 'D預算報價',
  E: 'E業主合同資料',
  F: 'F供應商報價與資料',
  G: 'G進度計畫管理',
  H: 'H照片',
  I: 'I其他',
};

const FOLDERS_WITH_CONTENT = ['A', 'D', 'F']; // 修改為有內容的資料夾

// 用 refresh token 取得新的 access token（自動，不需手動）
async function getAccessToken() {
  const resp = await fetch('https://api.dropboxapi.com/oauth2/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: DROPBOX_REFRESH_TOKEN,
      client_id: DROPBOX_APP_KEY,
      client_secret: DROPBOX_APP_SECRET,
    })
  });
  const data = await resp.json();
  if (!data.access_token) throw new Error('取得 access token 失敗: ' + JSON.stringify(data));
  return data.access_token;
}

async function getOrCreateDropboxLink(token, path) {
  const resp = await fetch('https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, settings: { requested_visibility: 'public' } })
  });
  const data = await resp.json();
  if (data.url) return data.url;

  if (data.error?.['.tag'] === 'shared_link_already_exists') {
    const listResp = await fetch('https://api.dropboxapi.com/2/sharing/list_shared_links', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ path, direct_only: true })
    });
    const listData = await listResp.json();
    return listData.links?.[0]?.url || null;
  }
  throw new Error(JSON.stringify(data.error || data));
}

async function getNotionBlocks() {
  const resp = await fetch(`https://api.notion.com/v1/blocks/${NOTION_PAGE_ID}/children`, {
    headers: { 'Authorization': `Bearer ${NOTION_TOKEN}`, 'Notion-Version': '2022-06-28' }
  });
  return (await resp.json()).results || [];
}

async function addBookmarkToBlock(blockId, url, caption) {
  const resp = await fetch(`https://api.notion.com/v1/blocks/${blockId}/children`, {
    method: 'PATCH',
    headers: { 'Authorization': `Bearer ${NOTION_TOKEN}`, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
    body: JSON.stringify({
      children: [{
        object: 'block',
        type: 'bookmark',
        bookmark: { url, caption: [{ type: 'text', text: { content: caption } }] }
      }]
    })
  });
  return resp.json();
}

(async () => {
  // 自動取得新的 access token
  console.log('【Step 0】取得 Dropbox access token...');
  const DROPBOX_TOKEN = await getAccessToken();
  console.log('  ✅ token 已自動更新');

  // Step 1: Dropbox shared links
  console.log('\n【Step 1】建立 Dropbox 分享連結...');
  const links = {};
  for (const key of FOLDERS_WITH_CONTENT) {
    const folderName = FOLDER_MAP[key];
    const path = `${PROJECT_PATH}/${folderName}`;
    try {
      const url = await getOrCreateDropboxLink(DROPBOX_TOKEN, path);
      links[key] = url;
      console.log(`  ✅ ${folderName}`);
    } catch (e) {
      console.error(`  ❌ ${folderName}: ${e.message}`);
    }
  }

  // Step 2: Get Notion page blocks
  console.log('\n【Step 2】讀取 Notion 頁面區塊...');
  const blocks = await getNotionBlocks();
  const headings = blocks.filter(b => b.type === 'heading_2');
  console.log(`  找到 ${headings.length} 個折疊標題`);

  // Step 3: Add bookmarks
  console.log('\n【Step 3】插入 Dropbox 連結至 Notion...');
  for (const block of headings) {
    const titleText = block.heading_2?.rich_text?.[0]?.plain_text || '';
    const key = titleText.charAt(0);
    if (!links[key]) continue;

    const folderName = FOLDER_MAP[key];
    const result = await addBookmarkToBlock(block.id, links[key], `📂 開啟 Dropbox 資料夾：${folderName}`);
    if (result.results) {
      console.log(`  ✅ "${titleText}" 已加入連結`);
    } else {
      console.error(`  ❌ "${titleText}" 失敗: ${JSON.stringify(result)}`);
    }
  }

  console.log('\n✅ 完成！');
})();
