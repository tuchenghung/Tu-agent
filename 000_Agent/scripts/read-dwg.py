# -*- coding: utf-8 -*-
import ezdxf
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

folder = r"D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\K施工圖面"

# 找最新的 dwg
dxf_files = [f for f in os.listdir(folder) if f.endswith('.dxf')]
dxf_files.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)

if not dxf_files:
    print("找不到 DXF 檔案")
    sys.exit(1)

filepath = os.path.join(folder, dxf_files[0])
print(f"讀取檔案: {dxf_files[0]}")
print(f"檔案大小: {os.path.getsize(filepath) / 1024 / 1024:.1f} MB\n")

try:
    doc = ezdxf.readfile(filepath)

    print("=== 圖層清單 ===")
    for layer in doc.layers:
        print(f"  - {layer.dxf.name}")

    print(f"\n=== 視圖/圖紙清單 ===")
    for layout in doc.layouts:
        print(f"  - {layout.name} | 物件數: {len(list(layout))}")

    print(f"\n=== 圖塊清單（前20個）===")
    count = 0
    for block in doc.blocks:
        if not block.name.startswith("*"):
            print(f"  - {block.name}")
            count += 1
            if count >= 20:
                print("  ...")
                break

    msp = doc.modelspace()
    entity_types = {}
    for e in msp:
        t = e.dxftype()
        entity_types[t] = entity_types.get(t, 0) + 1

    print(f"\n=== 模型空間物件統計 ===")
    for k, v in sorted(entity_types.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

except Exception as e:
    print(f"讀取錯誤: {e}")
