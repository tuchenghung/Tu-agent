// 早晨日報用：列出 Notion 行動任務庫「逾期 + 今日到期」的未完成任務
// 用法：node 000_Agent/scripts/notion_tasks_overdue.mjs
// Token 來源：專案根目錄 .env 的 NOTION_TOKEN
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const env = readFileSync(resolve(ROOT, '.env'), 'utf8');
const TOKEN = (env.match(/^NOTION_TOKEN\s*=\s*(.+)$/m) || [])[1]?.trim().replace(/^["']|["']$/g, '');
const DB_ID = 'f1dc0829-774c-493a-aa21-eefc6e35b034';
const today = new Date().toLocaleDateString('sv-SE', { timeZone: 'Asia/Taipei' }); // YYYY-MM-DD

const body = JSON.stringify({
  filter: {
    and: [
      { property: 'Deadline', date: { on_or_before: today } },
      { property: '狀態', status: { does_not_equal: '完成' } },
    ],
  },
  sorts: [{ property: 'Deadline', direction: 'ascending' }],
});

const resp = await fetch(`https://api.notion.com/v1/databases/${DB_ID}/query`, {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${TOKEN}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
  },
  body,
});
const data = await resp.json();
if (data.object === 'error') { console.log(`ERR:${data.message}`); process.exit(1); }

const rows = (data.results ?? []).map((r) => {
  const p = r.properties;
  return {
    name: (p['任務']?.title || []).map((t) => t.plain_text).join(''),
    dl: p.Deadline?.date?.start?.slice(0, 10) || '',
    st: p['狀態']?.status?.name || '',
  };
});

const overdue = rows.filter((x) => x.dl < today);
const dueToday = rows.filter((x) => x.dl === today);

console.log(`TODAY:${today}  逾期:${overdue.length}  今日到期:${dueToday.length}`);
for (const x of overdue) console.log(`逾期|${x.dl}|${x.st}|${x.name}`);
for (const x of dueToday) console.log(`今日|${x.dl}|${x.st}|${x.name}`);
