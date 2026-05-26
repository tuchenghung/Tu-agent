import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('C:\\Users\\deco01\\nodejs\\node_modules\\xlsx\\xlsx.js');

const src = 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\\D預算報價\\20260524-廠商報價三家合併版.xls';
const wb = XLSX.readFile(src);
const ws = wb.Sheets['標單詳細表'];
const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });

// Show rows 290-350 (around row 297)
process.stdout.write('=== 合併版 標單詳細表 R290-R350 ===\n');
for (let i = 289; i < Math.min(350, rows.length); i++) {
  if (rows[i].some(c => String(c).trim())) {
    process.stdout.write(`R${i+1}: ${rows[i].slice(0,8).join('\t')}\n`);
  }
}
