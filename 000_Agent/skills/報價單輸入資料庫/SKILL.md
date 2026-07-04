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
| 發包管理 | `3337aebd-089f-80d1-aa42-f85b80c119b9` |
| 案件財務管理（專案） | `2f97aebd-089f-80f7-9607-df6dc41ab3bd` |

## 執行步驟（照順序完成，每步完成後再進下一步）

### STEP 1：讀取報價單並建立摘要

1. 使用 `Read` 工具讀取使用者提供的檔案（PDF / JPG / Excel）
   - Excel（.xls/.xlsx）為二進位格式，需用 Node.js 解析：
     ```js
     const XLSX = require('C:/Users/deco01/nodejs/node_modules/xlsx');
     const wb = XLSX.readFile('檔案路徑');
     const ws = wb.Sheets[wb.SheetNames[0]];
     console.log(XLSX.utils.sheet_to_csv(ws));
     ```
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

### STEP 1.3：詢問圖說與規範依據

> 在 STEP 1 使用者確認摘要後，立即詢問。**不得跳過此步驟。**

詢問使用者：

```
📐 是否有本次報價對應的圖說或規範文件？

例如：施工圖面（PDF）、工程標單（BOQ）、規範說明書等

有的話請提供檔案路徑，我會：
1. 讀取並摘要圖說/規範內容
2. 對照報價單品項逐條比對
3. 建立本機分析文件（400_Knowledge/工程/）
4. 建立 Notion 圖說文件（工作文件中心），供日後相同類型工程查詢參考

[ 有，提供路徑 ] / [ 暫無，稍後補上 ] / [ 此案無圖說 ]
```

**若使用者提供圖說/規範路徑 → 執行以下子流程：**

#### 1. 讀取圖說/規範並比對報價

1. 使用 `Read` 工具讀取每份圖說/規範（PDF/Word/Excel）
2. 比對報價單品項與圖說規格：
   - 品項名稱是否一致（圖說編號 vs 廠商描述）
   - 尺寸規格是否匹配（W×H×D）
   - 數量是否合理（從平面圖推算）
   - 材料規格是否符合（圖說要求 vs 廠商報價）
3. 判斷各品項單價合理性（對照市場行情估算）

#### 2. 建立本機分析文件

建立 `400_Knowledge/工程/YYYY-MM-DD_{案件名稱}_{工種}報價合理性分析.md`，格式如下：

```markdown
---
date: YYYY-MM-DD
tags: [工程知識, {工種}, 報價合理性, {案件名稱}]
案件: {完整工程名稱}
廠商: {廠商名稱}
工種: {工種}
---

# {案件}_{工種}報價合理性分析

> 報價日期：YYYY-MM-DD｜圖說日期：YYYY-MM-DD｜分析日期：YYYY-MM-DD

## 一、圖說與標單來源
| 文件 | 檔案名稱 | Dropbox 連結 |
...

## 二、標單品項 vs 廠商報價對照
| 標單編號 | 標單品項 | 單位 | 數量 | 廠商品項 | 廠商單價 | 小計 |
...

## 三、單價合理性判斷
| 品項 | 單位 | 廠商單價 | 市場行情範圍 | 判斷 |
...（✅合理 / ⚠️偏高 / ❌明顯偏高）

## 四、圖說關鍵規格摘要
...

## 五、後續相似案件參考重點
...（供日後相同類型工程報價評估使用）

## 六、總價
...
```

#### 3. 建立 Notion 圖說文件

對每份圖說/規範檔案，在工作文件中心（`2617aebd-089f-80e8-90b1-faae6e0bc21a`）建立文件：

```
文件名稱：YYYYMMDD{工程名稱}{文件類型}-{供應商名稱}
  範例：20240603土銀大樓廁所整修木作圖面
類別：["圖說"]  ← 若非報價單，類別改為"圖說"
```

建立後：
1. 取得 Dropbox 分享連結（方法同 STEP 6）
2. 在頁面加入以下區塊：
   - `📎 原始圖說檔案`（段落）
   - 檔案名稱、歸檔路徑（段落）
   - Dropbox 連結（bookmark）
3. 記錄圖說 page_id 清單，供 STEP 5 建立關聯使用

