---
name: 報價單輸入資料庫
description: "報價單匯入 Notion + 自動歸檔。收到 PDF/Excel/JPG 報價單後，建立摘要確認 → 查詢/建立供應商 → 建立工程報價品項 → 建立工作文件中心報價單文件 → 自動複製檔案到 Dropbox 專案廠商報價資料夾並改名。觸發方式：使用者提供報價單檔案路徑，或直接輸入 /報價單輸入資料庫。"
---

# 報價單匯入 Notion SOP

## 資料庫 ID（固定，勿更改）

| 資料庫 | ID |
|--------|-----|
| 工作文件中心（報價單文件） | `2617aebd-089f-80e8-90b1-faae6e0bc21a` |
| 工程報價管理系統（品項明細） | `a1e36c9f-f084-4965-ac76-33e51e53f711` |
| 供應商資料庫 | `8ed44912-2c9e-4c9a-bbd1-d7bbc1933b3b` |

## 執行步驟（照順序完成，每步完成後再進下一步）

### STEP 1：讀取報價單並建立摘要

1. 使用 `Read` 工具讀取使用者提供的檔案（PDF / JPG / Excel）
2. 整理以下資訊並以表格呈現給使用者確認：
   - **供應商名稱**、聯絡人、電話、手機、統一編號
   - **報價日期**（民國轉西元）
   - **工程案件名稱**
   - **工種**（對應資料庫選項）
   - **品項明細**：每項的品項名稱、規格（W×H）、單位、數量、單價、小計
   - **總計金額**（含/不含稅）
   - **備註**
3. 詢問使用者：「以上摘要是否正確？是否繼續建立 Notion 資料？」
4. **等待使用者確認後才繼續**，若有修正先更新摘要

---

### STEP 1.5：重複報價單檢查

使用 `mcp__notion__API-post-search` 搜尋工作文件中心，確認是否已存在相同報價單。

**搜尋條件：** 以「供應商名稱」+ 「報價日期（YYYYMMDD）」作為關鍵字搜尋。

**情況 A：未找到重複** → 繼續 STEP 2

**情況 B：找到疑似重複的文件**
1. 列出所有符合的文件名稱與 Notion 連結
2. 告知使用者：
   ```
   ⚠️ 警告：偵測到可能重複的報價單
   
   已存在以下相似文件：
   - {文件名稱}（{Notion連結}）
   
   請確認是否為重複？
   [ 是重複，取消本次匯入 ] / [ 非重複，繼續建立 ]
   ```
3. **等待使用者明確回覆後才繼續**，若使用者確認重複則終止整個流程

---

### STEP 2：查詢供應商資料庫

使用 `mcp__notion__API-post-search` 搜尋供應商名稱。

**情況 A：供應商已存在**
- 記錄其 page_id，進行 STEP 3

**情況 B：供應商不存在 → 建立新供應商記錄**
1. 從報價單填入已知欄位：
   - `供應商名稱`（title）
   - `聯絡人`（rich_text）
   - `電話`（phone_number）
   - `手機`（rich_text）
   - `統編`（number，純數字）
   - `工種類別`（multi_select，從報價內容判斷）
   - `合作狀態`：選「評估中」
2. **網路補足缺漏資料**：使用 `WebSearch` 搜尋「{供應商名稱} 地址 統編」補足：
   - `地址`（rich_text）
   - `網址`（url，若有官網）
   - `電子郵件`（email，若能查到）
3. 建立後記錄新供應商的 page_id
4. 告知使用者：「已建立供應商：{名稱}，補充了以下資料：...」

---

### STEP 3：決定工程案件名稱與編號

**工程案件名稱**（`工程案件名稱` select 欄位）：
- 從現有選項中找最符合的
- 若無完全符合，選最接近的，並告知使用者

**編號規則**（`編號` title 欄位，每個品項一筆）：
- 格式：`供應商簡稱-YYMMDD-序號`
- 供應商簡稱：取名稱前2~3字（去掉「工程行/有限公司/股份有限公司」等後綴）
- YYMMDD：報價日期（西元後2碼+月+日），例如 260427
- 序號：從 001 開始，同一張報價單的品項依序遞增
- 參考現有範例：`楷程-251210-001`、`楷程-251210-002`

---

### STEP 4：在工程報價管理系統逐筆建立品項

對每個品項，使用 `mcp__notion__API-post-page` 在 `a1e36c9f-f084-4965-ac76-33e51e53f711` 建立：

