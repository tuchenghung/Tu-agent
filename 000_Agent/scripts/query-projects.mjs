import 'dotenv/config';
import https from 'https';

const TOKEN = process.env.NOTION_TOKEN;
const body = JSON.stringify({
  sorts: [{ timestamp: 'last_edited_time', direction: 'descending' }],
  page_size: 8
});

const options = {
  hostname: 'api.notion.com',
  path: '/v1/databases/3355cac1-0351-4ef4-8eb1-8b8f0bb619c3/query',
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + TOKEN,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body)
  }
};

const data = await new Promise((resolve, reject) => {
  const req = https.request(options, (res) => {
    let raw = '';
    res.on('data', chunk => raw += chunk);
    res.on('end', () => resolve(JSON.parse(raw)));
  });
  req.on('error', reject);
  req.write(body);
  req.end();
});

for (const p of data.results || []) {
  const name = (p.properties['專案']?.title || []).map(t => t.plain_text).join('');
  const status = p.properties['狀態']?.status?.name || '';
  process.stdout.write(p.id + '|' + status + '|' + name + '\n');
}