**若使用者選「暫無」或「無圖說」→ 記錄狀態，繼續下一步。**
在 STEP 7 回報中標記：「⚠️ 無圖說依據，建議後續取得後補充」

---

### STEP 1.5：重複報價單檢查

> 可與 STEP 2 同時執行（兩者皆為唯讀查詢，無相依性）

使用 `mcp__notion__API-post-search` 搜尋工作文件中心，確認是否已存在相同報價單。

**搜尋條件：** 以「供應商名稱」+「報價日期（YYYYMMDD）」作為關鍵字搜尋。

**情況 A：未找到重複** → 繼續 STEP 3

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

> 可與 STEP 1.5 同時執行

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
- 若無完全符合，新增選項並告知使用者

**案件名稱 relation（`案件名稱` 欄位）— 必填，不得略過：**
- 用 `API-post-search` 以工程案件名稱關鍵字搜尋，找案件管理系統（DB `3355cac1-0351-4ef4-8eb1-8b8f0bb619c3`）中對應的案件頁面
- 找到唯一符合 → 記下 `$CASE_PAGE_ID`，STEP 4 建立品項時填入 `案件名稱` relation
- 找到多個 → **AskUserQuestion** 讓使用者選擇
- 找不到 → 告知使用者「找不到對應案件，品項的案件名稱 relation 將留空，請事後手動補上」

**編號規則**（`編號` title 欄位，每個品項一筆）：
- 格式：`供應商簡稱-YYMMDD-序號`
- 供應商簡稱：取名稱前 2~3 字（去掉「工程行/有限公司/股份有限公司」等後綴）
- YYMMDD：報價日期（西元後 2 碼+月+日），例如 260427
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
  案件名稱: { relation: [{ id: "$CASE_PAGE_ID" }] }
```

- `總價` 欄位為公式（數量×單價），自動計算，**不需填入**
- `供應商` 欄位在建立時同步填入，無需事後更新
- `案件名稱` 欄位連結案件管理系統頁面，找不到時留空並告知使用者
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

**若 STEP 1.3 有圖說文件 → 在報價單工作文件中心頁面加入圖說連結區塊：**

```json
[
  { "type": "paragraph", "paragraph": { "rich_text": [{ "type": "text", "text": { "content": "📐 報價圖說依據" } }] } },
  { "type": "bulleted_list_item", "bulleted_list_item": { "rich_text": [
      { "type": "text", "text": { "content": "{圖說文件名稱}：" } },
      { "type": "text", "text": { "content": "開啟 Dropbox 檔案", "link": { "url": "{圖說Dropbox連結}" } } }
  ]}},
  { "type": "paragraph", "paragraph": { "rich_text": [{ "type": "text", "text": { "content": "📊 報價合理性分析：400_Knowledge/工程/{YYYY-MM-DD_案件_工種報價合理性分析.md}" } }] } }
]
```

---

### STEP 5.5：歸檔原始報價單到 Dropbox 專案資料夾

#### 1. 確認 Dropbox 根目錄與專案集團

| 平台 | 集團 | 路徑 |
|------|------|------|
| Windows | 宏祐集團 | `D:\Dropbox\宏祐` |
| Windows | YUSHI | `D:\Dropbox\yushi` |
| Mac | 宏祐集團 | `/Users/tuzhenghong/Library/CloudStorage/Dropbox/宏祐` |
| Mac | YUSHI | `/Users/tuzhenghong/Library/CloudStorage/Dropbox/yushi` |

若集團尚未確認，以 **AskUserQuestion** 詢問。

#### 2. 掃描並匹配專案資料夾

```js
const fs = require('fs');
const dirs = fs.readdirSync(DROPBOX_ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && d.name.includes(CASE_KEYWORD))
  .map(d => d.name);
