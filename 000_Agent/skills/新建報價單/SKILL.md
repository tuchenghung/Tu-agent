---
name: 新建報價單
description: "從 Excel 範本新建宏祐集團工程報價單：選擇格式 → 收集案件資訊 → 複製範本到 D預算報價/ → 填入表頭 placeholder → 開啟 Excel。觸發方式：/新建報價單"
---

# 新建報價單 Skill

觸發方式：`/新建報價單`

---

## 平台

**僅支援 Windows**（win32com 依賴 Excel COM）。

```
NODE = C:\Users\deco01\nodejs\node.exe
TEMPLATE_小型 = D:\Dropbox\Tu-agent\000_Agent\templates\報價單範本.xlsx
TEMPLATE_中型 = D:\Dropbox\Tu-agent\000_Agent\templates\報價單範本_中型.xlsx
TEMPLATE_大型 = D:\Dropbox\Tu-agent\000_Agent\templates\報價單範本_大型.xlsx
```

---

## STEP 1：收集必要資訊

用 **AskUserQuestion** 一次詢問以下 **4 個問題**（questions 陣列並排）：

```
問題1：報價單規模？
  header: "工程規模"
  options:
    - label: "小型（100萬以下）"
      description: "品項少，單層直列，A-M 13欄，~20列"
    - label: "中型（100~1000萬）"
      description: "多工種，摘要+明細雙層，甲/乙費用分類，A-N 14欄，200+列"
    - label: "大型（1000萬以上）"
      description: "複雜統包工程，格式待有案例補充"

問題2：集團？
  header: "集團"
  options:
    - label: "宏祐"
    - label: "yushi"

問題3：案件名稱
  → 完整工程名稱（對應 R4F PROJECT）
  → 另取簡稱：去掉「工程」「建置」後綴，保留地點+主體（對應 R3A）

問題4：工程地點、業主名稱、工程編號（可留空）
```

### 規模 → 範本對照

| 規模 | 格式代號 | 範本路徑 | 工作表名 |
|------|----------|----------|----------|
| 小型 | `小型` | `templates\報價單範本.xlsx` | 報價單 |
| 中型 | `中型` | `templates\報價單範本_中型.xlsx` | 工程簡稱（如「耳鼻喉科」） |
| 大型 | `大型` | `templates\報價單範本_大型.xlsx` | 工程簡稱 |

---

## STEP 2：找到案件 D預算報價 資料夾

寫入腳本到 `D:\Dropbox\Tu-agent\000_Agent\scripts\find_case_folder.mjs` 再執行：

```js
import fs from 'fs';
import path from 'path';

const ROOTS = {
  '宏祐': 'D:\\Dropbox\\宏祐\\規劃中案件',
  'yushi': 'D:\\Dropbox\\yushi\\規劃中案件'
};

const GROUP = '{{集團}}';      // 替換為 宏祐 或 yushi
const KEYWORD = '{{關鍵字}}';  // 取案件名稱前4~6字（去除常見前綴）

const root = ROOTS[GROUP];
const dirs = fs.readdirSync(root, { withFileTypes: true })
  .filter(d => d.isDirectory() && d.name.includes(KEYWORD))
  .map(d => d.name);

console.log(JSON.stringify(dirs));
```

- 找到唯一符合 → 記下 `$PROJECT_DIR = {案件資料夾}/D預算報價`
- 找到多個 → **AskUserQuestion** 讓使用者選擇
- 找不到 → 告知使用者確認案件資料夾名稱，或問是否要新建

`D預算報價` 不存在時自動建立：
```js
const dest = path.join(caseDir, 'D預算報價');
if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
```

---

## STEP 3：複製範本

新檔名格式：`YYYYMMDD-{案件名稱簡稱}.xlsx`
- 日期：今日（西元，8碼）
- 案件名稱簡稱：取前 12 字，去掉「工程」「建置」等後綴

**根據 STEP 1 選擇的格式決定範本來源：**

