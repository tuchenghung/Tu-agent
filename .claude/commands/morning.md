# 早晨日報

今天日期：使用 Bash 取得當前日期（`date +%Y-%m-%d`）。
昨天日期：`date -v-1d +%Y-%m-%d`

---

## 執行步驟

### Step 0：偵測平台

用 Bash 執行 `uname -s 2>/dev/null || echo Windows` 判斷平台：
- 結果為 `Darwin` → **Mac 模式**：後續使用 `mcp__gmail__`、`mcp__google-calendar__`、`mcp__notion__`
- 結果為其他（Windows / MINGW / Linux 等）→ **Windows 模式**：後續使用 `mcp__gmail-win__`、`mcp__calendar-win__`、`mcp__notion-win__`

Windows 模式下，Apple 提醒事項（Step 5）直接略過，標註「Windows 裝置不支援」。

---

### Step 1：取得日期

用 Bash 取得：
- Mac：`TODAY=$(date +%Y-%m-%d)` / `YESTERDAY=$(date -v-1d +%Y-%m-%d)`
- Windows：`TODAY` 用 `date +%Y-%m-%d`，`YESTERDAY` 用 `date -d "yesterday" +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d -d "-1 day"`
- 今天星期幾：`date +%A`（轉成中文）

---

### Step 2：Gmail — 昨日郵件

- **Mac 模式**：使用工具 `mcp__gmail__search_emails`
- **Windows 模式**：使用工具 `mcp__gmail-win__search_emails`

執行以下兩個搜尋（可並行）：

1. **昨天收到的郵件**
   - query: `after:YESTERDAY before:TODAY in:inbox`
   - maxResults: 20

2. **昨天我發出的郵件**
   - query: `after:YESTERDAY before:TODAY in:sent`
   - maxResults: 10

整理結果：
- 列出寄件人、主旨
- 標記是否「需要回覆」（判斷標準：對方有提問、有要求、有等待你回應）
- 若郵件數量為 0，直接說明「昨日無郵件」

---

### Step 3：Google Calendar — 昨天與今天行程

- **Mac 模式**：使用工具 `mcp__google-calendar__list-events`
- **Windows 模式**：使用工具 `mcp__calendar-win__list-events`

執行以下兩個查詢（可並行）：

1. **昨天行程**
   - timeMin: `YESTERDAY`T00:00:00+08:00
   - timeMax: `YESTERDAY`T23:59:59+08:00
   - singleEvents: true
   - orderBy: startTime

2. **今天行程**
   - timeMin: `TODAY`T00:00:00+08:00
   - timeMax: `TODAY`T23:59:59+08:00
   - singleEvents: true
   - orderBy: startTime

---

### Step 4：Notion — 任務與專案狀態

- **Mac 模式**：使用工具 `mcp__notion__API-post-search`
- **Windows 模式**：使用工具 `mcp__notion-win__API-post-search`

執行兩個搜尋（可並行）：

1. **近期更新的頁面**（了解昨天工作進度）
   - query: `""`（空字串，取最近修改）
   - filter: `{"value": "page", "property": "object"}`
   - sort: `{"direction": "descending", "timestamp": "last_edited_time"}`
   - page_size: 10

2. **搜尋進行中任務**
   - query: `"進行中"`
   - filter: `{"value": "page", "property": "object"}`
   - page_size: 10

整理結果：
- 昨天有修改的頁面標題 + 最後修改時間
- 進行中的任務/專案名稱

---

### Step 5：Apple 提醒事項

**Mac 模式**：使用工具 Bash，執行以下指令：

```bash
osascript -e '
tell application "Reminders"
  set output to ""
  repeat with l in lists
    repeat with r in reminders of l
      if completed of r is false then
        set dueStr to ""
        if due date of r is not missing value then
          set dueStr to " [截止：" & (due date of r as string) & "]"
        end if
        set output to output & "[" & name of l & "] " & name of r & dueStr & "\n"
      end if
    end repeat
  end repeat
  return output
end tell'
```

整理結果：
- 列出清單名稱 + 提醒事項名稱 + 截止日期（若有）
- 若無任何提醒，標明「無待辦提醒」

**Windows 模式**：直接略過此步驟，在報告中標記「提醒事項：Windows 裝置不支援，請至 Mac 查看」。

---

### Step 6：彙整輸出早晨日報

用以下格式輸出（繁體中文，精確，不廢話）：

---

## ☀️ 早晨日報 — [TODAY 日期，星期X]

### 📋 昨日工作回顧

**行事曆（昨天）**
- [昨天的會議與行程，若無則標明「無行程」]

**重要郵件（昨天）**
- [寄件人] — [主旨]（待回覆 ✉️ / 已閱）
- [若無郵件，標明「無新郵件」]

**Notion 更新**
- [昨天修改的頁面/任務，附最後修改時間]

---

### 📌 今日重要任務

**今日行程**（依時間排序）
- HH:MM [活動名稱]
- [若無行程，標明「今日無排程」]

**待辦 / 截止**
- [需要回覆的郵件]
- [Notion 中進行中的任務]
- [Apple 提醒事項，有截止日者優先列出（Mac 限定）]

**工程專案提醒**
- [Notion 中進行中的工程相關專案，若有尺寸/金額/截止日請照實列出]

---

### ⚡ 需要立即處理
- [最優先 1-3 件，依緊急度排序]

---

**執行原則：**
- 數字、日期、規格要精確，不要模糊帶過
- 若某服務無資料，一行說明即可，不填廢話
- 所有時間用 24 小時制，台灣時區 (UTC+8)