console.log(JSON.stringify(dirs));
```

- `CASE_KEYWORD`：從工程案件名稱取前 4~6 字（去掉常見前綴如「羅東」「博訊」）
- 找到唯一符合 → 自動使用
- 找到多個 → **AskUserQuestion** 讓使用者選擇
- 找不到 → 提示使用者確認，或選「跳過歸檔」

#### 3. 確認目標子目錄

目標資料夾（固定）：`$PROJECT_FOLDER/F供應商報價與資料/`
- 若不存在則自動建立

```js
const fs = require('fs'), path = require('path');
const dest = path.join(PROJECT_FOLDER, 'F供應商報價與資料');
if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
console.log(dest);
```

#### 4. 複製並重新命名

新檔名格式：`YYYYMMDD-{廠商簡稱}-{工種}{金額}{含稅/未稅}.{副檔名}`
- 廠商簡稱：去掉「有限公司/股份有限公司/工程行/泥作」等後綴，保留簡稱
- 金額：取優惠價/議價（非原始定價），直接附加，無分隔符號
- 含稅/未稅：明確含稅標 `含稅`，明確未稅標 `未稅`，不確定可省略
- 範例：`20260518-極鋼-鐵工工程330000含稅.pdf`、`20260131-銓聯-泥作183500未稅.jpg`

```js
const fs = require('fs'), path = require('path');
fs.copyFileSync(SOURCE_PATH, path.join(DEST_DIR, NEW_FILENAME));
if (!fs.existsSync(path.join(DEST_DIR, NEW_FILENAME))) throw new Error('複製失敗');
console.log('✅ 複製成功：', path.join(DEST_DIR, NEW_FILENAME));
```

成功後記下 `$ARCHIVED_PATH`（完整歸檔路徑），供 STEP 6 使用。
若複製失敗，顯示錯誤原因，詢問使用者：「跳過歸檔並繼續建立 Notion？」

---

### STEP 6：將原始報價單檔案嵌入 Notion 文件

使用 `mcp__notion__API-patch-block-children` 將檔案資訊加入 STEP 5 建立的工作文件中心頁面。

1. 優先使用 `$ARCHIVED_PATH`（STEP 5.5 歸檔後路徑），若跳過則用原始路徑
2. **取得 Dropbox 分享連結（必要步驟，不可跳過）**：
   - 憑證來源：`D:\Dropbox\Tu-agent\000_Agent\scripts\add_dropbox_link_to_notion.mjs`
   - Dropbox API 路徑格式：`/{集團}/{專案資料夾名稱}/廠商報價/{$NEW_FILENAME}`（正斜線，無磁碟代號）
   - 流程：
     1. 用 refresh_token 換取 access_token（POST `https://api.dropboxapi.com/oauth2/token`）
     2. 呼叫 `create_shared_link_with_settings`
     3. 若回傳 `shared_link_already_exists` → 改呼叫 `list_shared_links` 取既有連結
   - 若取得失敗 → 告知使用者並詢問是否手動補上，**不可靜默跳過**
3. 加入以下區塊（依序全部加入）：

```json
[
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{ "type": "text", "text": { "content": "📎 原始報價單檔案" } }]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{ "type": "text", "text": { "content": "檔案名稱：{$NEW_FILENAME}" } }]
    }
  },
  {
    "type": "paragraph",
    "paragraph": {
      "rich_text": [{ "type": "text", "text": { "content": "歸檔路徑：{$ARCHIVED_PATH}" } }]
    }
  },
  {
    "type": "bookmark",
    "bookmark": {
      "url": "{$SHARE_URL}",
      "caption": [{ "type": "text", "text": { "content": "點此開啟 Dropbox 檔案" } }]
    }
  }
]
```

---

### STEP 7：最終確認與回報

```
✅ Notion 建立完成

📄 報價單文件：{文件名稱}
🏢 供應商：{名稱}（新建/已存在）
📋 品項：{N} 筆
   - {編號} {品項名稱} {數量}{單位} × {單價} = {小計}
   ...
💰 總計：{總金額}（未稅）
📁 歸檔路徑：{$ARCHIVED_PATH}

📐 圖說/規範依據：
   - {圖說文件名稱}（{N}頁）→ Notion + Dropbox 已建立
   - 合理性分析：400_Knowledge/工程/{分析文件名稱}.md
   ← 若無圖說：⚠️ 無圖說依據，建議後續取得後補充

🔗 Notion 連結：
   報價單：{url}
   供應商：{url}
   圖說：{url}（若有）
```

