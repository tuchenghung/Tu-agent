import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('C:\\Users\\deco01\\nodejs\\node_modules\\xlsx\\xlsx.js');

// ─── Extract prices from 機電標單's 標單單價分析表 ───
const src1 = 'C:\\Users\\deco01\\Downloads\\機電標單.xls';
const wb1 = XLSX.readFile(src1);
const ws1 = wb1.Sheets['標單單價分析表'];
const rows1 = XLSX.utils.sheet_to_json(ws1, { header: 1, defval: '' });

const priceMap = {}; // 項次 → unit price (合計 from col5)
let currentItem = null;
for (let i = 0; i < rows1.length; i++) {
  const r = rows1[i];
  const c0 = String(r[0] || '').trim();
  const c1 = String(r[1] || '').trim();

  // Detect item number like 參.一.1, 肆.五.2
  if (/^[參肆伍]/.test(c0) && c0.includes('.')) {
    currentItem = c0;
  }

  // 合計 row: price is in col5 (複價)
  if (c1 === '合計') {
    const price = r[5];
    if (typeof price === 'number' && price > 0 && currentItem) {
      priceMap[currentItem] = price;
    }
  }
}

process.stdout.write('=== 機電標單 價格表 (原價，col5) ===\n');
for (const [k, v] of Object.entries(priceMap)) {
  process.stdout.write(`  ${k}: ${v.toLocaleString()}\n`);
}

// ─── Scan 合併版 標單詳細表 for 參/肆/伍 items ───
const src2 = 'D:\\Dropbox\\宏祐\\規劃中案件\\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\\D預算報價\\20260524-廠商報價三家合併版.xls';
const wb2 = XLSX.readFile(src2);
const ws2 = wb2.Sheets['標單詳細表'];
const rows2 = XLSX.utils.sheet_to_json(ws2, { header: 1, defval: '' });

process.stdout.write('\n=== 合併版 標單詳細表 — 參/肆/伍 所有行 ===\n');
const meRows = []; // { row0, item, desc, unit, qty }
let inME = false;
for (let i = 0; i < rows2.length; i++) {
  const r = rows2[i];
  const c0 = String(r[0] || '').trim();

  // Section header detection
  if (/^[參肆伍]/.test(c0)) {
    inME = true;
  }

  if (inME) {
    const c1 = String(r[1] || '').trim();
    const c2 = String(r[2] || '').trim();
    const c3 = r[3];
    const c4 = r[4];
    const c5 = r[5];

    if (r.some(c => String(c).trim())) {
      process.stdout.write(`R${i+1}: [${c0}] ${c1.substring(0,30).padEnd(30)} 單位=${c2} 數量=${c3} 單價=${c4} 複價=${c5}\n`);

      // Item rows (not section headers, not empty, with unit/qty)
      if (c0 && c0.includes('.') && c2 && c3 !== undefined) {
        meRows.push({ row0: i, item: c0, desc: c1, unit: c2, qty: c3, unitPrice: c4 });
      }
    }
  }
}

process.stdout.write(`\n=== 可填入的明細行 (${meRows.length} 筆) ===\n`);
for (const m of meRows) {
  const srcPrice = priceMap[m.item];
  const markup = srcPrice ? Math.round(srcPrice * 1.1) : null;
  process.stdout.write(`R${m.row0+1}: ${m.item} | 數量=${m.qty} ${m.unit} | 廠商單價=${srcPrice || '無'} | +10%=${markup || '無'}\n`);
}

// ─── Generate FILLS for fill-xls-values.py ───
process.stdout.write('\n=== Python FILLS dict (0-based rows) ===\n');
const fills = {};
for (const m of meRows) {
  const srcPrice = priceMap[m.item];
  if (srcPrice) {
    const markup = Math.round(srcPrice * 1.1);
    fills[m.row0] = markup;
  }
}
process.stdout.write('FILLS = {\n');
for (const [row0, price] of Object.entries(fills)) {
  const m = meRows.find(r => r.row0 === parseInt(row0));
  process.stdout.write(`    ${row0}: ${price},  # ${m?.item} 原價=${priceMap[m?.item]?.toLocaleString()}\n`);
}
process.stdout.write('}\n');
