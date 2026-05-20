import fs from 'fs';
const ROOTS = ['D:\\Dropbox\\宏祐', 'D:\\Dropbox\\yushi'];
const keyword = process.argv[2];
const results = [];
for (const root of ROOTS) {
  if (!fs.existsSync(root)) continue;
  for (const d of fs.readdirSync(root, { withFileTypes: true })) {
    if (d.isDirectory() && d.name.includes(keyword)) {
      results.push({ root, name: d.name, full: root + '\\' + d.name });
    }
  }
}
console.log(JSON.stringify(results));
