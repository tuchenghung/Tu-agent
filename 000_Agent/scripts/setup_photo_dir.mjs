import fs from 'fs';
import path from 'path';

const CASE_ROOT = 'D:\\Dropbox\\宏祐\\20260511羅東聖母醫院防火門維修案';
const DATE = '2026-05-20';
const DOWNLOADS = 'C:\\Users\\deco01\\Downloads';
const PHOTOS = [
  '552174_0.jpg','552175_0.jpg','552176_0.jpg','552177_0.jpg','552178_0.jpg',
  '552179_0.jpg','552180_0.jpg','552181_0.jpg','552182_0.jpg','552183_0.jpg'
];

// 找 M照片 資料夾（不含/含空格都試）
const caseItems = fs.readdirSync(CASE_ROOT);
console.log('案件資料夾內容:', caseItems.join(', '));

const mFolder = caseItems.find(n => n.startsWith('M'));
if (!mFolder) { console.error('找不到 M照片 資料夾'); process.exit(1); }

const mPath = path.join(CASE_ROOT, mFolder);
const targetDir = path.join(mPath, DATE);
fs.mkdirSync(targetDir, { recursive: true });
console.log('目標資料夾:', targetDir);

// 複製照片
const copied = [];
for (const photo of PHOTOS) {
  const src = path.join(DOWNLOADS, photo);
  const dst = path.join(targetDir, photo);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dst);
    copied.push(photo);
    console.log('✅ 複製:', photo);
  } else {
    console.log('⚠️  找不到:', src);
  }
}
console.log(`\n完成：共複製 ${copied.length} 張照片到 ${targetDir}`);
