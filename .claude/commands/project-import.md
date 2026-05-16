# 工程專案資料夾匯入

收到 Dropbox 專案資料夾路徑後，自動完成：
1. 掃描現有檔案
2. 依 A-I 分類建立 Dropbox 資料夾並移檔
3. 在 Notion Projects 資料庫建立新專案頁面（若尚未存在）
4. 建立 A-I 折疊標題並填入檔案清單備忘

觸發方式：
- 使用者提供 Dropbox 資料夾路徑（如 `D:\Dropbox\宏祐\202605-XXX工程`）
- 或直接輸入 `/project-import`

---

## 標準分類規則（A-I）

| 分類 | 說明 | 歸入判斷 |
|---|---|---|
| A 業主提供資料 | 業主/建築師提供的原始圖面、底圖、規範 | XREF 底圖、建築圖號（A/B/C 系列）DWG、PDF 規範 |
| B 規劃圖面 | 我方自行繪製的施工規劃圖 | 自行產出的 DWG，含版本號如 T0/T1/T2 |
| C 簡報資料 | 簡報、提案、RUN DOWN 腳本 | .pptx、.pdf 簡報 |
| D 預算報價 | 我方發出的詢價單、預算總表 | 詢價單 .xlsx，含版本（W0/V1/V2） |
| E 業主合同資料 | 業主招標文件、合約書、驗收文件 | 招標規範、合約 .pdf/.docx |
| F 供應商報價與資料 | 廠商/分包商報價單、標單、詢價包 | 廠商報價資料夾、詢價資料/木作/鐵工/系統櫃 |
| G 進度計畫管理 | 施工進度表、甘特圖 | .xlsx 進度表、.mpp |
| H 照片 | 現場勘查照、施工紀錄照 | .jpg/.png 照片，依日期子資料夾 |
| I 其他 | 不屬於以上分類 | plot.log、暫存、雜項 |

**特殊規則：**
- `.dwl` / `.dwl2`：AutoCAD lock 暫存，直接刪除
- `.bak`：AutoCAD 備份，移入同層的 `old/` 資料夾
- 已有子資料夾分類（如`廠商報價/`、`詢價資料/`）：整包移入對應分類，不拆散

---

## 執行步驟

### Step 0：取得路徑與平台

```bash
uname -s 2>/dev/null || echo Windows
```
- Windows → 使用 `mcp__notion-win__`
- Mac → 使用 `mcp__notion__`

從使用者訊息取得 Dropbox 資料夾路徑，存為 `$BASE`。

---

### Step 1：掃描資料夾

```bash
find "$BASE" -print 2>/dev/null | sort
```

分析檔案清單，依 A-I 規則判斷每個檔案/資料夾的歸屬。
整理出：
- 哪些分類有檔案（列出檔案清單）
- 哪些分類是空的（標記「尚無資料」）
- 是否有 `.dwl`/`.dwl2`/`.bak` 需要清理

---

### Step 2：建立 Dropbox A-I 資料夾並移檔

**若 Dropbox 根目錄尚無 A-I 資料夾則建立：**
```bash
BASE="$DROPBOX_PATH"
for folder in "A業主提供資料" "B規劃圖面" "C簡報資料" "D預算報價" \
              "E業主合同資料" "F供應商報價與資料" "G進度計畫管理" "H照片" "I其他"; do
  mkdir -p "${BASE}/${folder}"
done
```

**移動檔案（依 Step 1 分析結果）：**
```bash
mv "$SOURCE" "$BASE/A業主提供資料/" # 對每個檔案執行對應移動
```

**清理暫存：**
```bash
rm "${BASE}/.../*.dwl" "${BASE}/.../*.dwl2"   # 直接刪除 lock 檔
mv "${BASE}/.../*.bak" "${BASE}/.../old/"      # bak 移入 old/
```

---

### Step 3：Notion 專案頁面

**檢查是否已存在（搜尋同名專案）：**
```
mcp__notion-win__API-post-search
query: "專案名稱關鍵字"
filter: {"value": "page", "property": "object"}
```

