import 'dotenv/config';
const DROPBOX_APP_KEY = 't1n8ea51gyluo9o';
const DROPBOX_APP_SECRET = process.env.DROPBOX_APP_SECRET;
const DROPBOX_REFRESH_TOKEN = process.env.DROPBOX_REFRESH_TOKEN;
const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_PAGE_ID = '39f7aebd-089f-818f-b00a-fe97262f6ed5';

const DROPBOX_DIR = '/Tu-agent/400_Knowledge/工程/建材規格/images/busway';

const photos = [
  { file: 'IMG_3335.jpg', caption: 'TaiwanBusway 裝甲型匯流排 - 水平天花明架安裝，雙排LV幹線並列（同層配合冰水管佈設）' },
  { file: 'IMG_3368.jpg', caption: 'TaiwanBusway 裝甲型匯流排 - 轉角接頭(Elbow)與末端分接盒安裝特寫' },
  { file: 'IMG_0127.jpg', caption: 'TaiwanBusway 裝甲型匯流排 - 天花吊架多排LV幹線並列配置' },
  { file: 'IMG_0146.jpg', caption: 'TaiwanBusway 裝甲型匯流排 - 密集插入式分接單元(Plug-in Unit)配置，逐區分接取電' },
  { file: 'IMG_0097.jpg', caption: 'TaiwanBusway 裝甲型匯流排 - 大型末端接線箱(End Cable Box)/轉角接頭特寫' },
  { file: 'IMG_8958.jpg', caption: 'TaiwanBusway 裝甲型匯流排 - 垂直管道間(Riser)安裝，含樓層分接箱' },
  { file: 'IMG_8963.jpg', caption: 'TaiwanBusway 裝甲型匯流排 - 垂直轉水平轉接處(Edge to Flat Elbow)施工中' },
  { file: 'IMG_8959.jpg', caption: 'TaiwanBusway 裝甲型匯流排 - 垂直幹線搭配斷路器箱體(MCCB分接箱)' },
];

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
  return url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace(/&dl=0/, '&dl=1').replace(/\?dl=0/, '?dl=1');
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

  function bullet(text) { return { type: 'bulleted_list_item', bulleted_list_item: { rich_text: [{ type: 'text', text: { content: text } }] } }; }
  function para(text, bold=false) { return { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: text }, annotations: { bold } }] } }; }
  function heading(text) { return { type: 'heading_3', heading_3: { rich_text: [{ type: 'text', text: { content: text } }] } }; }

  const children = [
    heading('🛡️ 裝甲型匯流排 Cast Resin Busway（來源：TaiwanBusway 巴斯威爾）'),
    para('三種容量分級與適用場景：'),
    bullet('MV中高壓 17.5KV 800A~5000A：高壓幹線，適用自設變電站至配電盤間輸送、發電機併接站高壓輸送、大型工廠/資料中心一次側高壓配電'),
    bullet('LV低壓 1.0KV 400A~6400A：大樓垂直管道間主幹線配電，變電站低壓配電盤到各樓層電氣室（對應中華郵政案銅匯流排CU Bus way主幹線規模）'),
    bullet('插入式單元 50A~2000A：逐層/逐區分接取電用Tap-off Box，接於LV/MV幹線供各樓層分電箱、機櫃取電'),
    para('防護等級：IP68(入水保護)/IP66(插入槽保護)/IP55(最大PIU防護)/IK10(機械衝擊)'),
    para('適用標準：IEC國際標準、美國UL標準、CNS12514(840℃ 30分鐘)、IEC60331(750℃ 3小時)、BS6387(950℃ 3小時)、地震認證0.8g/GR-63'),
    heading('📷 施工實照（來源：使用者提供，TaiwanBusway應用案例）'),
    ...imageBlocks,
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
