# Obsidian 知識庫設定

> 建立日期：2026-05-16
> 狀態：✅ 運作中

## 是什麼
用 Obsidian 開啟 Tu-agent Dropbox 資料夾作為 vault，作為跨裝置知識庫的閱覽與編輯介面。

## 為什麼做
MEMORY.md、400_Knowledge 等知識庫檔案原本只能在 Claude Code 裡讀取，Obsidian 讓這些檔案有更好的視覺化介面，也可以在手機 Dropbox App 快速查閱。

## Vault 位置
```
~/Library/CloudStorage/Dropbox/Tu-agent/
```
Mac ↔ Windows 同步已由 Dropbox 自動處理，**不需要** Remotely Save 外掛。

## 已安裝外掛

| 外掛 | 用途 |
|------|------|
| Dataview | 自動索引知識庫，用查詢語法列出筆記 |
| Templater | 筆記範本，自動填入日期 |
| Tasks | 任務管理與截止日篩選 |
| Quick Add | 快速新增筆記 |
| Kanban | 看板視圖，追蹤工作流開發進度 |
| Tag Wrangler | 標籤管理 |
| obsidian-git | Git 版控整合（與 GitHub 私有 repo 同步）|

## Templater 範本
位置：`000_Agent/templates/`

| 範本 | 用途 |
|------|------|
| 工作流筆記.md | 記錄 Skill / 腳本 / 系統架構，自動填日期 |
| 日誌.md | 每日工作日誌 |

使用方式：`Cmd+N` 建新筆記 → `Cmd+P` → Templater: Open Insert Template Modal

## kepano Obsidian Skills（Claude Code 用）
位置：`000_Agent/skills/`

| Skill | 用途 |
|-------|------|
| defuddle | 網頁 Markdown 擷取 |
| json-canvas | JSON Canvas 格式操作 |
| obsidian-bases | Obsidian Bases 資料庫查詢 |
| obsidian-cli | Obsidian 指令列整合 |
| obsidian-markdown | Obsidian Markdown 語法 |

## 踩坑紀錄
- 指令面板搜尋 `templater` 前必須先 `Cmd+N` 開新空白筆記，否則出現「Active editor, can't append templates」錯誤
- Obsidian 預設會開到上次的 vault（小克勞德資料庫），需手動切換到 Tu-agent
- Remotely Save 不需要設定 Dropbox OAuth，因為 vault 本身就在 Dropbox 資料夾裡