**若不存在，建立新頁面：**
```
mcp__notion-win__API-post-page
parent: {"database_id": "3355cac1-0351-4ef4-8eb1-8b8f0bb619c3"}
properties:
  - 專案（title）：專案名稱
  - 公司別：宏祐國際 or 宏洋環控（依資料夾判斷）
  - 開始日：資料夾日期前綴（YYYYMMDD → YYYY-MM-DD）
  - 狀態：規劃中
  - 負責人：政宏（id: 261d872b-594c-8188-8718-000252a44fde）
```

---

### Step 4：建立 A-I 折疊標題與檔案備忘

**使用 Node.js 直接呼叫 Notion API**（MCP 工具不支援 heading_2 toggleable）：

Windows 路徑：`C:\Users\deco01\nodejs\node.exe`
Mac 路徑：`~/.nvm/versions/node/v24.14.1/bin/node`

```js
const TOKEN = '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';
const PAGE_ID = '...'; // 新建或找到的頁面 ID

const headings = [
  { title: 'A 業主提供資料', bullets: [...] },
  { title: 'B 規劃圖面',   bullets: ['尚無資料（...）'] },
  // ... C ~ I
];

const children = headings.map(h => ({
  object: 'block',
  type: 'heading_2',
  heading_2: {
    rich_text: [{ type: 'text', text: { content: h.title } }],
    is_toggleable: true,
    children: h.bullets.map(b => ({
      object: 'block',
      type: 'bulleted_list_item',
      bulleted_list_item: {
        rich_text: [{ type: 'text', text: { content: b } }]
      }
    }))
  }
}));

await fetch(`https://api.notion.com/v1/blocks/${PAGE_ID}/children`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ children })
});
```

**各分類備忘格式：**
- 有檔案：`檔案名 — 說明（日期、用途）`
- 空的：`尚無資料（待補：XXX）`

---

### Step 4.5：Dropbox 分享連結 → Notion bookmark

**為有檔案的 A-I 資料夾建立 Dropbox 分享連結，並插入 Notion 折疊標題內。**

使用腳本：`D:\Dropbox\Tu-agent\000_Agent\scripts\dropbox_notion_links.mjs`（Windows）

需修改腳本的以下參數：
- `NOTION_PAGE_ID`：當次新建的 Notion 頁面 ID
- `PROJECT_PATH`：Dropbox 資料夾路徑（`/宏祐/YYYYMMDD-XXX工程`）
- `FOLDERS_WITH_CONTENT`：有實際檔案的分類字母陣列（如 `['A', 'D', 'F']`）

**注意：**
- Dropbox token 有效期限約 4 小時，過期需重新申請（dropbox.com/developers/apps → Generate access token）
- Dropbox API 若 link 已存在會自動取得現有連結，不會重複建立

執行方式（Windows）：
```bash
"C:\Users\deco01\nodejs\node.exe" "D:\Dropbox\Tu-agent\000_Agent\scripts\dropbox_notion_links.mjs"
```

結果：Notion 頁面的 A/D/F 折疊標題底部會出現一個 `📂 開啟 Dropbox 資料夾：XXX` 書籤連結。

---

### Step 5：輸出執行摘要

```
## 執行完成

### Notion 新專案 ✅
- 名稱：XXX
- 公司別 / 開始日 / 狀態

### Dropbox 資料夾重整 ✅
| 分類 | 移入內容 |
|---|---|
| A | ... |
...

### 注意事項
- 異常分類（如 H 裡有 DWG）已處理
- 清理暫存：dwl × N、bak → old/ × N
```

---

## 關鍵常數

| 項目 | 值 |
|---|---|
| Notion Projects 資料庫 ID | `3355cac1-0351-4ef4-8eb1-8b8f0bb619c3` |
| Notion Token | `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` |
| 政宏 User ID | `261d872b-594c-8188-8718-000252a44fde` |
| Windows Node | `C:\Users\deco01\nodejs\node.exe` |
| Mac Node | `~/.nvm/versions/node/v24.14.1/bin/node` |
| Dropbox 根目錄（Windows） | `D:\Dropbox\宏祐\` |
| Dropbox 根目錄（Mac） | `~/Dropbox/宏祐/` |
