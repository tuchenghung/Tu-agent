import { existsSync, readdirSync, mkdirSync } from 'fs';
import { join } from 'path';

const root = 'D:\\Dropbox\\宏祐\\規劃中案件';
console.log('root exists:', existsSync(root));

const dirs = readdirSync(root);
const match = dirs.filter(d => d.includes('和平') || d.includes('202605'));
console.log('和平/202605 資料夾:', JSON.stringify(match));

// Try known path
const proj = join(root, '202605-市醫和平院區醫療大樓8樓婦兒科病房整修');
console.log('proj exists:', existsSync(proj));

if (existsSync(proj)) {
  const p1 = join(proj, 'F供應商報價與資料', '廠商報價');
  const p2 = join(proj, '廠商報價');
  const fDir = join(proj, 'F供應商報價與資料');
  console.log('F廠商報價 exists:', existsSync(p1));
  console.log('廠商報價 exists:', existsSync(p2));
  if (existsSync(fDir)) {
    console.log('F資料夾內容:', JSON.stringify(readdirSync(fDir)));
  }
  // Create if needed
  if (!existsSync(p1)) {
    mkdirSync(p1, { recursive: true });
    console.log('已建立:', p1);
  }
  console.log('DEST:', p1);
}
