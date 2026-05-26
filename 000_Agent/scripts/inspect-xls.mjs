import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('C:\\Users\\deco01\\nodejs\\node_modules\\xlsx\\xlsx.js');

// Check 機電標單 for any non-zero prices
const src1 = 'C:\\Users\\deco01\\Downloads\\機電標單.xls';
const wb1 = XLSX.readFile(src1);
process.stdout.write('\n=== 機電標單：有單價的行 ===\n');
for (const sn of wb1.SheetNames) {
  const ws = wb1.Sheets[sn];
  const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });
  let found = 0;
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];
    // Check columns 4 (單價) and 5 (複價) for non-zero numeric values
    const col4 = r[4], col5 = r[5];
    if ((typeof col4 === 'number' && col4 !== 0) || (typeof col5 === 'number' && col5 !== 0)) {
      process.stdout.write(`[${sn}] R${i+1}: ${r.slice(0,8).join('\t')}\n`);
      found++;
    }
  }
  if (!found) process.stdout.write(`[${sn}]: 所有單價為 0 或空白\n`);
}

// Show 合併版 機電 sheet header (first 12 rows) to see all columns
const src2 = 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\\D預算報價\\20260524-廠商報價三家合併版.xls';
const wb2 = XLSX.readFile(src2);
const ws2 = wb2.Sheets['標單詳細表 機電'];
process.stdout.write('\n=== 合併版 機電 sheet 欄結構 (前15行完整欄) ===\n');
const rows2 = XLSX.utils.sheet_to_json(ws2, { header: 1, defval: '' });
for (let i = 0; i < 15; i++) {
  process.stdout.write(`R${i+1} [${rows2[i].length}欄]: ${JSON.stringify(rows2[i])}\n`);
}
process.stdout.write('\n=== 合併版 機電 sheet：參/肆/伍 section (找水電空調醫療) ===\n');
let found = false;
for (let i = 0; i < rows2.length; i++) {
  const r = rows2[i];
  const c0 = String(r[0] || '');
  if (/^[參肆伍]/.test(c0)) {
    process.stdout.write(`R${i+1}: ${r.slice(0,10).join('\t')}\n`);
    found = true;
  }
}
if (!found) process.stdout.write('找不到 參/肆/伍 sections\n');
