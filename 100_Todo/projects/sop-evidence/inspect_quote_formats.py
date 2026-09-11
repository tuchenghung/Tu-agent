import json,sys,zipfile,hashlib,struct
from pathlib import Path
import openpyxl
sys.path.insert(0,'C:/Users/deco01/.codex/visualizations/2026/09/11/01a08de3-6096-7b41-902f-f01a284d91b6/xls-reader')
import xlrd
p=Path('D:/Dropbox/宏祐/規劃中案件/礁溪杏和醫院/20260818-礁溪杏和醫院8F病房整修工程/D預算報價/業主報價/20260723-礁溪杏和醫院8F病房整修工程整修工程V3.xlsx')
q=Path('D:/Dropbox/yushi/施工中案件/20251118南港實驗室GTP實驗室修改工程/D預算報價/20260426南港實驗室GTP實驗室修改工程.xls')
out=Path(__file__).parent
w=openpyxl.load_workbook(p);s=w.worksheets[0]
def cell(c):
 return dict(value=c.value,font=dict(name=c.font.name,size=c.font.sz,bold=c.font.b),alignment=dict(horizontal=c.alignment.horizontal,vertical=c.alignment.vertical,wrap=c.alignment.wrap_text),numberFormat=c.number_format,border={k:getattr(c.border,k).style for k in ['top','bottom','left','right']})
m=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sheet=s.title,columns={k:dict(width=v.width,hidden=v.hidden) for k,v in s.column_dimensions.items()},rowHeights={str(k):v.height for k,v in s.row_dimensions.items() if v.height},merges=list(map(str,s.merged_cells.ranges)),printArea=str(s.print_area),printTitles=s.print_title_rows,pageSetup=str(s.page_setup),margins=str(s.page_margins),printOptions=str(s.print_options),headerFooter=str(s.HeaderFooter),cells={a:cell(s[a]) for a in ['A1','A2','A3','C3','F3','A7','B7','D8','B9','B10','E10','F10','F26','F27','F28','F29','B30','B36','B37']})
with zipfile.ZipFile(p) as z:
 m['media']=[]
 for n in z.namelist():
  if n.startswith('xl/media/'):
   t=out/('macro-reference-'+Path(n).name);t.write_bytes(z.read(n));m['media'].append(dict(archivePath=n,extractedPath=str(t),bytes=len(z.read(n))))
 m['drawingXml']={n:z.read(n).decode() for n in z.namelist() if n.startswith('xl/drawings/') and n.endswith('.xml')}
x=xlrd.open_workbook(q,formatting_info=True);t=x.sheet_by_name('報價')
def xcell(r,c):
 a=t.cell(r-1,c-1);xf=x.xf_list[a.xf_index];f=x.font_list[xf.font_index]
 return dict(value=a.value,font=dict(name=f.name,heightTwips=f.height,bold=f.bold),alignment=vars(xf.alignment),border=vars(xf.border),numberFormat=x.format_map[xf.format_key].format_str)
y=dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),sheet=t.name,columns={str(k+1):vars(v) for k,v in t.colinfo_map.items()},rowInfo={str(k+1):vars(v) for k,v in t.rowinfo_map.items()},merges=t.merged_cells,cells={f'{r},{c}':xcell(r,c) for r,c in [(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(6,7),(7,1),(7,2),(8,2),(9,2),(9,3),(9,5),(9,6),(71,6),(72,6),(73,6),(74,2)]},names=[dict(name=n.name,formula=n.raw_formula.hex()) for n in x.name_obj_list])
# Read-only BIFF record scan for print setup and embedded drawing presence.
from xlrd.compdoc import CompDoc
c=CompDoc(q.read_bytes());b=c.get_named_stream('Workbook') or c.get_named_stream('Book')
records=[];pos=0;sheetIndex=-1
while pos+4<=len(b):
 op,ln=struct.unpack_from('<HH',b,pos);d=b[pos+4:pos+4+ln];pos+=4+ln
 if op==0x0809 and len(d)>=4 and struct.unpack_from('<H',d,2)[0]==0x10:sheetIndex+=1
 if sheetIndex==0 and op in [0x14,0x15,0x26,0x27,0x28,0x29,0xA1,0x83,0x84,0xE0,0xEC,0xEB,0xED,0x5D]:
  if op!=0xE0:records.append(dict(op=hex(op),length=ln,hex=d.hex() if op not in [0xEC,0xEB,0xED,0x5D] else 'drawing/object payload omitted'))
y['printAndDrawingRecords']=records
result=dict(macro=m,yashi=y,conversion=dict(excelRegistryPath='C:/Program Files/Microsoft Office/Root/Office16/EXCEL.EXE',libreOfficeFound=False,nativeConversionNotAttempted=True))
m['columns']={k:v for k,v in m['columns'].items() if k in list('ABCDEFGHIJ')}
y['rowInfo']={str(k+1):{'heightTwips':v.height,'hidden':v.hidden} for k,v in t.rowinfo_map.items()}
y['decodedPrint']={'printArea':'A1:G77','repeatRows':'1:7','paper':'A4','orientation':'portrait','scale':100,'fitWidth':1,'fitHeight':1,'fitModeVerified':False,'margins':{x['op']:struct.unpack('<d',bytes.fromhex(x['hex']))[0] for x in records if x['op'] in ['0x26','0x27','0x28','0x29']},'headerMargin':0.31496062992125984,'footerMargin':0.31496062992125984}
(out/'2026-09-11_quote-format-spec.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding='utf8')
print(json.dumps({'output':'2026-09-11_quote-format-spec.json','yashiRowHeights':{k:v for k,v in y['rowInfo'].items() if int(k)<12}},ensure_ascii=False))
