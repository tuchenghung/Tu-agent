import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\Dropbox\宏祐\舊案件\羅東聖母醫院南澳日照中心\A業主提供資料\院方提供圖檔\1140801.dxf', encoding='utf-8', errors='replace') as f:
    content = f.read()

entities_start = content.find('ENTITIES\n')
entities_end = content.find('\nENDSEC', entities_start)
entities = content[entities_start:entities_end if entities_end > 0 else entities_start+2000000]

lines = entities.split('\n')
skip_keywords = ['$0$', 'AEC_', 'DISP_REP', '天花板材料', '二樓平面圖', '三樓平面圖', '全區圖', '新細明體', '細明體', '位置圖']

chinese_texts = []
for i, line in enumerate(lines):
    val = line.strip()
    if any('一' <= c <= '鿿' for c in val) or any('！' <= c <= '～' for c in val):
        skip = False
        for kw in skip_keywords:
            if kw in val:
                skip = True
                break
        if not skip:
            chinese_texts.append(val)

print(f'共找到 {len(chinese_texts)} 筆')
seen = set()
for t in chinese_texts:
    clean = re.sub(r'\\P', '\n  ', t)
    clean = re.sub(r'\\[A-Za-z][0-9.]+;', '', clean)
    clean = clean.replace('{', '').replace('}', '')
    if clean not in seen and len(clean) > 1:
        seen.add(clean)
        if len(clean) < 120:
            print(clean)
