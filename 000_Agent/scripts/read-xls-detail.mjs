import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('C:\\Users\\deco01\\nodejs\\node_modules\\xlsx\\xlsx.js');

// Read 機電標單 - list all sheets and show items with 參/肆/伍 (water/HVAC/medical)
const src = 'C:\\Users\\deco01\\Downloads\\機電標單.xls';
const wb1 = XLSX.readFile(src);
process.stdout.write('\n=== 機電標單 Sheets: ' + wb1.SheetNames.join(', ') + '\n');
for (const sn of wb1.SheetNames) {
  const ws = wb1.Sheets[sn];
  const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });
  process.stdout.write('\n--- Sheet: ' + sn + ' (rows=' + rows.length + ')\n');
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];
    const line = r.join('\t');
    // Show rows with content - first 20 rows and rows with 參/肆/伍 section headers
    if (i < 20 || /^[參肆伍]/.test(String(r[0])) || (String(r[0]).includes('參') || String(r[1] || '').includes('水電') || String(r[1] || '').includes('消防') || String(r[1] || '').includes('空調'))) {
      if (r.some(c => String(c).trim())) process.stdout.write(`R${i+1}: ${line}\n`);
    }
  }
}

// Read 合併版 機電 sheet
const src2 = 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\\D預算報價\\20260524-廠商報價三家合併版.xls';
const wb2 = XLSX.readFile(src2);
const meSheet = wb2.Sheets['標單詳細表 機電'];
if (meSheet) {
  const rows = XLSX.utils.sheet_to_json(meSheet, { header: 1, defval: '' });
  process.stdout.write('\n\n=== 合併版：標單詳細表 機電 (first 60 rows) ===\n');
  for (let i = 0; i < Math.min(rows.length, 60); i++) {
    if (rows[i].some(c => String(c).trim())) {
      process.stdout.write(`R${i+1}: ${rows[i].join('\t')}\n`);
    }
  }
}