```python
import shutil, os
from datetime import date

# 根據格式選擇範本
FORMAT = '{{報價單格式}}'  # '小型工程' 或 '大型工程'

TEMPLATES = {
    '小型': (r'D:\Dropbox\Tu-agent\000_Agent\templates\報價單範本.xlsx', '報價單'),
    '中型': (r'D:\Dropbox\Tu-agent\000_Agent\templates\報價單範本_中型.xlsx', '{{工程簡稱}}'),
    '大型': (r'D:\Dropbox\Tu-agent\000_Agent\templates\報價單範本_大型.xlsx', '{{工程簡稱}}'),
}

FORMAT = '{{格式}}'  # 小型 / 中型 / 大型
src, SHEET_NAME = TEMPLATES[FORMAT]

if not os.path.exists(src):
    print(f'ERROR: {FORMAT}範本不存在：{src}')
    print('請先儲存一份乾淨版 Excel 作為範本至上述路徑。')
    exit(1)

filename = f'{date.today().strftime("%Y%m%d")}-{{案件簡稱}}.xlsx'
dst = os.path.join(r'{{$PROJECT_DIR}}', filename)
shutil.copy2(src, dst)
print(dst)
```

> ⚠️ **中型/大型範本尚未建立時**：告知使用者需先手動儲存一份乾淨版 Excel 作為範本：
> - 中型：`templates\報價單範本_中型.xlsx`（來源：耳鼻喉科 V3 格式，清空數值後儲存）
> - 大型：`templates\報價單範本_大型.xlsx`（1000萬+案例，有案例後補充）

---

## STEP 4：填入表頭（win32com）

**ONLY write to header cells. 絕對不改任何格式、列高、欄寬、WrapText。**

```python
import win32com.client, os

file_path = r'{{$OUTPUT_PATH}}'
FORMAT = '{{格式}}'  # '小型' / '中型' / '大型'
SHEET_NAME = '報價單' if FORMAT == '小型' else '{{工程簡稱}}'

replacements = {
    '{{工程名稱}}': '{{工程名稱}}',   # 完整工程名稱
    '{{業主名稱}}': '{{業主名稱}}',
    '{{工程地點}}': '{{工程地點}}',
    '{{工程編號}}': '{{工程編號}}',   # 若空白則填 ''
}

excel = win32com.client.Dispatch('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False
wb = excel.Workbooks.Open(os.path.abspath(file_path))
ws = wb.Sheets(SHEET_NAME)

# 掃描所有 placeholder 格子並替換值
used = ws.UsedRange
for row in range(used.Row, used.Row + used.Rows.Count):
    for col in range(used.Column, used.Column + used.Columns.Count):
        cell = ws.Cells(row, col)
        val = str(cell.Value or '')
        for placeholder, actual in replacements.items():
            if placeholder in val:
                cell.Value = val.replace(placeholder, actual)
                break  # 一格只有一個 placeholder

wb.Save()
wb.Close(False)
excel.Quit()
print('Done')
```

> 特別注意：
> - R3A 可能是 merged cell，直接對 R3C1 寫值即可（win32com 會處理 merge）
> - 工程編號若空白 → 寫入 '' 清空 placeholder，不留 `{{工程編號}}`
> - 大型格式工作表名稱 = 工程簡稱（如「耳鼻喉科」），非「報價單」

---

## STEP 5：開啟 Excel

```python
import os, subprocess
subprocess.Popen(['explorer', r'{{$OUTPUT_PATH}}'])
```

---

## STEP 6：回報

```
✅ 報價單已建立

📁 路徑：{$OUTPUT_PATH}
🏗️ 工程：{工程名稱}
🏢 業主：{業主名稱}
📍 地點：{工程地點}

Excel 已開啟，請填入品項內容。
```

---

## 重要規則

1. **NEVER 修改格式**：只填值，不動字體、列高、欄寬、WrapText、顏色
2. **NEVER AutoFit**：列高是手動設定的，不可 AutoFit
3. 範本路徑固定：`D:\Dropbox\Tu-agent\000_Agent\templates\報價單範本.xlsx`
4. 工程編號若使用者留空 → 清空 placeholder 即可，不要留 `{{}}`
5. 填完後立刻開啟 Excel，讓使用者直接編輯品項
