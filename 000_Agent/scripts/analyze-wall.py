# -*- coding: utf-8 -*-
import ezdxf
import os
import sys
import math
sys.stdout.reconfigure(encoding='utf-8')

folder = r"D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\K施工圖面"
dxf_files = sorted([f for f in os.listdir(folder) if f.endswith('.dxf')],
                   key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
doc = ezdxf.readfile(os.path.join(folder, dxf_files[0]))
msp = doc.modelspace()

LAYER = "C3-輕質隔間"
print(f"=== 圖層 {LAYER} 物件分析 ===\n")

type_count = {}
for e in msp:
    if e.dxf.layer != LAYER:
        continue
    t = e.dxftype()
    type_count[t] = type_count.get(t, 0) + 1

print("物件類型統計：")
for k, v in type_count.items():
    print(f"  {k}: {v} 個")

# 取前10個 LWPOLYLINE 看點數與尺寸
print("\n前10個 LWPOLYLINE 詳細資料：")
count = 0
for e in msp:
    if e.dxf.layer != LAYER or e.dxftype() != 'LWPOLYLINE':
        continue
    pts = list(e.get_points())
    n = len(pts)

    # 計算各邊長度
    sides = []
    for i in range(len(pts)-1):
        dx = pts[i+1][0] - pts[i][0]
        dy = pts[i+1][1] - pts[i][1]
        sides.append(math.sqrt(dx**2 + dy**2))
    if e.is_closed and len(pts) > 1:
        dx = pts[0][0] - pts[-1][0]
        dy = pts[0][1] - pts[-1][1]
        sides.append(math.sqrt(dx**2 + dy**2))

    sides_sorted = sorted(sides, reverse=True)
    print(f"  頂點數: {n} | 封閉: {e.is_closed} | 各邊長(mm): {[f'{s:.0f}' for s in sides_sorted]}")
    count += 1
    if count >= 10:
        break
