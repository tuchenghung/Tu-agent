# 雙系統 Codex App 啟用

Dropbox 同步整个 Tu-agent。主流程在 000_Agent/skills/morning-briefing/SKILL.md，Codex 專案入口在 .agents/skills/morning-briefing/SKILL.md，以相對路徑銜接，不需跨系統符號連結。

在 Windows 或 Mac 的 Codex App 加入並開啟該台實際的 Tu-agent 資料夾。等待 Dropbox 將上述檔案下載到本機，建議設為離線可用。在新任務輸入：
「使用 morning-briefing Skill 產生今天的早晨簡報。」
若 Skill 未出現，重新開啟 Codex，或明確要求讀取 000_Agent/skills/morning-briefing/SKILL.md 並執行。
該台 App 必須有可用 Gmail、Slack 連線。本機授權要各自確認，不能只靠同步檔案。

## 排程

Skill 不會自行啟動。Windows 既有「平日早晨簡報」會指向這份流程。Mac 尚未安裝或驗證；安裝後在已開啟 Tu-agent 的 Codex 任務貼上：

「請先檢查本機是否已有『平日早晨簡報』排程，有就更新，沒有才建立。每週一至週五 Asia/Taipei 上午 07:30，讀取此專案的 000_Agent/skills/morning-briefing/SKILL.md 並執行，每次讀取最新內容。請使用這台電腦實際的 Tu-agent 路徑。來源失敗就如實回報，不寫成功紀錄。先手動執行驗證 Gmail 與 Slack 是否可用。」

每天只需一份簡報時，選一台負責定時執行，另一台可手動使用；切換負責電腦時停用原機排程，再啟用另一台。兩台皆啟用可能重複執行；Dropbox 不提供即時排程協調或離線自動接手。
本機執行需保持電腦可用與 App 運行。不直接同步 ~/.codex 的對話資料庫、target_thread_id 或授權檔到另一台。

參考：https://learn.chatgpt.com/docs/build-skills
https://learn.chatgpt.com/docs/automations
