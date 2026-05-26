import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('C:\\Users\\deco01\\nodejs\\node_modules\\xlsx\\xlsx.js');

const src = 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\\D預算報價\\20260524-廠商報價三家合併版.xls';
const wb = XLSX.readFile(src);

console.log('Sheets:', wb.SheetNames);
for (const sheetName of wb.SheetNames) {
  const ws = wb.Sheets[sheetName];
  const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });
  console.log('\n=== Sheet:', sheetName, '===');
  for (let i = 0; i < Math.min(rows.length, 60); i++) {
    const row = rows[i];
    if (row.some(c => String(c).trim())) {
      console.log(`R${i+1}:`, row.join('\t'));
    }
  }
}
