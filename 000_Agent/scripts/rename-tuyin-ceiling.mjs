import fs from 'fs';
import path from 'path';

const BASE = 'D:\\Dropbox\\宏祐\\舊案件\\土銀大樓裝修\\詢價資料\\輕鋼架';

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

mv('20240617台大天花板報價單(懷湘).pdf', '20240615-懷湘-天花板工程.pdf');
mv('20240529大樓廁所及樓梯間整修工程輕鋼架標單.pdf', '20240529-土銀大樓-天花板工程標單.pdf');

console.log('\n目錄內容:');
fs.readdirSync(BASE).forEach(f => console.log(' ', f));
