import fs from 'fs';
import path from 'path';

const PROJECT_FOLDER = 'D:\\Dropbox\\宏祐\\20260511羅東聖母醫院防火門維修案';
const ROOTS = ['D:\\Dropbox\\宏祐', 'D:\\Dropbox\\yushi'];

function getDateDirs(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter(d => d.isDirectory() && /^\d{8}/.test(d.name))
    .map(d => ({ name: d.name, full: path.join(dir, d.name) }))
    .sort((a, b) => b.name.localeCompare(a.name));
}

// 找 P請購單 資料夾（可能有空格，開頭為 P）
let P_DIR = null;
if (fs.existsSync(PROJECT_FOLDER)) {
  const pCandidate = fs.readdirSync(PROJECT_FOLDER, { withFileTypes: true })
    .find(d => d.isDirectory() && d.name.startsWith('P'));
  if (pCandidate) P_DIR = path.join(PROJECT_FOLDER, pCandidate.name);
}

let dirs = P_DIR ? getDateDirs(P_DIR) : [];
let crossProject = false;

// 若目前專案無 P請購單 或為空，跨專案掃描
if (dirs.length === 0) {
  console.error(P_DIR ? 'P請購單 無日期子資料夾' : '找不到 P請購單 資料夾', '→ 掃描其他專案...');
  const allDirs = [];
  for (const root of ROOTS) {
    if (!fs.existsSync(root)) continue;
    for (const proj of fs.readdirSync(root, { withFileTypes: true })) {
      if (!proj.isDirectory()) continue;
      const projPath = path.join(root, proj.name);
      try {
        for (const pf of fs.readdirSync(projPath, { withFileTypes: true })) {
          if (pf.isDirectory() && pf.name.startsWith('P')) {
            for (const d of getDateDirs(path.join(projPath, pf.name))) allDirs.push(d);
          }
        }
      } catch {}
    }
  }
  allDirs.sort((a, b) => b.name.localeCompare(a.name));
  if (allDirs.length === 0) { console.error('所有專案均無請購單範本'); process.exit(1); }
  dirs = allDirs;
  crossProject = true;
  console.error('跨專案找到範本：' + dirs[0].full);

  // 若本專案無 P請購單，建立它
  if (!P_DIR) {
    P_DIR = path.join(PROJECT_FOLDER, 'P請購單');
    fs.mkdirSync(P_DIR, { recursive: true });
    console.error('已建立 P請購單 資料夾：' + P_DIR);
  }
}

console.log(JSON.stringify({ pDir: P_DIR, latest: dirs[0], crossProject }));
