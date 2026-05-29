# -*- coding: utf-8 -*-
import ezdxf, os, sys, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

folder = r"D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\K施工圖面"
dxf_files = sorted([f for f in os.listdir(folder) if f.endswith('.dxf')],
                   key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
doc = ezdxf.readfile(os.path.join(folder, dxf_files[0]))
msp = doc.modelspace()

# 只取主平面圖區域（Y > -2000）
Y_MIN = -2000

fig, ax = plt.subplots(figsize=(22, 14))
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

wall_patches, wall_count, total_len = [], 0, 0
rc_patches = []

for e in msp:
    if e.dxftype() != 'LWPOLYLINE':
        continue
    pts = [(p[0], p[1]) for p in e.get_points()]
    if not pts:
        continue
    cy = sum(p[1] for p in pts) / len(pts)
    if cy < Y_MIN:
        continue

    if e.dxf.layer == 'C3-輕質隔間' and e.dxftype() == 'LWPOLYLINE' and len(pts) >= 3:
        # 計算長邊
        sides = []
        for i in range(len(pts)-1):
            dx = pts[i+1][0]-pts[i][0]; dy = pts[i+1][1]-pts[i][1]
            sides.append(math.sqrt(dx**2+dy**2))
        dx = pts[0][0]-pts[-1][0]; dy = pts[0][1]-pts[-1][1]
        if e.is_closed: sides.append(math.sqrt(dx**2+dy**2))
        sides.sort(reverse=True)
        total_len += sides[0]
        wall_count += 1
        wall_patches.append(Polygon(pts, closed=True))

    elif e.dxf.layer == 'C2-RC牆' and e.dxftype() == 'LWPOLYLINE' and len(pts) >= 3:
        rc_patches.append(Polygon(pts, closed=True))

if rc_patches:
    ax.add_collection(PatchCollection(rc_patches, facecolor='#457b9d', edgecolor='#a8dadc', linewidth=0.5, alpha=0.6))
if wall_patches:
    ax.add_collection(PatchCollection(wall_patches, facecolor='#e63946', edgecolor='#ff6b6b', linewidth=0.8, alpha=0.95))

ax.autoscale()
ax.set_aspect('equal')

font = matplotlib.font_manager.FontProperties(fname='C:/Windows/Fonts/msjh.ttc')
ax.set_title(f'羅東聖母醫院 1F 中醫診所 — 主平面圖\n輕質隔間（紅）{wall_count}段 / {total_len/100:.2f}m  ｜  RC牆（藍）',
             color='white', fontsize=13, pad=12, fontproperties=font)
ax.tick_params(colors='gray')

from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(facecolor='#e63946', edgecolor='#ff6b6b', label=f'輕質隔間  {wall_count}段 / {total_len/100:.2f} m'),
    Patch(facecolor='#457b9d', edgecolor='#a8dadc', label='RC牆（參考）'),
], facecolor='#2d2d44', edgecolor='#666', labelcolor='white',
   prop=matplotlib.font_manager.FontProperties(fname='C:/Windows/Fonts/msjh.ttc', size=11),
   loc='upper right')

output = r"D:\Dropbox\Tu-agent\000_Agent\scripts\wall-preview.png"
plt.savefig(output, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
print(f"主平面圖牆段：{wall_count} 段，總長：{total_len/100:.2f} m")
print(f"圖片：{output}")
