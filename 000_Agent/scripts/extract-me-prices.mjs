import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('C:\\Users\\deco01\\nodejs\\node_modules\\xlsx\\xlsx.js');

// Extract item→price mappings from 機電標單's 標單單價分析表
const src = 'C:\\Users\\deco01\\Downloads\\機電標單.xls';
const wb = XLSX.readFile(src);

// ─── Part 1: Extract from 標單單價分析表 ───
const ws1 = wb.Sheets['標單單價分析表'];
const rows1 = XLSX.utils.sheet_to_json(ws1, { header: 1, defval: '' });

process.stdout.write('\n=== 機電標單 標單單價分析表 — 所有 合計 行 ===\n');
const priceMap = {}; // 項次 → price

let currentItem = null;
for (let i = 0; i < rows1.length; i++) {
  const r = rows1[i];
  const c0 = String(r[0] || '').trim();
  const c1 = String(r[1] || '').trim();
  const c2 = String(r[2] || '').trim();

  // Detect item number rows like 參.一.1, 肆.二.3, etc.
  if (/^[參肆伍]/.test(c0) && c0.includes('.')) {
    currentItem = c0;
  }

  // Detect 合計 rows with numeric value
  if (c0 === '合計' || c1 === '合計' || c2 === '合計') {
    // Find numeric value in the row
    let price = null;
    for (let j = 0; j < r.length; j++) {
      if (typeof r[j] === 'number' && r[j] > 0) {
        price = r[j];
        break;
      }
    }
    if (price !== null && currentItem) {
      priceMap[currentItem] = price;
      process.stdout.write(`R${i+1}: 項次=${currentItem}  合計=${price}\n`);
    }
  }
}

process.stdout.write(`\n共找到 ${Object.keys(priceMap).length} 個有價格的項次\n`);
process.stdout.write('\n=== priceMap JSON ===\n');
process.stdout.write(JSON.stringify(priceMap, null, 2) + '\n');

// ─── Part 2: Show 合計 context more clearly ───
process.stdout.write('\n=== 前30筆 合計 行詳細 (with surrounding context) ===\n');
let count = 0;
let lastItem = null;
for (let i = 0; i < rows1.length; i++) {
  const r = rows1[i];
  const c0 = String(r[0] || '').trim();
  const c1 = String(r[1] || '').trim();

  if (/^[參肆伍]/.test(c0) && c0.includes('.')) {
    lastItem = c0;
  }

  if ((c0 === '合計' || c1 === '合計') && count < 30) {
    process.stdout.write(`R${i+1} [${lastItem}] 合計: ${r.slice(0,8).join(' | ')}\n`);
    count++;
  }
}
