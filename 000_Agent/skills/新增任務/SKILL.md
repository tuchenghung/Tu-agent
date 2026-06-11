---
name: 新增任務
description: "新增任務至 Notion 行動任務資料庫。觸發方式：使用者說「新增任務 XXX」或「/新增任務 XXX」。同步建立 Notion 任務 + 本地 TaskCreate。若有截止日，自動建立 Google Calendar 提醒。"
---

# 新增任務 SOP

## 資料庫 ID

| 資料庫 | ID |
|--------|-----|
| Notion 行動任務資料庫 | `8847aebd-089f-82d9-8e4b-816bddc1192a` |
| Notion 案件財務管理（專案） | `2f97aebd-089f-80f7-9607-df6dc41ab3bd` |

## 觸發方式

- `/新增任務 任務名稱`
- 使用者說「新增任務 XXX」

---

## 執行步驟

### STEP 1：解析任務名稱

從使用者輸入取得：
- `$TASK_NAME`：任務名稱（必填）
- 若未附任務名稱，直接問「任務名稱是什麼？」

---

### STEP 2：詢問截止日與描述（可選）

用 **AskUserQuestion** 詢問：

**問題 1**：「這個任務有截止日嗎？」
- 選項：今天 / 明天 / 本週五 / 自訂日期 / 無截止日

若選「自訂日期」→ 請使用者用文字回覆日期（格式：YYYY-MM-DD 或中文如「6/20」）

**問題 2**：「要關聯到哪個專案？」（可與問題 1 合併為多問題 AskUserQuestion）
- 選項：南港GTP / 羅東聖母S棟 / 龍潭廠 / 不關聯 / 我來輸入

若使用者選「不關聯」或無明確答案 → 跳過專案關聯。

---

### STEP 3：建立 Notion 任務

使用 `mcp__notion__API-post-page` 建立：

```json
{
  "parent": { "database_id": "8847aebd-089f-82d9-8e4b-816bddc1192a" },
  "properties": {
    "行動任務卡片": { "title": [{ "text": { "content": "$TASK_NAME" } }] },
    "行動狀態": { "status": { "name": "尚未開始" } },
    "截止日": { "date": { "start": "YYYY-MM-DD" } },
    "問題／目標": { "rich_text": [{ "text": { "content": "$DESCRIPTION" } }] },
    "專案項目": { "relation": [{ "id": "$PROJECT_PAGE_ID" }] }
  }
}
```

- `截止日` 若無則省略該欄位
- `問題／目標` 若無描述則省略或填空
- `專案項目` 若不關聯則省略

---

### STEP 4：建立本地 TaskCreate

```
TaskCreate(
  subject: "$TASK_NAME",
  description: "Notion 任務已建立。截止日：$DEADLINE（若有）"
)
```

---

### STEP 5：若有截止日 → 建立 Google Calendar 提醒

使用 `mcp__google-calendar__create-event`：
- 標題：`📋 $TASK_NAME`
- 日期：截止日當天（全天事件）
- 提醒：前一天 + 前一小時（per 記憶庫設定）

---

### STEP 6：回報完成

```
✅ 任務已建立

📋 任務名稱：$TASK_NAME
📅 截止日：$DEADLINE（若無則「無」）
🔗 Notion：https://www.notion.so/$PAGE_ID
📌 Google Calendar：已設前一天＋前一小時提醒（若有截止日）
```

---

## 常用專案 page_id 對照

| 案件 | page_id |
|------|---------|
| 南港實驗室GTP實驗室修改工程 | `3057aebd-089f-8017-9b12-d90b5e31933e` |
| 博訊龍潭廠1、4F裝修工程 | （從案件財務管理 DB 查詢） |
| 羅東聖母S棟病房整修 | （從案件財務管理 DB 查詢） |

---

## 注意事項

1. `行動狀態` 預設值為「尚未開始」
2. 截止日若使用者給中文日期（如「6/20」）→ 轉換為 `2026-06-20`
3. 若使用者說「今天」→ 用當天日期；「明天」→ +1 天；「本週五」→ 計算當週五
4. Google Calendar 提醒規則 → 前一天全天行程＋前一小時提醒（固定，不需詢問）
