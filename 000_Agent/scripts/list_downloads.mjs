import fs from 'fs';
import path from 'path';

const dir = 'C:\\Users\\deco01\\Downloads';
const exts = new Set(['.jpg', '.jpeg', '.png', '.pdf', '.xls', '.xlsx']);

const files = fs.readdirSync(dir, { withFileTypes: true })
  .filter(f => f.isFile() && exts.has(path.extname(f.name).toLowerCase()))
  .map(f => {
    const s = fs.statSync(path.join(dir, f.name));
    return { name: f.name, mtime: s.mtime, full: path.join(dir, f.name) };
  })
  .sort((a, b) => b.mtime - a.mtime)
  .slice(0, 10);

files.forEach(f => console.log(f.mtime.toISOString().slice(0, 16).replace('T', ' ') + '  ' + f.name));
