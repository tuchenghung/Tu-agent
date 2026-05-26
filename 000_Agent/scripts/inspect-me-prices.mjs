import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('C:\\Users\\deco01\\nodejs\\node_modules\\xlsx\\xlsx.js');

const src = 'C:\\Users\\deco01\\Downloads\\機電標單.xls';
const wb = XLSX.readFile(src);
const ws = wb.Sheets['標單單價分析表'];
const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });

// Show rows 1100-1145 around 參.一.1 合計
process.stdout.write('=== R1100-1145 (around 參.一.1) ===\n');
for (let i = 1099; i < Math.min(1145, rows.length); i++) {
  if (rows[i].some(c => String(c).trim())) {
    process.stdout.write(`R${i+1}: ${JSON.stringify(rows[i])}\n`);
  }
}

// Show rows 1130-1160 around 參.一.2
process.stdout.write('\n=== R1130-1160 (around 參.一.2) ===\n');
for (let i = 1129; i < Math.min(1160, rows.length); i++) {
  if (rows[i].some(c => String(c).trim())) {
    process.stdout.write(`R${i+1}: ${JSON.stringify(rows[i])}\n`);
  }
}

// Show all rows with large numeric values (>10000)
process.stdout.write('\n=== 所有數值 > 10000 的行 ===\n');
for (let i = 0; i < rows.length; i++) {
  const r = rows[i];
  for (let j = 0; j < r.length; j++) {
    if (typeof r[j] === 'number' && r[j] > 10000) {
      process.stdout.write(`R${i+1} col${j}: ${r[j]}  row=${JSON.stringify(r)}\n`);
      break;
    }
  }
}
