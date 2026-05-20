import fs from 'fs';
import path from 'path';

const SRC = 'D:\\Dropbox\\宏祐\\20251104羅東聖母中醫診所規劃案\\P請購單\\20260512弱電機房線槽安裝請購單(已請購)(已驗收)';
const P_DIR = 'D:\\Dropbox\\宏祐\\20251104羅東聖母中醫診所規劃案\\P請購單';
const NEW_NAME = '20260520測試請購單';
const DST = path.join(P_DIR, NEW_NAME);

// 複製整個資料夾
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
console.error('複製完成，目的地：' + DST);

// 列出複製後的檔案
const allFiles = fs.readdirSync(DST);
console.error('複製後檔案：', allFiles);

// 清除舊 PDF
let deletedFiles = [];
for (const f of allFiles) {
  const fp = path.join(DST, f);
  if (f.endsWith('.pdf')) {
    fs.unlinkSync(fp);
    deletedFiles.push(f + ' (PDF)');
  }
}

// 找 xlsx 檔案，判斷空白範本（最小的）
const xlsxFiles = fs.readdirSync(DST).filter(f => f.endsWith('.xlsx'));
console.error('xlsx 檔案：', xlsxFiles);

let blankXlsx = null;
if (xlsxFiles.length === 1) {
  blankXlsx = xlsxFiles[0];
} else if (xlsxFiles.length > 1) {
  xlsxFiles.sort((a, b) => fs.statSync(path.join(DST, a)).size - fs.statSync(path.join(DST, b)).size);
  blankXlsx = xlsxFiles[0];
  // 刪除其他 xlsx
  for (const f of xlsxFiles.slice(1)) {
    fs.unlinkSync(path.join(DST, f));
    deletedFiles.push(f + ' (xlsx)');
  }
}

// 改名空白 xlsx
let xlsxPath = null;
if (blankXlsx) {
  const newXlsxName = NEW_NAME + '.xlsx';
  fs.renameSync(path.join(DST, blankXlsx), path.join(DST, newXlsxName));
  xlsxPath = path.join(DST, newXlsxName);
  console.error('xlsx 改名為：' + newXlsxName);
}

// 處理廠商報價子資料夾
const VENDOR_DIR = path.join(DST, '廠商報價');
let vendorCleared = false;
if (fs.existsSync(VENDOR_DIR)) {
  const vendorFiles = fs.readdirSync(VENDOR_DIR);
  for (const f of vendorFiles) {
    fs.unlinkSync(path.join(VENDOR_DIR, f));
  }
  vendorCleared = true;
  console.error('廠商報價資料夾已清空');
} else {
  fs.mkdirSync(VENDOR_DIR);
  console.error('廠商報價資料夾已建立');
}

console.log(JSON.stringify({
  dst: DST,
  xlsxPath,
  vendorDir: VENDOR_DIR,
  deletedFiles,
  vendorCleared
}));
