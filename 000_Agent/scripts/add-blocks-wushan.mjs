import 'dotenv/config';
const TOKEN = process.env.NOTION_TOKEN;
const PAGE_ID = '36b7aebd-089f-81c2-b191-e124c1be3ef0';
const BASE = 'D:\\Dropbox\\yushi\\20240612名毅吾山';
const SEP = '\\';

const sections = [
  ['A 業主提供資料', 'A業主提供資料'],
  ['B 規劃圖面',     'B規劃圖面'],
  ['C 簡報資料',     'C簡報資料'],
  ['D 預算報價',     'D預算報價'],
  ['E 業主合同資料', 'E業主合同資料'],
  ['F 供應商報價與資料', 'F供應商報價與資料'],
  ['G 進度計畫管理', 'G進度計畫管理'],
  ['H 照片',         'H照片'],
  ['I 其他',         'I其他'],
];

const children = sections.map(([title, folder]) => ({
  object: 'block',
  type: 'heading_2',
  heading_2: {
    rich_text: [{ type: 'text', text: { content: title } }],
    is_toggleable: true,
    children: [{
      object: 'block',
      type: 'bulleted_list_item',
      bulleted_list_item: {
        rich_text: [{ type: 'text', text: { content: BASE + SEP + folder } }]
      }
    }]
  }
}));

const r = await fetch('https://api.notion.com/v1/blocks/' + PAGE_ID + '/children', {
  method: 'PATCH',
  headers: {
    'Authorization': 'Bearer ' + TOKEN,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ children })
});
const d = await r.json();
console.log('Done:', d.results?.length, 'blocks');
