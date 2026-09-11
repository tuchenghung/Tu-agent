from pathlib import Path
import json,hashlib,openpyxl,re,collections,copy
base=Path(__file__).parent
sources=json.loads((base/'sources.json').read_text(encoding='utf-8'))
configs=[('xinghe8','8F裝修工程 ',38,163,'病房整修'),('xinghe37','3、7F裝修工程',39,252,'門診與復健整修'),('mary5','耳鼻喉科',35,150,'耳鼻喉科整修'),('mary8','8F預算V5',39,151,'戒護病房整修'),('museum','靈醫會史蹟館',38,161,'史蹟館展示空間'),('xinghe37','大樓消防灑水泵浦工程',9,13,'大樓灑水泵浦')]
templates=[]; audit=[]
for ti,(sid,sheet,start,end,title) in enumerate(configs):
 src=next(s for s in sources if s['id']==sid)
 assert hashlib.sha256(Path(src['path']).read_bytes()).hexdigest()==src['sha256']
 w=openpyxl.load_workbook(src['path'],read_only=True,data_only=False); s=w[sheet]
 rows=list(s.iter_rows(values_only=True)); chapters=[]; cmap={}; tops={}; top=''; sub=''; prev=None
 def add(chname,r,kind):
  nonlocal_dummy=None
  a,b,c,*_=rows[r-1]; name=str(b).strip()
  remark=rows[r-1][6] if len(rows[r-1])>6 else None
  if remark and not str(remark).startswith('=') and str(remark)!='約457坪': name+='\n備註：'+str(remark).strip()
  if chname not in cmap:
   ch=dict(id=f'{sid}-{ti}-ch{len(chapters)+1}',name=chname,items=[]); cmap[chname]=ch; chapters.append(ch)
  item=dict(id=f'{sid}-{ti}-r{r}',name=name,unit=str(c).strip(),sourceSheet=sheet,sourceRow=r,originalItemNo=str(a).strip(),kind=kind)
  item['sourceRefs']=[dict(sourceId=sid,sourceSheet=sheet,sourceRow=r,originalItemNo=str(a).strip())]
  cmap[chname]['items'].append(item); return item
 for r,row in enumerate(rows[:start-1],1):
  a,b,c=row[:3]
  if str(a).startswith('甲.') and b and c: tops[str(a).strip().rstrip('.')]=str(b).strip()
 for r in range(start,end+1):
  row=rows[r-1]; a,b,c=row[:3]; a=str(a).strip().rstrip('.') if a is not None else ''; b=str(b).strip() if b is not None else ''
  if not b or '小計' in b or not a.startswith('甲') and ti!=5:
   # Only bare specification continuation adjacent to a detail gets joined.
   if b and not a and not c and prev and r==prev.get('_last',prev['sourceRow'])+1 and not any(x in b for x in ['小計','總計','合計','稅金']):
    prev['name']+='\n'+b; prev['_last']=r
   else: prev=None
   continue
  if not c:
   parts=a.split('.')
   if len(parts)<=2: top=b; sub=''
   else:
    inferred=tops.get('.'.join(parts[:2]),top)
    top=inferred; sub='' if b==top else b
   prev=None; continue
  if ti==5: chname='大樓消防灑水泵浦工程'
  elif sid=='mary8' and r==142: chname='氣體工程'
  else:
   # Priced two-level / three-level Chinese item rows are genuine lump-sum items, not headings.
   parts=a.split('.')
   standalone=len(parts)==3 and not re.search(r'\d',parts[-1])
   chname=top if standalone else top+('／'+sub if sub else '')
  assert chname,(sid,r)
  prev=add(chname,r,'direct')
 for r in range(9,start):
  row=rows[r-1]; a,b,c=row[:3]
  if a and str(a).startswith('乙.') and b and c:
   if sid=='mary5' and r==26: audit.append('耳鼻喉科第22與26列均為工程保險；範本只保留第22列，避免重複選入。'); continue
   add('間接工程費',r,'indirect')
 for ch in chapters:
  for item in ch['items']: item.pop('_last',None)
 templates.append(dict(id=f'{sid}-{ti}',name=title,sourceId=sid,chapters=chapters))
 w.close()
groups=collections.defaultdict(list)
for t in templates[:5]:
 for ch in t['chapters']:
  for item in ch['items']:
   groups[(item['name'],item['unit'],item['kind'],ch['name'])].append(item)
common_ch=[]; common_map={}; common=[]
for (name,unit,kind,chapter),items in groups.items():
 refs=[r for i in items for r in i['sourceRefs']]; ids=list(dict.fromkeys(r['sourceId'] for r in refs))
 if len(ids)<2: continue
 if chapter not in common_map:
  ch=dict(id=f'common-ch{len(common_ch)+1}',name=chapter,items=[]); common_map[chapter]=ch; common_ch.append(ch)
 i=copy.deepcopy(items[0]); i['id']=f'common-r{len(common)+1}'; i['sourceRefs']=refs; common_map[chapter]['items'].append(i)
 common.append(dict(name=name,occurrences=len(ids),sourceIds=ids))
templates.insert(0,dict(id='medical-common',name='醫療整修共用架構',sourceId='cross-source',chapters=common_ch))
result=dict(sources=sources,templates=templates,common=common)
assert all(hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256'] for s in sources)
ids=[i['id'] for t in templates for c in t['chapters'] for i in c['items']]; assert len(ids)==len(set(ids))
out=base.parent/'2026-09-11_quote-patterns.json'; out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
stats=[dict(name=t['name'],chapters=len(t['chapters']),items=sum(len(c['items']) for c in t['chapters'])) for t in templates]
print(json.dumps(stats,ensure_ascii=False,indent=2))
(base/'stats.json').write_text(json.dumps(stats,ensure_ascii=False),encoding='utf-8')
