import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('C:\\Users\\deco01\\nodejs\\node_modules\\xlsx\\xlsx.js');

const src = 'C:\\Users\\deco01\\Downloads\\機電標單.xls';
const wb = XLSX.readFile(src);

for (const sheetName of wb.SheetNames) {
  const ws = wb.Sheets[sheetName];
  const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });
  console.log('\n=== Sheet:', sheetName, '===');
  for (const row of rows) {
    if (row.some(c => String(c).trim())) {
      console.log(row.join('\t'));
    }
  }
}
