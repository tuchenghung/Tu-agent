import fs from 'fs';
import path from 'path';

const SRC = 'C:\\Users\\deco01\\Downloads\\549482.jpg';
const VENDOR_DIR = 'D:\\Dropbox\\宏祐\\20260511羅東聖母醫院防火門維修案\\P請購單\\20260520防火門維修請購單\\廠商報價';
const NEW_NAME = '20260511-鼎堅工業-鐵工工程.jpg';
const DST = path.join(VENDOR_DIR, NEW_NAME);

fs.copyFileSync(SRC, DST);
console.log(JSON.stringify({ quotePath: DST }));
console.error('✅ 報價單已複製：' + DST);