```
parent: { database_id: "a1e36c9f-f084-4965-ac76-33e51e53f711" }
properties:
  編號: { title: [{ text: { content: "極鋼-260427-001" } }] }
  品項名稱: { rich_text: [{ text: { content: "病房不銹鋼窗" } }] }
  品項規格: { rich_text: [{ text: { content: "W1.5×H1.5m" } }] }
  單位: { select: { name: "組" } }
  數量: { number: 12 }
  單價: { number: 11500 }
  工種: { select: { name: "鐵工工程" } }
  報價日期: { date: { start: "2026-04-27" } }
  工程案件名稱: { select: { name: "羅東聖母S棟病房整修" } }
  備註: { rich_text: [{ text: { content: "..." } }] }
  供應商: { relation: [{ id: "供應商page_id" }] }
```

- `總價` 欄位為公式（數量×單價），自動計算，**不需填入**
- `供應商` 欄位在建立時同步填入，無需事後更新
- 建立完成後記錄所有品項的 page_id 清單

---

### STEP 5：在工作文件中心建立報價單文件

使用 `mcp__notion__API-post-page` 在 `2617aebd-089f-80e8-90b1-faae6e0bc21a` 建立：

```
parent: { database_id: "2617aebd-089f-80e8-90b1-faae6e0bc21a" }
properties:
  文件名稱: { title: [{ text: { content: "YYYYMMDD{工程名稱}報價-{供應商名稱}" } }] }
  類別: { multi_select: [{ name: "報價單" }] }
```

文件名稱格式範例：`20260428聖母醫院介護病房鐵格柵報價-極鋼工程行`

記下回傳的工作文件中心頁面 `page_id`，完成後**逐筆更新 STEP 4 的所有品項**，設定 `報價單及圖面` 關聯：

```
對每個品項 page_id，呼叫 API-patch-page：
properties:
  報價單及圖面: { relation: [{ id: "工作文件中心_page_id" }] }
```

---

### STEP 5.5：歸檔原始報價單到 Dropbox 專案資料夾

**目的：** 將使用者提供的原始報價單檔案，複製到對應專案的 `F供應商報價與資料/廠商報價/` 目錄，並依命名規則重新命名。

#### 1. 確認 Dropbox 根目錄與專案集團

依平台與集團（STEP 1 or STEP 3 已知）取得 `$DROPBOX_ROOT`：

| 平台 | 集團 | 路徑 |
|------|------|------|
| Windows | 宏祐集團 | `D:\Dropbox\宏祐` |
| Windows | YUSHI | `D:\Dropbox\yushi` |
| Mac | 宏祐集團 | `/Users/tuzhenghong/Library/CloudStorage/Dropbox/宏祐` |
| Mac | YUSHI | `/Users/tuzhenghong/Library/CloudStorage/Dropbox/yushi` |

若集團尚未確認，以 **AskUserQuestion** 詢問。

#### 2. 掃描並匹配專案資料夾

以 Node.js 掃描 `$DROPBOX_ROOT`，找出名稱含有案件關鍵字的資料夾：

```js
// Windows
const NODE = 'C:\\Users\\deco01\\nodejs\\node.exe';

// 掃描邏輯（以 Node 執行）
const fs = require('fs');
const dirs = fs.readdirSync(DROPBOX_ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && d.name.includes(CASE_KEYWORD))
  .map(d => d.name);
console.log(JSON.stringify(dirs));
```

- `CASE_KEYWORD`：從 STEP 3 的工程案件名稱取前 4~6 字（去掉常見前綴如「羅東」「博訊」）
- 若找到唯一符合的資料夾 → 自動使用
- 若找到多個 → 用 **AskUserQuestion** 讓使用者選擇
- 若找不到 → 提示使用者確認案件名稱，或選「跳過歸檔」

記下 `$PROJECT_FOLDER`（完整路徑）。

#### 3. 確認目標子目錄存在

目標路徑依實際狀況選擇（優先順序）：

1. `$PROJECT_FOLDER/F供應商報價與資料/廠商報價/`（A-I 標準結構已整理）
2. `$PROJECT_FOLDER/廠商報價/`（尚未整理 A-I 結構，只有廠商報價資料夾）
3. 兩者都不存在 → 在 `$PROJECT_FOLDER` 下建立 `廠商報價/`

掃描邏輯（Node.js）：
```js
const fs = require('fs'), path = require('path');
const p1 = path.join(PROJECT_FOLDER, 'F供應商報價與資料', '廠商報價');
const p2 = path.join(PROJECT_FOLDER, '廠商報價');
let dest;
if (fs.existsSync(p1))      dest = p1;
else if (fs.existsSync(p2)) dest = p2;
else { fs.mkdirSync(p2, { recursive: true }); dest = p2; }
console.log(dest);
```

記下 `$DEST_DIR`（最終目標路徑）。

#### 4. 複製並重新命名

