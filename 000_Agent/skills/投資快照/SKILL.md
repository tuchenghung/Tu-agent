---
name: 投資快照
description: "收到台股或美股持倉快照截圖後，自動完成：存本機快照 → 更新投資週報資料庫 → 更新台股/美股研究頁 callout → 新增持倉總覽 toggle → 處理新個股/加碼。觸發方式：使用者提供持倉截圖，或直接輸入 /投資快照。"
---

# 投資快照 SOP

## Notion 頁面 ID

| 名稱 | ID |
|------|-----|
| 投資週報資料庫 | `3697aebd-089f-810b-9874-f0aac05dff26` |
| 台股研究頁面 | `3697aebd-089f-8103-971e-c1cd95307c82` |
| 美股研究頁面 | `3697aebd-089f-811a-991c-ebe43bdc1a71` |

## 台股研究頁 callout block ID

| 區塊 | ID |
|------|-----|
| 獲利（綠色） | `02bd56ff-46a5-4da5-b7b7-b38e444c61f3` |
| 虧損（紅色） | `fbce3e1a-e137-4eef-b26b-6db25af9ffd4` |

## 美股研究頁 callout block ID

| 區塊 | ID |
|------|-----|
| 摘要（藍色） | `3697aebd-089f-8121-9c92-fbad9bdc693f` |
| 獲利（綠色） | `3697aebd-089f-8184-86a1-ed6d4d4c764c` |
| 虧損（紅色） | `3697aebd-089f-8101-bdda-fc7fb85065f1` |

---

## 台股快照完整流程（6 步，缺一不可）

### STEP 1：存本機快照

存 `500_Investment/持倉快照/YYYY-MM-DD.md`，內容包含：
- 損益總覽表（總市值、估總損益、獲利/虧損檔數）
- 完整持倉明細表（股票/類別/股數/現價/均價/市值/損益/損益%/損益平衡價）
- vs 上次快照變化表

---

### STEP 2：投資週報資料庫新增一筆

使用 `mcp__notion__API-post-page` 在投資週報資料庫建立頁面，並用 Node.js 在頁面內加入持倉表格 + 變化表 children blocks：

```js
// 投資週報頁面屬性
{
  "快照日期": { "title": [{ "text": { "content": "YYYY-MM-DD（台股）" } }] },
  "總市值（元）": { "number": 數值 },
  "總損益（元）": { "number": 數值 },
  "損益%": { "number": 小數（如0.179） },
  "獲利檔": { "number": 數值 },
  "虧損檔": { "number": 數值 },
  "持股數": { "number": 數值 },
  "損益週變化（元）": { "number": 數值 },
  "市值週變化（元）": { "number": 數值 },
  "備註": { "rich_text": [{ "text": { "content": "vs 上次摘要..." } }] }
}
```

建立後用 Node.js 加入完整持倉表格（8欄）+ 變化表（4欄）作為 children blocks。

---

### STEP 3：更新台股研究頁兩個 callout

用 Node.js/curl（MCP 不支援 callout 更新）：

```js
// 獲利 callout（綠色）
{ callout: { rich_text: [{ text: { content: "獲利部位（N 檔）\n台達電 +X%　..." } }], icon: { type: "emoji", emoji: "📈" }, color: "green_background" } }

// 虧損 callout（紅色）
{ callout: { rich_text: [{ text: { content: "虧損部位（N 檔）\n森崴能源 -X%　..." } }], icon: { type: "emoji", emoji: "⚠️" }, color: "red_background" } }
```

---

### STEP 4：台股研究頁新增 snapshot toggle

用 Node.js 在台股研究頁插入新 toggle（使用 `after` 參數插在上次快照 toggle 後面）：

```
toggle 標題：📊 持倉總覽（YYYY-MM-DD 快照）　市值 NT$X,XXX,XXX　總損益 +XXX,XXX（+X%）
toggle 內容：完整持倉表格（8欄）
```

**注意：toggle 要插在上次快照 toggle 後面，不是頁面最底部。**

---

### STEP 5：有新個股

**情況 A：全新個股（首次買入）**
1. 用 `POST /pages`（parent: 台股研究頁 ID）建立新子頁，內含持倉數據表
2. 建立 `500_Investment/個股/股票名.md`（格式對齊其他個股）
3. 個股頁面內建立「零股買進明細」表，加入第一筆買入記錄

