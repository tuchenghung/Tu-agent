import fs from 'fs';
import path from 'path';

const PROJECT_FOLDER = 'D:\\Dropbox\\宏祐\\20251104羅東聖母中醫診所規劃案';

// 找 P請購單 資料夾（可能有空格）
const caseItems = fs.readdirSync(PROJECT_FOLDER, { withFileTypes: true });
const pFolder = caseItems.find(d => d.isDirectory() && d.name.startsWith('P'));
if (!pFolder) { console.error('找不到 P請購單 資料夾'); process.exit(1); }

const P_DIR = path.join(PROJECT_FOLDER, pFolder.name);
console.error('P請購單路徑:', P_DIR);

const dirs = fs.readdirSync(P_DIR, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => ({ name: d.name, full: path.join(P_DIR, d.name) }))
  .sort((a, b) => b.name.localeCompare(a.name));

if (dirs.length === 0) { console.error('P請購單 資料夾內無子資料夾'); process.exit(1); }

console.log(JSON.stringify({ pDir: P_DIR, latest: dirs[0], all: dirs }));
