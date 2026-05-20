import fs from 'fs';
import path from 'path';

const SRC = 'D:\\Dropbox\\宏祐\\20251104羅東聖母中醫診所規劃案\\P請購單\\20260520測試請購單';
const P_DIR = 'D:\\Dropbox\\宏祐\\20260511羅東聖母醫院防火門維修案\\P請購單';
const NEW_NAME = '20260520防火門維修請購單';
const DST = path.join(P_DIR, NEW_NAME);

function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const item of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, item.name);
    const d = path.join(dst, item.name);
    if (item.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

console.error('複製資料夾中...');
copyDir(SRC, DST);
console.error('複製完成：' + DST);

const allFiles = fs.readdirSync(DST);
console.error('複製後檔案：', allFiles);

// 刪除舊 PDF
for (const f of allFiles) {
  if (f.endsWith('.pdf')) {
    fs.unlinkSync(path.join(DST, f));
    console.error('刪除 PDF：' + f);
  }
}

// 找 xlsx，保留最小的（空白範本），改名
const xlsxFiles = fs.readdirSync(DST).filter(f => f.endsWith('.xlsx'));
let blankXlsx = null;
if (xlsxFiles.length === 1) {
  blankXlsx = xlsxFiles[0];
} else if (xlsxFiles.length > 1) {
  xlsxFiles.sort((a, b) => fs.statSync(path.join(DST, a)).size - fs.statSync(path.join(DST, b)).size);
  blankXlsx = xlsxFiles[0];
  for (const f of xlsxFiles.slice(1)) {
    fs.unlinkSync(path.join(DST, f));
    console.error('刪除多餘 xlsx：' + f);
  }
}

let xlsxPath = null;
if (blankXlsx) {
  const newName = NEW_NAME + '.xlsx';
  fs.renameSync(path.join(DST, blankXlsx), path.join(DST, newName));
  xlsxPath = path.join(DST, newName);
  console.error('xlsx 改名為：' + newName);
}

// 廠商報價資料夾
const VENDOR_DIR = path.join(DST, '廠商報價');
if (fs.existsSync(VENDOR_DIR)) {
  for (const f of fs.readdirSync(VENDOR_DIR)) fs.unlinkSync(path.join(VENDOR_DIR, f));
  console.error('廠商報價資料夾已清空');
} else {
  fs.mkdirSync(VENDOR_DIR);
  console.error('廠商報價資料夾已建立');
}

console.log(JSON.stringify({ dst: DST, xlsxPath, vendorDir: VENDOR_DIR }));
