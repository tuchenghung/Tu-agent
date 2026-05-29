import fs from 'fs';
import path from 'path';

const BASE = 'D:\\Dropbox\\宏祐\\舊案件\\土銀大樓裝修\\詢價資料\\搗擺\\廠商報價';

function mv(src, dest) {
  const s = path.join(BASE, src);
  const d = path.join(BASE, dest);
  if (fs.existsSync(s)) {
    fs.renameSync(s, d);
    console.log('✅', src, '→', dest);
  } else {
    console.log('❌ NOT FOUND:', src);
  }
}

mv('113.06.04 - 宏祐 - 基隆大樓裝修案.pdf', '20240604-祐明-導擺工程.pdf');
mv('廁所搗擺隔間詳圖(總高2100,離地5cm)-Model.pdf', '20240604-祐明-導擺隔間施工詳圖.pdf');

console.log('\n目錄內容:');
fs.readdirSync(BASE).forEach(f => console.log(' ', f));
