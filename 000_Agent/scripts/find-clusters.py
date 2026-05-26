# -*- coding: utf-8 -*-
import ezdxf, os, sys, math
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

folder = r"D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\K施工圖面"
dxf_files = sorted([f for f in os.listdir(folder) if f.endswith('.dxf')],
                   key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
doc = ezdxf.readfile(os.path.join(folder, dxf_files[0]))
msp = doc.modelspace()

all_x, all_y = [], []
for e in msp:
    if e.dxf.layer != 'C3-輕質隔間' or e.dxftype() != 'LWPOLYLINE':
        continue
    for p in e.get_points():
        all_x.append(p[0])
        all_y.append(p[1])

print(f"X 範圍: {min(all_x):.0f} ~ {max(all_x):.0f}")
print(f"Y 範圍: {min(all_y):.0f} ~ {max(all_y):.0f}")

# 用 Y 分群（每 2000 單位一桶）
y_arr = np.array(all_y)
bins = np.arange(min(all_y)-100, max(all_y)+100, 2000)
counts, edges = np.histogram(y_arr, bins=bins)
print("\nY 軸分布（每 2000cm 一格）：")
for i, c in enumerate(counts):
    if c > 0:
        print(f"  Y {edges[i]:.0f} ~ {edges[i+1]:.0f} : {c} 個點")
