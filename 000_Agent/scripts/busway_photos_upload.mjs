import 'dotenv/config';
const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = process.env.DROPBOX_APP_SECRET;
const DROPBOX_REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;
const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_PAGE_ID = '39f7aebd-089f-818f-b00a-fe97262f6ed5';

const DROPBOX_DIR = '/Tu-agent/400_Knowledge/工程/建材規格/images/busway';

const photos = [
  { file: 'busway_1.png', caption: '宇辰系統科技 - 匯流排施工實照，鋼構天花上方安裝現場' },
  { file: 'busway_2.png', caption: '宇辰系統科技 - 匯流排本體剖面示意（鋁排疊層結構）' },
  { file: 'busway_3.png', caption: '宇辰系統科技 - 匯流排本體剖面示意（銅排導體特寫）' },
  { file: 'busway_4.png', caption: '宇辰系統科技 - 匯流排系統組成示意圖（盤接頭/直線段/插入段/橋式模鑄接頭/插入單元/伸縮單元/末端接線箱/昇位彈簧/吊架）' },
  { file: 'busway_5.png', caption: '宇辰系統科技 - 資料中心/廠房天花安裝實照（藍黃雙排匯流排+電纜架）' },
  { file: 'busway_7.png', caption: '宇辰系統科技 - 天花安裝近拍，匯流排與線槽並排配置' },
];
const pdfFile = { file: '台達樹脂模鑄式匯流排_BR系列.pdf', name: '台達InfraSuite樹脂模鑄式匯流排BR系列型錄(250A-1600A)' };

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

async function getOrCreateLink(token, path) {
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

function toDirect(url) {
  return url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '?dl=1');
}

(async () => {
  console.log('取得 Dropbox token...');
  const token = await getAccessToken();

  const imageBlocks = [];
  for (const p of photos) {
    const path = `${DROPBOX_DIR}/${p.file}`;
    const url = await getOrCreateLink(token, path);
    const directUrl = toDirect(url);
    console.log('✅', p.file, directUrl);
    imageBlocks.push({
      type: 'image',
      image: { type: 'external', external: { url: directUrl }, caption: [{ type: 'text', text: { content: p.caption } }] }
    });
  }

  const pdfPath = `${DROPBOX_DIR}/${pdfFile.file}`;
  const pdfUrl = await getOrCreateLink(token, pdfPath);
  console.log('✅ PDF', pdfUrl);

  const children = [
    { type: 'heading_3', heading_3: { rich_text: [{ type: 'text', text: { content: '📷 產品實照（來源：宇辰系統科技官網）' } }] } },
    ...imageBlocks,
    { type: 'heading_3', heading_3: { rich_text: [{ type: 'text', text: { content: '📄 廠商型錄' } }] } },
    { type: 'bookmark', bookmark: { url: pdfUrl, caption: [{ type: 'text', text: { content: pdfFile.name } }] } },
  ];

  const resp = await fetch(`https://api.notion.com/v1/blocks/${NOTION_PAGE_ID}/children`, {
    method: 'PATCH',
    headers: { 'Authorization': `Bearer ${NOTION_TOKEN}`, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
    body: JSON.stringify({ children })
  });
  const data = await resp.json();
  if (data.results) {
    console.log(`✅ Notion 已插入 ${data.results.length} 個區塊`);
  } else {
    console.error('❌ Notion 失敗:', JSON.stringify(data, null, 2));
  }
})();
