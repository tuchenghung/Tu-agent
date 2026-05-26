import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\Dropbox\宏祐\已完成案件\羅東聖母正子\K施工圖面\20241211-正子中心建置_第1包結構補強工程__第2包屏蔽裝修工程-鉛材料施工數量計算圖V8.dxf', encoding='utf-8', errors='replace') as f:
    content = f.read()

entities_start = content.find('ENTITIES\n')
entities_end = content.find('\nENDSEC', entities_start)
entities = content[entities_start:entities_end if entities_end > 0 else entities_start+3000000]

lines = entities.split('\n')
skip_keywords = ['$0$', 'AEC_', 'DISP_REP', '天花板材料', '新細明體', '細明體', 'barricade', 'laflt', 'TWPRGE', 'grail']

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

seen = set()
count = 0
for t in chinese_texts:
    clean = re.sub(r'\\P', '\n  ', t)
    clean = re.sub(r'\\[A-Za-z][0-9.;]+', '', clean)
    clean = clean.replace('{', '').replace('}', '').strip()
    if clean and clean not in seen and len(clean) > 1 and len(clean) < 120:
        seen.add(clean)
        print(clean)
        count += 1
        if count >= 200:
            break
