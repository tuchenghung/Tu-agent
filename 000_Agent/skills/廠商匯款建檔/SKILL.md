---
name: 廠商匯款建檔
description: "廠商匯款資料建檔 Skill — 收到廠商請款單/發票/匯款資訊（照片或文字，含公司名稱、統編、匯款銀行、分行、戶名、帳號）後，自動查重 → 視需要建立/補齊供應商資料庫記錄 → 建立廠商匯款資料表記錄並關聯供應商 → 特殊情況（開票公司與實際收款帳戶不同）雙邊互相標註。觸發方式：使用者提供請款單、發票、對帳單或匯款資訊圖片/文字，或直接輸入 /廠商匯款建檔。"
---

# 廠商匯款建檔 SOP

## 資料庫 ID（固定，勿更改）

| 資料庫 | ID |
|--------|-----|
| 廠商匯款資料表 | `3387aebd-089f-809b-b9ce-e73fc7784e5d` |
| 供應商資料庫 | `8ed44912-2c9e-4c9a-bbd1-d7bbc1933b3b` |

## 為什麼全部用 curl / Node fetch 直連，不用 Notion MCP

`mcp__notion(-win)__API-query-data-source`、`API-create-a-data-source` 等新版 data source 系列工具，在目前環境會回傳 `invalid_request_url`（新版端點與 MCP server 設定的 `Notion-Version: 2022-06-28` 不相容）。查詢、建立、更新資料庫與頁面一律改走舊版 REST API（`Notion-Version: 2022-06-28`），穩定且兩邊功能一致。`API-retrieve-a-database`、`API-post-page`（單純建立無 relation 時）等基礎 MCP 工具若可用可以混用，但涉及 database query 或 patch database schema 時務必用 curl/fetch。

Token 讀取：
- Windows：`D:\Dropbox\Tu-agent\.env` 的 `NOTION_TOKEN`
- Mac：`~/Library/CloudStorage/Dropbox/Tu-agent/.env`（或使用者實際 Dropbox 路徑）的 `NOTION_TOKEN`

用 `require('dotenv').config()`（或 `node -e` 內嵌）讀取，不要把 token 貼進指令字串裡輸出到終端機。

---

## 執行步驟

### STEP 1：讀取請款單/匯款資訊並建立摘要

用 `Read` 工具讀取使用者提供的圖片或文件，整理以下欄位並以表格呈現給使用者確認：

| 欄位 | 說明 |
|------|------|
| 公司名稱 | 開立請款單/發票的公司全名（含「有限公司」等完整字號） |
| 統一編號 | 8 碼 |
| 匯款銀行 | 銀行全名（如「第一銀行」「台灣企銀」） |
| 分行 | 分行名稱 |
| 戶名 | 匯款帳戶戶名，通常等於公司名稱，但代收轉付時可能不同 |
| 帳號 | 純數字，去除破折號 |
| 地址 | 若請款單上有 |
| 聯絡電話 | 若有 |
| 請款事由 | 工程/服務內容摘要，寫入備註用 |
| 請款金額 | 含稅總額，寫入備註用 |

**公司名稱注意繁簡字**：常見混淆如「誼」≠「谊」、「台」≠「臺」。辨識完先跟使用者核對一次公司全名再繼續，不要憑影像 OCR 直覺帶過。

詢問使用者：「以上資訊是否正確？是否繼續建立？」**等待確認後才進 STEP 2。**

---

### STEP 2：判斷是否為「代收轉付」情境

檢查請款單上是否有「請款公司」與「實際付款/收款對象」不一致的註記（常見寫法：「此次交易請付款至：XXX」）。

- **一致**（開票公司=收款帳戶）→ 只需建立/更新一家廠商的匯款記錄，跳到 STEP 3
- **不一致** → 兩家公司都要各自查重、各自建立匯款記錄，並在雙方「備註」互相標註關聯與原因（例如：「本次請款實際付款對象為 OOO，見該廠商記錄」／「此帳號為 OOO 請款單之實際付款對象」）。後續 STEP 3~5 對兩家公司各跑一次。

---

### STEP 3：查詢/建立供應商資料庫記錄

用 Node.js 直連查詢 `8ed44912-2c9e-4c9a-bbd1-d7bbc1933b3b`（不要用 MCP 的 `API-query-data-source`）：

```js
require('dotenv').config();
const token = process.env.NOTION_TOKEN;
fetch('https://api.notion.com/v1/databases/8ed44912-2c9e-4c9a-bbd1-d7bbc1933b3b/query', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filter: { property: '供應商名稱', title: { contains: '{公司名稱關鍵字}' } },
    page_size: 5
  })
}).then(r => r.json()).then(d => console.log(JSON.stringify((d.results||[]).map(p => ({ id: p.id, name: p.properties['供應商名稱']?.title?.[0]?.plain_text })), null, 2)));
```

**情況 A：已存在** → 記下 `page_id`，若統編/電話/地址等基本欄位是空的且本次有資料，順手用 `PATCH /v1/pages/{id}` 補齊（不要覆蓋既有非空欄位）。

**情況 B：不存在** → 建立新供應商基本記錄：

