---
name: 新增任務
description: "新增任務並同步三個平台：Claude TaskCreate + Google Calendar 提醒 + Notion 專案頁 to_do。觸發方式：使用者說「新增任務 XXX」或「幫我記一個任務 XXX」，可帶截止日與優先級。"
---

# 新增任務 SOP

使用者新增任務時，**三個平台必須同步**，缺一不可：
1. Claude TaskCreate（session 追蹤）
2. Google Calendar（截止日提醒，有 deadline 才建）
3. Notion 專案頁面（to_do block，有對應專案才加）

---

## 執行步驟

### STEP 1：解析輸入

從使用者輸入取得：
- `$TASK_NAME`：任務名稱
- `$DEADLINE`：截止日（YYYY-MM-DD，若有）
- `$PRIORITY`：優先級（緊急重要 / 重要不緊急 / 緊急不重要 / 一般）

若 deadline 未明確指定，詢問：「這個任務有截止日嗎？」

---

### STEP 2：建立 Claude Task

使用 `TaskCreate`：
- subject：`$TASK_NAME`
- description：任務說明，含優先級與截止日

---

### STEP 3：建立 Google Calendar 提醒（有 deadline 才執行）

使用 `mcp__google-calendar__create-event`：
- calendarId：`primary`
- summary：`⚠️ $TASK_NAME（$PRIORITY）`（無優先級則省略括號）
- start：`$DEADLINE`（全天行程格式 YYYY-MM-DD）
- end：`$DEADLINE + 1 天`
- reminders：`useDefault: false`，overrides：前一天 1440 分鐘 + 前一小時 60 分鐘，均為 popup

---

### STEP 4：Notion 專案頁面新增 to_do（有對應專案才執行）

若任務與特定案件相關（從任務名稱或使用者說明判斷）：

1. 找出對應的 Notion Projects 頁面 ID（DB：`3355cac1-0351-4ef4-8eb1-8b8f0bb619c3`）
   - 從 session 記憶中找（若之前已建立或提及該專案）
   - 或詢問：「這個任務屬於哪個專案？」

2. 使用 Notion API PATCH blocks children，新增 to_do block：
```json
{
  "object": "block",
  "type": "to_do",
  "to_do": {
    "rich_text": [{"type": "text", "text": {"content": "📋 $TASK_NAME — 截止 $DEADLINE（$PRIORITY）"}}],
    "checked": false
  }
}
```

若找不到對應專案或任務無關聯專案，跳過此步驟（不影響 STEP 2、3）。

---

### STEP 5：回報結果

```
✅ 任務建立完成

任務：$TASK_NAME
優先級：$PRIORITY
截止日：$DEADLINE

✅ Claude Task #N 已建立
✅ Google Calendar：$DEADLINE（前一天+前一小時提醒）
✅ Notion to_do：已加入 $PROJECT_NAME 頁面
   （若無對應專案則顯示「無關聯專案，已跳過」）
```

---

## 關鍵常數

| 項目 | 值 |
|------|-----|
| Notion Projects DB | `3355cac1-0351-4ef4-8eb1-8b8f0bb619c3` |
| Google Calendar ID | `primary` |
| 提醒設定 | 前一天 popup (1440 min) + 前一小時 popup (60 min) |
