# AutoCAD 平面圖轉 Blender 3D 踩坑紀錄

**案子**：訊龍潭廠 1F 門面裝修工程
**日期**：2026-06-06

---

## 流程摘要

DXF → Python(ezdxf) 轉 SVG → Blender 匯入 → 曲線擠出

---

## 踩坑清單

### 1. Blender 5.x 移除內建 DXF 匯入外掛
- **問題**：Blender 5.1.2 的附加元件裡找不到 DXF 匯入器
- **解法**：用 Python ezdxf 把 DXF 轉成 SVG，Blender 內建支援 SVG 匯入

### 2. SVG 單位換算錯誤（尺寸差 10 倍）
- **問題**：DXF 單位是 cm，直接輸出 SVG 數值，Blender 讀成 mm → 縮小 10 倍
- **解法**：SVG 輸出時所有座標 × 10（cm → mm），並在 width/height 加 `mm` 單位
  ```
  width="{W}mm" height="{H}mm"
  ```
- **不需要**在 Blender 手動縮放

### 3. 弧線（門的開關示意）被擠出成牆
- **問題**：(N)Door 圖層的 ARC 實體擠出後變成亂刺
- **解法**：SVG 轉換時排除 ARC/CIRCLE/SPLINE/ELLIPSE 類型

### 4. CAD 符號線（窗框叉號等）造成突刺
- **問題**：大量 < 10cm 的短線段被擠出成細刺
- **解法**：轉換時過濾 `長度 < 10cm` 的線段；窗戶/鐵捲門層用 `< 30cm`
- **數量**：2013 條 → 過濾後 442 條，突刺大幅減少

### 5. 窗戶/鐵捲門圖層沒有匯出到 for_blender.dxf
- **問題**：在 AutoCAD 分好圖層後，另存 DXF 時只存了牆和門，沒帶窗戶
- **解法**：確認窗戶圖層**可見（開啟）** → 另存新檔 → 選 DXF 格式（不是存 DWG）

### 6. Blender 5.x 材質節點名稱改變
- **問題**：`mat.node_tree.nodes["Principled BSDF"]` 找不到，KeyError
- **解法**：改用 type 查找：
  ```python
  bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
  ```

### 7. Blender 曲線擠出後 Z 高度是設定值的 2 倍
- **問題**：設擠出 3m，Z 尺寸顯示 6m（因為往兩個方向各擠 3m）
- **解法**：設擠出 `1.5`，實際總高度才是 3m

### 8. Blender 文字編輯器不會自動重載外部檔案
- **問題**：腳本更新後 Blender 還是跑舊版
- **解法**：文字 → 重新載入，或關掉重開

---

## 正確的 SVG 轉換腳本位置
```
K施工圖面/blender_setup.py  ← Blender 執行腳本（重建場景用）
```

## 輸出的 SVG 檔案
```
blender_wall.svg      ← 牆 + 門框（過濾 < 10cm）
blender_window.svg    ← 橫拉鋁窗（過濾 < 30cm）
blender_door.svg      ← 鐵捲門（過濾 < 30cm）
```

---

## 下次繼續
- [ ] 加地板（平面）
- [ ] 套材質：牆白、窗藍半透明、地板磁磚
- [ ] 加燈光（太陽燈）
- [ ] F12 渲染輸出示意圖給業主