若有欄位無法自動填入，列出並詢問使用者。

---

### STEP 8：詢問是否已發包，同步寫入發包管理

> 在 STEP 7 完成後立即執行，不得跳過詢問。

用 **AskUserQuestion** 詢問：
- 問題：「這份報價是否已確認發包？」
- 選項：
  - 已發包（合約已確認，尚未開工）
  - 進行中（已進場施工）
  - 已完成（工程結束）
  - 尚未發包（跳過此步驟）

**若選「尚未發包」→ 結束流程，不建立發包管理記錄。**

**若選其他狀態 → 執行以下流程：**

#### 1. 搜尋案件財務管理 DB 找對應專案

用 `API-post-search` 以工程案件名稱關鍵字搜尋，篩選
`parent.database_id == "2f97aebd-089f-80f7-9607-df6dc41ab3bd"` 的頁面。

- 找到唯一符合 → 自動使用，記下 `$PROJECT_ID`
- 找到多個 → **AskUserQuestion** 讓使用者選擇
- 找不到 → 告知使用者並提供「我來貼連結」選項；從 URL 擷取 page_id

#### 2. 建立發包管理記錄

用 `API-post-page` 在 `3337aebd-089f-80d1-aa42-f85b80c119b9` 建立：

```json
{
  "parent": { "database_id": "3337aebd-089f-80d1-aa42-f85b80c119b9" },
  "properties": {
    "廠商名稱": { "title": [{ "text": { "content": "{工程案件名稱}｜{廠商簡稱}{工種簡稱}" } }] },
    "工種": { "select": { "name": "{工種（發包管理格式，見下表）}" } },
    "成本": { "number": 未稅合計數字 },
    "日期": { "date": { "start": "YYYY-MM-DD" } },
    "狀態": { "status": { "name": "已發包 / 進行中 / 已完成" } },
    "是否已發包": { "checkbox": true },
    "專案": { "relation": [{ "id": "$PROJECT_ID" }] },
    "備註": { "rich_text": [{ "text": { "content": "{品項摘要}，報價編號 {編號}" } }] },
    "報價單連結": { "files": [{ "type": "external", "name": "{$NEW_FILENAME}", "external": { "url": "$SHARE_URL" } }] }
  }
}
```

**廠商名稱格式**：`{工程案件名稱}｜{廠商簡稱}{工種簡稱}`
- 廠商簡稱：同 STEP 3 編號簡稱
- 工種簡稱：取工種主要關鍵字（如「乾盤管」「輕隔間」「地磚」）
- 範例：`南港GTP實驗室修改工程｜嘉祿乾盤管`、`羅東聖母S棟｜極鋼鐵工`

**報價單連結**：直接使用 STEP 6 已取得的 `$SHARE_URL`，無需重新取得。

**工種對照（工程報價管理 → 發包管理）：**

| 工程報價管理 | 發包管理選項 |
|------------|------------|
| 空調工程 | 空調 |
| 水電工程 | 水電 |
| 消防工程 | 水電 |
| 鐵工工程 | 鐵工 |
| 輕隔間工程 | 輕鋼架 |
| 天花板工程 / 輕鋼架工程 | 輕鋼架 |
| 油漆工程 | 油漆 |
| 地板工程（PVC） | PVC地磚 |
| 地板工程（塑膠地磚） | 塑膠地磚 |
| 拆除清運 | 拆除 |
| 木作工程 | 木作 |
| 泥作工程 | 泥作 |
| 玻璃工程 | 玻璃 |
| 防水工程 | 防水 |
| 衛浴設備 | 衛浴設備 |

若報價單跨多個工種（如水電+消防），以主工種為主，在備註補充說明。

#### 2.5 同步建立/更新案件財務管理頁面的「本案發包明細」表格

> 發包管理資料庫的成本會透過 rollup 自動反映到案件財務管理頁面的「成本」欄位，但案件財務管理頁面內若已有「本案發包明細」inline 子資料庫（供快速瀏覽單一案件所有發包項目），也要同步寫入一筆，不能只寫發包管理就結束。

