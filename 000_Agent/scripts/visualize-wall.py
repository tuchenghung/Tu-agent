# -*- coding: utf-8 -*-
import ezdxf
import os
import sys
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

folder = r"D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\K施工圖面"
dxf_files = sorted([f for f in os.listdir(folder) if f.endswith('.dxf')],
                   key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
doc = ezdxf.readfile(os.path.join(folder, dxf_files[0]))
msp = doc.modelspace()

fig, ax = plt.subplots(1, 1, figsize=(20, 16))
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

# 畫 C3-輕質隔間（紅色填滿）
wall_patches = []
for e in msp:
    if e.dxf.layer != 'C3-輕質隔間' or e.dxftype() != 'LWPOLYLINE':
        continue
    pts = [(p[0], p[1]) for p in e.get_points()]
    if len(pts) >= 3:
        poly = Polygon(pts, closed=True)
        wall_patches.append(poly)

pc = PatchCollection(wall_patches, facecolor='#e63946', edgecolor='#ff6b6b', linewidth=0.5, alpha=0.9)
ax.add_collection(pc)

# 畫 C2-RC牆（灰色）作為背景參考
rc_patches = []
for e in msp:
    if e.dxf.layer != 'C2-RC牆' or e.dxftype() != 'LWPOLYLINE':
        continue
    pts = [(p[0], p[1]) for p in e.get_points()]
    if len(pts) >= 3:
        poly = Polygon(pts, closed=True)
        rc_patches.append(poly)

if rc_patches:
    pc2 = PatchCollection(rc_patches, facecolor='#457b9d', edgecolor='#a8dadc', linewidth=0.5, alpha=0.7)
    ax.add_collection(pc2)

# 找密度最高的區域（用histogram找主要聚集點）
all_x, all_y = [], []
for e in msp:
    if e.dxf.layer != 'C3-輕質隔間' or e.dxftype() != 'LWPOLYLINE':
        continue
    for p in e.get_points():
        all_x.append(p[0])
        all_y.append(p[1])

if all_x:
    # 用25%~75%中位數區間找主圖
    x1, x2 = np.percentile(all_x, 10), np.percentile(all_x, 90)
    y1, y2 = np.percentile(all_y, 10), np.percentile(all_y, 90)
    pad_x = (x2 - x1) * 0.15
    pad_y = (y2 - y1) * 0.15
    ax.set_xlim(x1 - pad_x, x2 + pad_x)
    ax.set_ylim(y1 - pad_y, y2 + pad_y)

ax.set_aspect('equal')
ax.set_title('羅東聖母醫院 1F 中醫診所\n輕質隔間牆（紅色）vs RC牆（藍色）',
             color='white', fontsize=14, pad=15,
             fontproperties=matplotlib.font_manager.FontProperties(fname='C:/Windows/Fonts/msjh.ttc'))
ax.tick_params(colors='gray')
for spine in ax.spines.values():
    spine.set_edgecolor('#444')

# 加圖例
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#e63946', edgecolor='#ff6b6b', label=f'輕質隔間 (168段 / 257.81m)'),
    Patch(facecolor='#457b9d', edgecolor='#a8dadc', label='RC牆（參考）'),
]
ax.legend(handles=legend_elements, loc='upper right',
          facecolor='#2d2d44', edgecolor='#666', labelcolor='white',
          prop=matplotlib.font_manager.FontProperties(fname='C:/Windows/Fonts/msjh.ttc', size=11))

output = r"D:\Dropbox\Tu-agent\000_Agent\scripts\wall-preview.png"
plt.savefig(output, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
print(f"圖片已儲存：{output}")