```js
fetch('https://api.notion.com/v1/pages', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    parent: { database_id: '8ed44912-2c9e-4c9a-bbd1-d7bbc1933b3b' },
    properties: {
      '供應商名稱': { title: [{ text: { content: '{公司全名}' } }] },
      '統編': { number: {統編數字} },
      '電話': { phone_number: '{電話}' },
      '地址': { rich_text: [{ text: { content: '{地址}' } }] },
      '合作狀態': { select: { name: '評估中' } }
    }
  })
}).then(r => r.json()).then(d => console.log(d.id));
```

**不要**在供應商資料庫加匯款銀行/帳號等欄位——那是廠商匯款資料表的職責，供應商資料庫只放公司基本資料，避免兩處重複維護（2026-07-08 曾誤加後又移除）。

---

### STEP 4：查詢廠商匯款資料表是否已有同公司記錄

```js
fetch('https://api.notion.com/v1/databases/3387aebd-089f-809b-b9ce-e73fc7784e5d/query', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filter: { property: '公司名稱', title: { contains: '{公司名稱關鍵字}' } }
  })
}).then(r => r.json()).then(d => console.log(JSON.stringify((d.results||[]).map(p => ({ id: p.id, name: p.properties['公司名稱']?.title?.[0]?.plain_text })), null, 2)));
```

**已有記錄** → 用 `PATCH /v1/pages/{id}` 更新匯款資訊即可，不要建立第二筆。
**沒有記錄** → 進 STEP 5 建立。

---

### STEP 5：補齊 select 選項並建立廠商匯款資料表記錄

`匯款銀行`、`分行` 是 select 欄位。先確認要填入的值是否已在現有選項中（可從 STEP 4 查詢結果或直接 retrieve database 看 `properties.匯款銀行.select.options` / `properties.分行.select.options`）。

**沒有的話先補選項再寫入**，不要塞一個資料庫裡不存在的 select 值（Notion 會直接建立同名新選項沒錯，但先補的目的是讓兩步驟操作可控、可預期，且能一次補多個常用值）：

```js
fetch('https://api.notion.com/v1/databases/3387aebd-089f-809b-b9ce-e73fc7784e5d', {
  method: 'PATCH',
  headers: { 'Authorization': 'Bearer ' + token, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    properties: {
      '匯款銀行': { select: { options: [ /* 既有選項全部列出 */ { name: '第一銀行' }, /* ...其餘既有選項... */ { name: '{新銀行}' } ] } },
      '分行': { select: { options: [ /* 既有選項全部列出 */ { name: '{新分行}' } ] } }
    }
  })
});
```

> ⚠️ PATCH select options 時是**整份取代**，務必把既有選項也一併列出，只是多加新的，不能只丟新選項單獨 PATCH，否則會把舊選項洗掉。

接著建立記錄，`帳號` 是 number 類型，填純數字（去除所有破折號、空格）：

```js
fetch('https://api.notion.com/v1/pages', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    parent: { database_id: '3387aebd-089f-809b-b9ce-e73fc7784e5d' },
    properties: {
      '公司名稱': { title: [{ text: { content: '{公司全名}' } }] },
      '統一編號': { rich_text: [{ text: { content: '{統編}' } }] },
      '匯款銀行': { select: { name: '{銀行}' } },
      '分行': { select: { name: '{分行}' } },
      '戶名': { rich_text: [{ text: { content: '{戶名}' } }] },
      '帳號': { number: {純數字帳號} },
      '地址': { rich_text: [{ text: { content: '{地址}' } }] },
      '聯絡電話': { phone_number: '{電話}' },
      '合作狀態': { select: { name: '進行中' } },
      '供應商': { relation: [{ id: '{STEP3的供應商page_id}' }] },
      '備註': { rich_text: [{ text: { content: '{請款事由、日期、金額；若為代收轉付情境，註明對應關係}' } }] }
    }
  })
}).then(r => r.json()).then(d => console.log(d.id, d.url));
```

**`供應商` relation 一定要填**，連回 STEP 3 的供應商頁面，不要漏掉這個關聯。

若 STEP 2 判斷為代收轉付情境，兩家公司各跑一次 STEP 3~5，並在建立第二家時把第一家的 page id 回填進備註文字裡（Notion 這個備註欄位是 rich_text，用文字描述關聯即可，不需要額外 relation 欄位）。

---

### STEP 6：最終回報

```
✅ 廠商匯款資料建檔完成

🏢 {公司名稱}（{新建/更新供應商記錄}）
🏦 {匯款銀行} {分行}｜戶名：{戶名}｜帳號：{帳號}
📝 備註：{請款事由摘要}

🔗 廠商匯款資料表：{url}
🔗 供應商資料庫：{url}

（若為代收轉付情境，列出兩家公司各自連結，並註明誰是實際收款方）
```

---

## 重要規則

1. **STEP 1 確認公司全名（含繁簡字）後才繼續**，OCR 辨識不完全可信
2. **查重不可跳過**：供應商資料庫、廠商匯款資料表都要各自查一次，避免重複建立
3. **供應商資料庫不放匯款欄位**，匯款資訊只存廠商匯款資料表，兩處分工明確
4. **select 選項用 PATCH 整份取代**，補新選項時要保留舊選項
5. **帳號是 number 類型**，寫入前務必去除破折號、空格、全形字元
6. **代收轉付情境雙邊互相標註**，不能只建收款方或只建開票方其中一邊

---

## 分類

[[Skill目錄]]
