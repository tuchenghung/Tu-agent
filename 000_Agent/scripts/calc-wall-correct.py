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

total_length = 0
wall_count = 0
complex_walls = []

for e in msp:
    if e.dxf.layer != LAYER or e.dxftype() != 'LWPOLYLINE':
        continue

    pts = list(e.get_points())
    sides = []
    for i in range(len(pts)-1):
        dx = pts[i+1][0] - pts[i][0]
        dy = pts[i+1][1] - pts[i][1]
        sides.append(math.sqrt(dx**2 + dy**2))
    if e.is_closed:
        dx = pts[0][0] - pts[-1][0]
        dy = pts[0][1] - pts[-1][1]
        sides.append(math.sqrt(dx**2 + dy**2))

    sides_sorted = sorted(sides, reverse=True)

    if len(pts) == 4:
        # 標準矩形：取最長邊（長邊出現兩次，取其一）
        wall_len = sides_sorted[0]
        total_length += wall_len
        wall_count += 1
    else:
        # 非矩形（L型、T型等）：記錄下來，取最長邊近似
        complex_walls.append(sides_sorted)
        wall_len = sides_sorted[0] if sides_sorted else 0
        total_length += wall_len
        wall_count += 1

print(f"=== 輕質隔間牆 長度計算（取矩形長邊）===\n")
print(f"牆段總數：{wall_count} 段")
print(f"總長度：{total_length:.0f} 單位 = {total_length/100:.2f} m")
print(f"\n（圖面單位為 cm，換算後為公尺）")

if complex_walls:
    print(f"\n【複雜形狀牆段 {len(complex_walls)} 段，請人工確認】")
    for s in complex_walls:
        print(f"  各邊長: {[f'{x:.0f}' for x in s]}")
