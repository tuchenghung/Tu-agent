import 'dotenv/config';
const TOKEN = process.env.NOTION_TOKEN;
const PAGE_ID = '36b7aebd-089f-8142-945f-eb5c2054bb06';
const BASE = 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-羅東聖母醫院ICU及開刀房備援氣體工程';
const folders = [
  'A業主提供資料', 'B規劃圖面', 'C簡報資料', 'D預算報價',
  'E業主合同資料', 'F供應商報價與資料', 'G進度計畫管理', 'H照片', 'I其他'
];

function api(path, method, body) {
  return fetch('https://api.notion.com/v1' + path, {
    method: method || 'GET',
    headers: {
      'Authorization': 'Bearer ' + TOKEN,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json'
    },
    body: body ? JSON.stringify(body) : undefined
  }).then(r => r.json());
}

const page = await api('/blocks/' + PAGE_ID + '/children');
const headings = page.results.filter(b => b.type === 'heading_2');
console.log('找到', headings.length, '個折疊區塊');

for (let i = 0; i < headings.length; i++) {
  const folderPath = BASE + '\\' + folders[i];
  const children = await api('/blocks/' + headings[i].id + '/children');
  const bullet = children.results[0];
  if (bullet) {
    await api('/blocks/' + bullet.id, 'PATCH', {
      bulleted_list_item: {
        rich_text: [{ type: 'text', text: { content: folderPath } }]
      }
    });
    console.log('✅', folders[i]);
  }
}
console.log('完成');
