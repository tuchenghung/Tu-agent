---
name: 新增任務
description: "新增任務至 Notion 行動任務資料庫。觸發方式：使用者說「新增任務 XXX」或「/新增任務 XXX」。同步建立 Notion 任務 + 本地 TaskCreate。若有截止日，自動建立 Google Calendar 提醒。"
---

# 新增任務 SOP

## 資料庫 ID

| 資料庫 | ID |
|--------|-----|
| Notion Tasks（行動任務庫） | `f1dc0829-774c-493a-aa21-eefc6e35b034` |
| Notion Projects（專案與指標） | `3355cac1-0351-4ef4-8eb1-8b8f0bb619c3` |

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

### STEP 2：詢問截止日與專案（**兩題都必問，不得跳過**）

用 **AskUserQuestion** 一次送出兩個問題：

**問題 1**：「這個任務有截止日嗎？」
- 選項：今天 / 明天 / 本週五 / 自訂日期 / 無截止日

若選「自訂日期」→ 請使用者用文字回覆日期（格式：YYYY-MM-DD 或中文如「6/20」）

**問題 2（必問）**：「要關聯到哪個專案？」
- 選項：南港GTP / 龍潭廠 / 羅東聖母 / 不關聯 / 我來輸入

**問題 3（必問）**：「任務優先級？」
- 選項：緊急重要 / 重要不緊急 / 緊急不重要 / 不重要不緊急

⚠️ **問題 2、3 不得省略**，即使使用者未提也必須詢問。
若使用者選「不關聯」→ 跳過 Project 欄位。

---

### STEP 3：建立 Notion 任務

使用 `mcp__notion__API-post-page` 建立：

```json
{
  "parent": { "database_id": "f1dc0829-774c-493a-aa21-eefc6e35b034" },
  "icon": { "type": "emoji", "emoji": "📋" },
  "properties": {
    "任務": { "title": [{ "text": { "content": "$TASK_NAME" } }] },
    "狀態": { "status": { "name": "待處理" } },
    "Deadline": { "date": { "start": "YYYY-MM-DD" } },
    "備註": { "rich_text": [{ "text": { "content": "$DESCRIPTION" } }] },
    "優先級": { "select": { "name": "$PRIORITY" } },
    "Project": { "relation": [{ "id": "$PROJECT_PAGE_ID" }] }
  }
}
```

- `Deadline` 若無則省略該欄位
- `備註` 若無描述則省略
- `Project` 若不關聯則省略

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

## 常用專案 page_id 對照（來自 Projects（專案與指標）DB）

| 案件 | page_id |
|------|---------|
| 南港實驗室GTP實驗室修改工程 | `3627aebd-089f-81e9-b146-ffc433daf3f0` |
| 博訊龍潭廠1、4F裝修工程 | `3627aebd-089f-816c-b0ee-e3eb4906cc49` |
| 博訊龍潭廠1 4F改修追加工程 | `3627aebd-089f-8105-af62-c67aee029abd` |
| 羅東聖母醫院S棟5樓耳鼻喉科整修工程 | `367c47de-5bd0-4dd6-85b6-817d2c23975a` |
| 南崁廠房高架地板工程 | `3797aebd-089f-81f4-9bc2-d8a3900c9561` |
| 市醫和平院區醫療大樓8樓婦兒科病房整修工程 | `adcbd1bd-8636-4ae9-a1a4-219d7557e96d` |

---

## 注意事項

1. `狀態` 預設值為「待處理」（選項：待處理 / 進行中 / 卡住 / 完成）
2. 截止日若使用者給中文日期（如「6/20」）→ 轉換為 `2026-06-20`
3. 若使用者說「今天」→ 用當天日期；「明天」→ +1 天；「本週五」→ 計算當週五
4. Google Calendar 提醒規則 → 前一天全天行程＋前一小時提醒（固定，不需詢問）
5. **勿使用 `8847aebd`（雷蒙的行動任務庫），那是第三方模板系統**


---

## 分類

[[Skill目錄]]