**情況 B：已持有但快照首次出現（有個股研究頁）**
1. 在個股研究頁頂部（公司描述後）新增持倉更新區塊：持倉數據表 + divider
2. 在「零股買進明細」末尾加一筆，更新筆數標題

---

### STEP 6：有加碼

1. 更新 `500_Investment/個股/股票名.md`（股數、成本、損益）
2. 在個股研究頁「零股買進明細」末尾加一筆，更新筆數標題（N筆 → N+1筆）

---

## 美股快照完整流程（5 步，缺一不可）

### STEP 1：存本機快照

存 `500_Investment/持倉快照/YYYY-MM-DD_美股.md`，內容包含：
- 損益總覽（USD + TWD換算，匯率記錄）
- ETF 配置表 + 個股分主題表
- vs 上次快照變化表

---

### STEP 2：投資週報資料庫新增一筆

同台股，但數值換算為 TWD（USD × 匯率），標題為 `YYYY-MM-DD（美股）`，icon 用 🇺🇸。

---

### STEP 3：更新美股研究頁三個 callout

用 Node.js/curl 更新：
- 摘要 callout（藍色）：總市值 $X,XXX、總損益 +$X,XXX（+X%）、獲利N檔、虧損N檔、快照日期
- 獲利 callout（綠色）：獲利部位清單 + 損益%
- 虧損 callout（紅色）：虧損部位清單 + 損益%

---

### STEP 4：美股研究頁新增 snapshot toggle

用 Node.js 插入新 toggle（after 上次快照 toggle），toggle 內加完整持倉表格（8欄）。

---

### STEP 5：有新個股

同台股 STEP 5 邏輯，parent 改為美股研究頁 ID。

---

## 零股買入規則

| 情況 | 動作 |
|------|------|
| **已持有** → 加碼/再買 | 個股研究頁「零股買進明細」末尾加一筆，更新筆數（N筆→N+1筆） |
| **全新個股** | 建新子頁 + 建 .md + 個股頁建完整結構（見下方格式） |

零股買進明細欄位格式：**成交日期 / 股數 / 成交價 / 成本（元）/ 委託書號**
- 委託書號若無填「—」
- 不新增其他額外區段

---

## 新個股 Notion 頁面完整結構

參考格式：森崴能源（6806）、台船（2208）

```
1. 公司描述（paragraph）— 說明公司業務與定位
2. paragraph：═══ 近五年財報（2021–2025）═══
3. table（5欄）：年度 / 營收（億）/ EPS / ROE / 股息
4. paragraph：══════ 持倉狀況 ══════
5. bullets：持有股數、均價、現價、損益%
6. paragraph：══════ 公司業務 ══════
7. bullets：主要業務項目
8. paragraph：══════ 投資亮點 ══════
9. bullets：買進理由
10. paragraph：══════ 投資風險 ══════
11. bullets：主要風險
12. paragraph：═══ 零股買進明細（N 筆）═══
13. table（5欄）：成交日期 / 股數 / 成交價 / 成本（元）/ 委託書號
```

### 財報數據來源
- EPS：https://histock.tw/stock/{股票代號}/%E6%AF%8F%E8%82%A1%E7%9B%88%E9%A4%98（用 Playwright 抓）
- MOPS（官方）：https://mops.twse.com.tw/mops/#/web/home

### 加碼時（已有頁面）
在公司描述後插入：
1. paragraph：`══════ 持倉更新（YYYY-MM-DD）══════`
2. table（2欄）：項目 / 數值（股數、現價、均價、成本、損益、獲利率、損益平衡價）
3. divider

---

## 個股 .md 格式規則

- 格式與現有個股一致（含研究連結區段，不特立獨行）
- 狀態欄位：獲利中 / 虧損中（不用「微幅虧損」等自創詞）
- 每次快照後確認：`500_Investment/個股/` 檔案數 = 快照筆數

---

## API 技術備注

- **callout / toggle 更新**：MCP 不支援，必須用 Node.js 直接呼叫 Notion REST API
- **新增持倉表格**：用 Node.js `PATCH /blocks/{id}/children` 加 table block
- **toggle 位置**：用 `after: {上次toggle_id}` 參數插入，不 append 到頁面底部
- **新個股子頁**：用 `POST /pages`（parent: `{ page_id: 研究頁ID }`）建立
- **.env 路徑**：`/Users/tuzhenghong/Library/CloudStorage/Dropbox/Tu-agent/.env`