新檔名格式：`YYYYMMDD-{廠商名稱}-{工種}.{副檔名}`
- `YYYYMMDD`：報價日期（STEP 1 取得）
- `廠商名稱`：供應商名稱（去掉「有限公司/股份有限公司/工程行」等後綴，保留簡稱）
- `工種`：STEP 4 判斷的工種（中文，如「鐵工工程」）
- 副檔名：保留原始副檔名（.pdf / .xlsx / .jpg）

範例：`20260518-極鋼-鐵工工程.pdf`

```bash
# Windows（PowerShell）
Copy-Item -Path "$SOURCE_PATH" -Destination "$DEST_DIR\$NEW_FILENAME"

# Mac
cp "$SOURCE_PATH" "$DEST_DIR/$NEW_FILENAME"
```

#### 5. 確認複製成功

```bash
# 驗證檔案存在
Test-Path "$DEST_DIR\$NEW_FILENAME"   # Windows
ls "$DEST_DIR/$NEW_FILENAME"           # Mac
```

成功後記下 `$ARCHIVED_PATH`（完整歸檔路徑），供 STEP 6 使用。

若複製失敗（權限、路徑不存在等），顯示錯誤原因，詢問使用者：「跳過歸檔並繼續建立 Notion？」

---

### STEP 6：將原始報價單檔案嵌入 Notion 文件

使用 `mcp__notion__API-patch-block-children` 將原始檔案資訊加入 STEP 5 建立的工作文件中心頁面（block_id = 報價單文件 page_id）。

**流程：**

1. 取得歸檔後的路徑（優先使用 `$ARCHIVED_PATH`，若 STEP 5.5 跳過則用原始路徑）
2. 判斷路徑是否在 Dropbox：
   - **是** → 嘗試用 Playwright 取得 Dropbox 分享連結（`dropbox_notion_links.mjs` 邏輯）
   - **否** → 直接記錄本機路徑
3. 使用 `mcp__notion__API-patch-block-children` 加入以下區塊：

```json
[
  {
    "type": "callout",
    "callout": {
      "rich_text": [{ "type": "text", "text": { "content": "📎 原始報價單檔案" } }],
      "icon": { "emoji": "📎" },
      "color": "gray_background"
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{ "type": "text", "text": { "content": "檔案名稱：{$NEW_FILENAME 或原始檔名}" } }]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{ "type": "text", "text": { "content": "歸檔路徑：{$ARCHIVED_PATH}" } }]
    }
  }
]
```

4. 若成功取得 Dropbox 分享連結，額外加入 bookmark 區塊：

```json
{
  "type": "bookmark",
  "bookmark": { "url": "{Dropbox分享連結}" }
}
```

---

### STEP 7：最終確認與回報

完成後向使用者回報：

```
✅ Notion 建立完成

📄 報價單文件：{文件名稱}
🏢 供應商：{名稱}（新建/已存在）
📋 品項：{N} 筆
   - {編號} {品項名稱} {數量}{單位} × {單價} = {小計}
   ...
💰 總計：{總金額}（未稅）

🔗 Notion 連結：
   報價單：{url}
   供應商：{url}
```

若有欄位無法自動填入，列出並詢問使用者。

---

## 重要規則

1. **每步都確認再繼續**，不要一次全部執行後才回報
2. **編號不能重複**，建立前先查詢資料庫確認無重複
3. **不含稅金額為基準**，有含稅版本寫入備註
4. **所有欄位不留空**，能查到的資料一定補上
5. **工種 select 選項**從資料庫現有選項中選，不自創新選項（除非使用者確認）
6. **單位 select 選項**同上，從現有選項選

## 工種對照（報價單描述 → Notion 工種選項）

| 報價單內容 | Notion 工種 |
|-----------|------------|
| 不銹鋼、鐵格柵、鋼門、伸縮門 | 鐵工工程 |
| 水電、配線、配管 | 水電工程 |
| 輕隔間 | 輕隔間工程 |
| 天花板、輕鋼架 | 天花板工程 / 輕鋼架工程 |
| 空調、冷氣 | 空調工程 |
| 消防、灑水 | 消防工程 |
| 油漆 | 油漆工程 |
| 地板、地磚 | 地板工程 |
| 拆除清運 | 拆除清運 |
| 木作 | 木作工程 |
| 泥作 | 泥作工程 |

## 工程案件名稱選項（資料庫現有）

- 羅東聖母S棟病房整修
- 杏和醫院裝修工程
- 金運科技廠房整修工程
- 龍潭二樓辦公室裝修工程
- 耕莘醫院安康院區高壓氧建置工程
- 羅東聖母中醫診所建置工程
- 竹北廠房庫板工程
- 南港實驗室GTP實驗室修改工程
- 其他（詢問使用者）
