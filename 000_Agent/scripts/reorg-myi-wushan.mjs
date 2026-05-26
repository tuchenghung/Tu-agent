import fs from 'fs';
import path from 'path';

const BASE = 'D:\\Dropbox\\yushi\\20240612名毅吾山';

function log(emoji, msg) { console.log(emoji, msg); }

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function moveItem(src, dst) {
  if (!fs.existsSync(src)) { log('⚠️', '不存在: ' + src); return false; }
  ensureDir(path.dirname(dst));
  if (fs.existsSync(dst)) { log('⚠️', '目標已存在: ' + dst); return false; }
  fs.renameSync(src, dst);
  log('📁', path.relative(BASE, src) + ' → ' + path.relative(BASE, dst));
  return true;
}

function moveContents(srcDir, dstDir) {
  if (!fs.existsSync(srcDir)) { log('⚠️', '來源資料夾不存在: ' + srcDir); return; }
  ensureDir(dstDir);
  for (const item of fs.readdirSync(srcDir)) {
    moveItem(path.join(srcDir, item), path.join(dstDir, item));
  }
}

// Step 1: Create A-I standard folders
const aiDirs = [
  'A業主提供資料',
  'B規劃圖面',
  'C簡報資料',
  'D預算報價',
  'D預算報價\\參考報價',
  'E業主合同資料',
  'F供應商報價與資料',
  'F供應商報價與資料\\廠商報價',
  'G進度計畫管理',
  'H照片',
  'I其他',
];
for (const d of aiDirs) {
  ensureDir(path.join(BASE, d));
  log('✅', '建立: ' + d);
}

// Step 2: Delete junk files (._*, .bak, .dwl, .dwl2, plot.log)
function deleteJunk(dir) {
  if (!fs.existsSync(dir)) return;
  for (const item of fs.readdirSync(dir)) {
    const full = path.join(dir, item);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      deleteJunk(full);
    } else if (
      item.startsWith('._') ||
      item.endsWith('.bak') ||
      item.endsWith('.dwl') ||
      item.endsWith('.dwl2') ||
      item === 'plot.log'
    ) {
      fs.unlinkSync(full);
      log('🗑️', '刪除: ' + path.relative(BASE, full));
    }
  }
}
deleteJunk(BASE);

// Step 3: A業主提供資料
moveItem(
  path.join(BASE, '客變圖面', '建商客變資料'),
  path.join(BASE, 'A業主提供資料', '建商客變資料')
);
moveItem(
  path.join(BASE, '客變文件'),
  path.join(BASE, 'A業主提供資料', '客變文件')
);
moveItem(
  path.join(BASE, '附件客戶變更原則.docx'),
  path.join(BASE, 'A業主提供資料', '附件客戶變更原則.docx')
);

// Step 4: B規劃圖面 — 圖檔資料夾 + 客變圖面 PDFs + root files
moveItem(
  path.join(BASE, '圖檔'),
  path.join(BASE, 'B規劃圖面', '圖檔')
);
// Remaining items in 客變圖面 (建商客變資料 already moved)
const kvDir = path.join(BASE, '客變圖面');
if (fs.existsSync(kvDir)) {
  for (const item of fs.readdirSync(kvDir)) {
    moveItem(path.join(kvDir, item), path.join(BASE, 'B規劃圖面', item));
  }
}
moveItem(
  path.join(BASE, '20240612-Model.pdf'),
  path.join(BASE, 'B規劃圖面', '20240612-Model.pdf')
);
moveItem(
  path.join(BASE, '20240830客變圖7F C-3  周家榆 屋主.dwg'),
  path.join(BASE, 'B規劃圖面', '20240830客變圖7F C-3  周家榆 屋主.dwg')
);

// Step 5: C簡報資料
const cFiles = [
  '設備建議.docx',
  '165.png',
  '484300369_967677955497835_3623326171802839329_n.jpg',
  'apple_nso-marina-bay-sands_exterior_09072020_Full-Bleed-Image.jpg.xlarge_2x.jpg',
  'Ayia Napa Marina.jpg',
  'Docks_LandingPage_1210x535_150dpi-e1676644760863.jpeg',
  'Marina Bay Sands_1440x670_tcm154-41518.jpg.webp',
];
for (const f of cFiles) {
  moveItem(path.join(BASE, f), path.join(BASE, 'C簡報資料', f));
}

// Step 6: E業主合同資料
const eFiles = [
  '設計合約書111.01.01.doc',
  '設計合約書20240715.docx',
  '設計合約書20240715.pdf',
];
for (const f of eFiles) {
  moveItem(path.join(BASE, f), path.join(BASE, 'E業主合同資料', f));
}

// Step 7: F供應商報價與資料
moveItem(
  path.join(BASE, 'C棟廚具.pdf'),
  path.join(BASE, 'F供應商報價與資料', '廠商報價', 'C棟廚具.pdf')
);

// Step 8: H照片 — move contents (not folder itself, since H照片 already exists)
moveContents(path.join(BASE, '照片'), path.join(BASE, 'H照片'));

// Step 9: I其他
moveItem(
  path.join(BASE, 'desktop.ini'),
  path.join(BASE, 'I其他', 'desktop.ini')
);

// Summary
console.log('\n=== 完成 ===');
console.log('根目錄剩餘項目:');
for (const item of fs.readdirSync(BASE).sort()) {
  console.log(' ', item);
}
