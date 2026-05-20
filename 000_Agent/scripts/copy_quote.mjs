import fs from 'fs';
import path from 'path';

const SRC = 'C:\\Users\\deco01\\Downloads\\地坪水泥粉光-銓聯.xls';
const VENDOR_DIR = 'D:\\Dropbox\\宏祐\\20251104羅東聖母中醫診所規劃案\\P請購單\\20260520測試請購單\\廠商報價';

const fileName = path.basename(SRC);
const DST = path.join(VENDOR_DIR, fileName);

if (!fs.existsSync(SRC)) {
  console.error('找不到檔案：' + SRC);
  process.exit(1);
}

fs.copyFileSync(SRC, DST);
console.log(JSON.stringify({ quotePath: DST, fileName }));
console.error('✅ 報價單已複製至：' + DST);
