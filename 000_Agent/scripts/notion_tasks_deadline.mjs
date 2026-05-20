// 查詢 Tasks（行動任務庫）3 天內到期未完成任務
const TOKEN = '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';
const DB_ID = 'f1dc0829-774c-493a-aa21-eefc6e35b034';

const today = new Date().toISOString().split('T')[0];
const plus3 = new Date(Date.now() + 3 * 86400000).toISOString().split('T')[0];

const body = JSON.stringify({
  filter: {
    and: [
      { property: 'Deadline', date: { on_or_before: plus3 } },
      { property: 'Deadline', date: { on_or_after: today } },
      { property: '狀態', status: { does_not_equal: '完成' } }
    ]
  },
  sorts: [{ property: 'Deadline', direction: 'ascending' }]
});

const resp = await fetch(`https://api.notion.com/v1/databases/${DB_ID}/query`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
  },
  body
});

const data = await resp.json();
if (data.object === 'error') {
  console.log(`ERR:${data.message}`);
  process.exit(1);
}

console.log(`TOTAL:${data.results?.length ?? 0}`);
for (const r of data.results ?? []) {
  const p = r.properties;
  const name = (p['任務']?.title || []).map(t => t.plain_text).join('');
  const dl = p.Deadline?.date?.start || '';
  const st = p['狀態']?.status?.name || '';
  const pr = p['優先級']?.select?.name || '';
  console.log(`TASK|${dl}|${st}|${pr}|${name}`);
}