1. 用 `API-get-block-children` 讀取 `$PROJECT_ID`（案件財務管理頁面）的 block children，找 `type: "child_database"` 且標題含「本案發包明細」的區塊
2. **情況 A：已存在** → 記下該 database_id，直接新增一筆品項
3. **情況 B：不存在** → 先建立：
   - ⚠️ Notion MCP 的 `API-create-a-data-source` 在本環境呼叫會回傳 `invalid_request_url`（新版 data source 端點與 MCP server 設定的 `Notion-Version: 2022-06-28` 不相容），改用 curl 直連舊版 `POST https://api.notion.com/v1/databases` 建立：
     ```bash
     curl -s -X POST https://api.notion.com/v1/databases \
       -H "Authorization: Bearer $(取自 ~/.claude.json 的 mcpServers.notion.env.OPENAPI_MCP_HEADERS)" \
       -H "Notion-Version: 2022-06-28" \
       -H "Content-Type: application/json" \
       -d '{
         "parent": {"type": "page_id", "page_id": "$PROJECT_ID"},
         "title": [{"type": "text", "text": {"content": "本案發包明細"}}],
         "properties": {
           "工種/品項": {"title": {}},
           "廠商": {"rich_text": {}},
           "合約金額": {"number": {"format": "number"}},
           "已付金額": {"number": {"format": "number"}},
           "狀態": {"select": {"options": [
             {"name": "未發包", "color": "gray"},
             {"name": "已發包", "color": "blue"},
             {"name": "施工中", "color": "yellow"},
             {"name": "完工", "color": "green"}
           ]}},
           "備註": {"rich_text": {}}
         }
       }'
     ```
   - 建立後立即 `PATCH /v1/databases/{id}` 設定 `{"is_inline": true}`，否則會顯示成連結頁面而非嵌入表格
4. 在該 database（inline 或新建）用 `API-post-page` 新增一筆：
   ```json
   {
     "parent": { "database_id": "本案發包明細_database_id" },
     "properties": {
       "工種/品項": { "title": [{ "text": { "content": "{工種簡稱或品項摘要}" } }] },
       "廠商": { "rich_text": [{ "text": { "content": "{廠商全名}" } }] },
       "合約金額": { "number": 含稅金額 },
       "已付金額": { "number": 0 },
       "狀態": { "select": { "name": "{對應STEP8狀態：已發包/施工中/完工}" } },
       "備註": { "rich_text": [{ "text": { "content": "{品項摘要，同發包管理備註}" } }] }
     }
   }
   ```
   - **合約金額填含稅金額**，與發包管理「成本」欄位使用的含稅金額一致，方便對照
   - 之後若有零星耗材/雜支（五金零件、加班茶水等）需歸入同一案件成本，也比照本步驟同時寫入發包管理＋本案發包明細兩處，缺一不可

#### 3. 回報

```
✅ 發包管理已新增

🏗️ {工程案件名稱}｜{廠商簡稱}{工種簡稱}
💰 成本：NT${未稅合計}（未稅）
📅 報價日期：{報價日期}
🔖 狀態：{狀態}
🔗 https://www.notion.so/{page_id（無連字號）}
```

---

## 重要規則

1. **每步都確認再繼續**，不要一次全部執行後才回報
2. **編號不能重複**，建立前先查詢資料庫確認無重複
3. **不含稅金額為基準**，有含稅版本寫入備註
4. **所有欄位不留空**，能查到的資料一定補上
5. **工種 select 選項**從資料庫現有選項中選，不自創新選項（除非使用者確認）
6. **單位 select 選項**同上，從現有選項選
7. **一價多項目的處理規則**：報價單中若一個單價包含多個子項目（例如「冰水管安裝及配管 1式 175,100」下含10項細目），**不得跳過或留空**，應：
   - 建立一筆 Notion 品項，`品項名稱` 填大項名稱
   - `品項規格` 欄位寫入所有子項目（格式：「含：子項×數量、子項×數量、…」，與報價單格式一致）
   - `單價` 填整包金額，`數量` 填1（或實際數量），`單位` 填整包單位（式/組等）
   - `備註` 標記「一價包含多子項」

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
- 博洽辦公室
- 其他（詢問使用者）


---

## 分類

[[Skill目錄]]
