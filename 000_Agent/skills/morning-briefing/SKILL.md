---
name: morning-briefing
description: "Gmail＋Slack 早晨簡報：整理主要收件匣、私訊與提及中的今日重要事項；Windows、macOS Codex App 共用，不含行事曆或財經新聞。"
---

# 平日早晨簡報

以繁體中文使用即時 Gmail 與 Slack 產生精簡簡報。預設排程為週一至週五 07:30，Asia/Taipei；手動執行不限時間。Skill 是共用流程，定時觸發由各裝置 Codex App 排程負責。

## 跨系統

以下檔案路徑皆相對於本 SKILL.md 所在資料夾，不是目前工作目錄。使用當前會話實際可用的 Gmail、Slack 讀取工具，依工具結構決定參數，不寫死 MCP 工具名稱、使用者家目錄或 Windows/Mac 指令。不要使用另一個 morning Skill 的行事曆及持股流程。
僅在首次啟用或另一台裝置安裝時讀取 [SETUP.md](SETUP.md)。

## 搜尋

- 查詢前記錄當前 UTC 時間為 search_end_utc。讀取 records/ 下成功 JSON，取最新有效且不在未來的 search_end_utc 為本次 search_start_utc；尚無成功紀錄則回溯 72 小時。失敗、未完成的執行不計成功。
- 先輕量讀取 Gmail 和 Slack。需授權時，直接開啟當前可用的原生連線流程，完成後重試。若任一來源不可用，最終只說明哪個來源不可用，不捏造簡報、不寫成功紀錄、不說「未找到緊急項目」。
- Gmail 僅主要收件匣，使用 in:inbox category:primary -in:spam -in:trash -category:promotions -category:social，加上本次起訖時間。可使用 after: / before: Unix 秒，並核對實際郵件時間。若回傳標籤出現 CATEGORY_UPDATES、CATEGORY_FORUMS、CATEGORY_PROMOTIONS、CATEGORY_SOCIAL，排除該郵件。先取約 10–15 封，僅讀取少數有行動價值的正文。
- Slack 優先私訊、提及、使用者參與的對話串及已知高價值頻道。使用工具支援的時間篩選並核對訊息時間；不要猜使用者 ID 或頻道。
- 僅為理解候選項目的對話串、文件或引用讀取較舊資料。有足夠候選項目判斷前 3–5 項就停止，不详盡搜尋、不湊數。

## 最終格式

只回傳一則最終回覆，不顯示工具、來源檢查、搜尋備註或流程說明。首次建立任務的介紹已完成，勿重複。

# 早晨簡報

## 重點項目
合併兩來源為一份清單，只列今天可能需注意的前 3–5 項，允許少於 3 項。每項包含：內容、重要原因、建議動作、急迫性（立即／今天／本週）、真實直接連結或引用。區分來源事實與建議，不把一般通知自動當成緊急事件。

## 稍後 / 供參
選填，最多 3 點，無助益則省略。

兩來源皆成功查詢且無重要項目時說「未找到緊急項目。」
不包含行事曆或持股新聞。

## 同步報告與紀錄

兩來源皆成功且簡報完成後，將最終 Markdown 保存為 reports/YYYY-MM-DDTHH-mm-ssZ-<唯一識別碼>.md，再以相同檔名保存 records/ 下的 JSON：
{"search_start_utc":"ISO 8601 UTC","search_end_utc":"查詢前記錄的 UTC 時間","completed_at_utc":"ISO 8601 UTC","sources":["gmail","slack"],"report":"reports/對應檔名.md"}
必要時建立 reports/、records/。唯一檔名避免覆寫另一台紀錄；若保存失敗，不宣稱成功時間已保存。

Dropbox 共用流程與資料，不是跨裝置鎖。兩台可以各自手動執行；每天只需一份時，僅在一台啟用排程。不能保證兩台同時觸發不重複，或自動接手離線電腦。已同步紀錄可延續搜尋範圍，不代表即時同步已完成。
