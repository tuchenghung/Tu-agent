# -*- coding: utf-8 -*-
import ezdxf
import os
import sys
import math
sys.stdout.reconfigure(encoding='utf-8')

folder = r"D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\K施工圖面"
dxf_files = [f for f in os.listdir(folder) if f.endswith('.dxf')]
dxf_files.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
filepath = os.path.join(folder, dxf_files[0])

doc = ezdxf.readfile(filepath)
msp = doc.modelspace()

TARGET_LAYER = "C3-輕質隔間_dim"

print(f"=== 圖層：{TARGET_LAYER} ===\n")

# 從 _dim 圖層抓 DIMENSION 標注數值
dim_values = []
print("【標注尺寸清單】")
for e in msp.query(f'DIMENSION[layer=="{TARGET_LAYER}"]'):
    try:
        val = e.dxf.actual_measurement
        if val and val > 0:
            dim_values.append(val)
            print(f"  {val:.0f} mm")
    except:
        pass

if dim_values:
    total = sum(dim_values)
    print(f"\n標注筆數：{len(dim_values)} 筆")
    print(f"標注總長：{total:.0f} mm = {total/1000:.2f} m")
else:
    print("  此圖層無 DIMENSION 標注")

# 也從 C3-輕質隔間 圖層算幾何長度
WALL_LAYER = "C3-輕質隔間"
print(f"\n=== 圖層：{WALL_LAYER}（實際牆線幾何長度）===\n")

total_geo = 0
count = 0

for e in msp:
    if e.dxf.layer != WALL_LAYER:
        continue
    t = e.dxftype()
    try:
        if t == 'LINE':
            s = e.dxf.start
            end = e.dxf.end
            length = math.sqrt((end.x-s.x)**2 + (end.y-s.y)**2)
            total_geo += length
            count += 1
        elif t == 'LWPOLYLINE':
            pts = list(e.get_points())
            for i in range(len(pts)-1):
                dx = pts[i+1][0] - pts[i][0]
                dy = pts[i+1][1] - pts[i][1]
                total_geo += math.sqrt(dx**2 + dy**2)
            if e.is_closed and len(pts) > 1:
                dx = pts[0][0] - pts[-1][0]
                dy = pts[0][1] - pts[-1][1]
                total_geo += math.sqrt(dx**2 + dy**2)
            count += 1
    except Exception as ex:
        pass

print(f"物件數：{count} 個")
print(f"幾何總長：{total_geo:.0f} mm = {total_geo/1000:.2f} m")
