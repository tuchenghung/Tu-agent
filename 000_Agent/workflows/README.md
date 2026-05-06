# workflows/ — 你每天主動喊的固定儀式

這個資料夾放「你手動打一次、AI 就跑一整套流程」的多步驟工作流，例如 `/morning`、`/journal`、`/quote-import`。

## 跟 skills/ 差在哪？

- **skills** 是「方法論 + SOP」，會被其他任務引用（例如工程估價技巧、Notion 操作手冊）
- **workflows** 是「每天的固定儀式」，會**串接多個 skill** 一次跑完

所以一個 workflow 常常長這樣：
> `/morning` → 讀信件（用 email skill）→ 查行事曆（用 calendar skill）→ 整理成今日任務清單

## 怎麼讓 workflow 變成 slash 指令？

workflow 檔案本身不在 Claude Code 自動掃描的位置，所以你需要**在 `.claude/commands/` 放一個 shim 檔案**，或直接放在 `~/.claude/skills/` 讓它被掃到。
