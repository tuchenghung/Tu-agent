from pathlib import Path
import json,hashlib,openpyxl
root=Path('D:/Dropbox/宏祐/規劃中案件')
specs=[('xinghe8','杏和醫院8F病房','20260723-*V3.xlsx'),('xinghe37','杏和醫院3F門診及7F復健','20260306-*V7.xlsx'),('mary5','聖母醫院5F耳鼻喉科','20260626-*.xlsx'),('mary8','聖母醫院8F戒護病房','20260504-*V4.xlsx'),('museum','靈醫會史蹟館','20260830-*.xlsx')]
out=Path(__file__).parent
sources=[]
for sid,label,pattern in specs:
 paths=[p for p in root.rglob(pattern) if ('杏和' in str(p) if sid.startswith('xinghe') else '羅東聖母醫院' in str(p))]
 if sid=='xinghe8': paths=[p for p in paths if p.parent.name=='業主報價']
 assert len(paths)==1, paths
 p=paths[0]; h=hashlib.sha256(p.read_bytes()).hexdigest(); w=openpyxl.load_workbook(p,read_only=True,data_only=False)
 sources.append(dict(id=sid,label=label,path=p.as_posix(),sha256=h,sheets=w.sheetnames))
 lines=[]
 for s in w:
  lines.append(f'=== {s.title} ({s.max_row}x{s.max_column}) ===')
  for row in s.iter_rows():
   values=['%s:%s'%(c.column_letter,str(c.value).replace('\n',' / ')) for c in row[:12] if c.value is not None]
   if values: lines.append(f'{row[0].row} '+' | '.join(values))
 (out/f'{sid}.txt').write_text('\n'.join(lines),encoding='utf-8')
 w.close()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
(out/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(sources,ensure_ascii=False,indent=2))
