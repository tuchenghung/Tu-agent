# 長期記憶與資料入口

## 用戶偏好

- **共用資料根目錄（2026-09-07）**：使用者指定 `D:\Dropbox\Tu-agent` 為 AI Agent 資料存放資料夾，Markdown 資料及未來新增的工作資料皆存放於此，依既有資料層路由分類。Claude Code 也使用同一份資料；修改共用檔案前須重新讀取，避免覆蓋其他工具的新內容，並遵守 Windows / macOS 設定隔離原則。

---
- AI PM／AI Tech Lead／Workflow Architect、台灣繁體中文及模型調度授權，統一見 [AGENTS.md](../../AGENTS.md)，不重複維護條文。
- 2026-09-08 已同意：明確且已授權工作直接執行；複雜但明確的需求自行拆解，必要歧義才提問；只回顧相關進度，不每次詢問反思日誌。

## Feedback

- **Agent 分工澄清（2026-09-07）**：過度以兩個 Agent 同時修改同一任務為前提提醒 → 使用者會讓 Codex 與 Claude Code 處理不同任務，按此分工正常共用資料 → 不必反覆提醒同任務衝突；共用記憶與規則檔仍須在修改前讀取最新內容。
- **雙系統隔離原則**：使用者同時有 Windows 11（PC）與 macOS（MacBook Pro M3 Pro），兩邊透過 Dropbox 同步專案資料夾。在 Windows 操作時不得修改 Mac 專屬設定（如 `~/.nvm/`、Mac 路徑的 MCP 設定）；在 Mac 操作時同理不動 Windows 設定（如 `C:\Users\deco01\nodejs\`、`-win` 結尾的 MCP 設定）。設定檔若有平台差異，以當前執行平台為準，不要跨平台套用。
- [建立 Notion 資源前先查重](feedback_check_before_create.md) — 建 database/page 前用 `API-get-block-children` 確認頁面上無同名資源，避免重複建立。

---

## 專案入口

- **士林 TOD 商場 3D**：1–5F示意模型完成，各層高6m/板厚15cm，標高0/6/12/18/24m；最新含樓梯手扶梯示意成果 `100_Todo/projects/shilin-tod-3d/model_1F_5F_stairs/`，接續讀專案紀錄。樓板輪廓、開口與牆體仍待核定。

- **郵政大樓 3D**：正式位置 `D:/Dropbox/宏祐/施工中案件/20260618-中華郵政臺北郵件處理中心整修統包工程/K施工圖面/3D專案`，讀取其中 `專案紀錄.md`。使用者確認為一樓，牆柱高度 5 m；後續成果存正式位置。Tu-agent 的 `100_Todo/projects/postal-3d/` 僅為工作備份。

## 按需檢索

- [工程知識索引與待辦](../reference/工程知識索引.md)：無塵室空調文件、歷史報價係數、尚待指示的程式更新；不自動套用歷史數值。
- [整合工具經驗](../reference/整合工具經驗.md)：project-import、Dropbox／Notion 歷史 SOP 與限制。
- [環境與工具紀錄](../reference/環境與工具設定紀錄.md)：平台路徑與工具歷史設定，實際能力以當次環境為準。
- [使用者背景](../reference/使用者背景.md)：工程、投資、家庭與工具偏好。
- 每日進度：`daily/YYYY-MM-DD.md`；專案細節查各專案紀錄。

<!-- 原記憶源自 AI 分身起始助手 by 雷小蒙 v1.2，雷蒙 Raymond Hou，https://github.com/Raymondhou0917/claude-code-resources ，CC BY-NC-SA 4.0。2026-09-08 整併，原文保留於 000_Agent/archive/2026-09-08_rules-before-consolidation/。 -->
