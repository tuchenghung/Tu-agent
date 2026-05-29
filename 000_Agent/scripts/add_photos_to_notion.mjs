import 'dotenv/config';
const NOTION_TOKEN = process.env.NOTION_TOKEN;
const PAGE_ID = '3667aebd-089f-8171-a124-ce4ad2179727';

const photos = [
  { file: '552174_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/v42n3qo9mkqyg2f4tnagl/552174_0.jpg?rlkey=fk955c3h3i3wu77yybr36jbiz&dl=1', caption: '防火門完工正面，雙扇常閉防火門（11F 樓梯口），安裝完成後門扇關閉正常' },
  { file: '552175_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/wagx4nsmmamar3ttssn6a/552175_0.jpg?rlkey=ycmssynqcr42xiy7r3xuwbgx8&dl=1', caption: '下方地絞鍊安裝完成，面板固定，地面水泥填補平整，底部旋轉頭露出' },
  { file: '552176_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/apf8erobezlpoio642q67/552176_0.jpg?rlkey=trn8m4zr6zbflvbdvc96wezj0&dl=1', caption: '上方 pivot 頂樞特寫，門頂旋轉軸連接門框，不鏽鋼框體固定完成' },
  { file: '552177_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/bq0ce3nyi7sevzvc6ucxl/552177_0.jpg?rlkey=dkbok803uu8mfvm8q6k5otbxe&dl=1', caption: '新 H-222 地絞鍊本體埋設中，對齊門框軸心，水泥填充固定' },
  { file: '552178_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/jr9gs34dgwh4qrwtd3u2g/552178_0.jpg?rlkey=n0080mmv7wbieg23r2t3ho507&dl=1', caption: 'H-222 本體放入預埋槽，水泥正在填充，待乾燥後蓋上面板' },
  { file: '552179_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/y89q3jv8miqi3ylzxjj3i/552179_0.jpg?rlkey=gzrz6eqr52ubkl0rtirep3k8v&dl=1', caption: '門頂上框側旋轉臂安裝特寫，齒狀調整片已對位、螺絲固定完成' },
  { file: '552180_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/havrqlzgzmen0ol9q01cp/552180_0.jpg?rlkey=mtiiqxnwoe6com4gnwnud68hv&dl=1', caption: '舊地絞鍊拆除後預埋槽現況，鏽蝕嚴重、殼體氧化變形' },
  { file: '552181_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/dy93fud5vkkek79mwfylw/552181_0.jpg?rlkey=0ojvir3uf60jojgcsovf6jzc9&dl=1', caption: '新舊地絞鍊對比：舊 HS-222（NS 0350739，嚴重鏽蝕）vs 新 H-222（NS 0011303）' },
  { file: '552182_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/4d7y5xyjulyo8ik78o0ax/552182_0.jpg?rlkey=7iyn5pb08e2ov6v0ybmr2jdx5&dl=1', caption: '施工中現場，防火門打開，工人於 11F 樓梯間施工' },
  { file: '552183_0.jpg', url: 'https://dl.dropboxusercontent.com/scl/fi/5bb729ov5wnkswp3cxtj7/552183_0.jpg?rlkey=1mjss6lv8zoj9jt7qfvp0slw8&dl=1', caption: '另一側舊地絞鍊拆除，預埋槽金屬殼扭曲變形，確認報廢' },
];

// 分批插入（每批 10 張）
const children = photos.map(p => ({
  type: 'image',
  image: {
    type: 'external',
    external: { url: p.url },
    caption: [{ type: 'text', text: { content: p.caption } }]
  }
}));

const resp = await fetch(`https://api.notion.com/v1/blocks/${PAGE_ID}/children`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${NOTION_TOKEN}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ children })
});

const data = await resp.json();
if (data.results) {
  console.log(`✅ 成功插入 ${data.results.length} 個 block`);
} else {
  console.error('❌ 失敗:', JSON.stringify(data, null, 2));
}
