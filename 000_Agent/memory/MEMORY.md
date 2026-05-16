<!-- AI 分身起始助手紀錄:START -->
<!-- AI 分身起始助手 by 雷小蒙 v1.2 · 2026-05-06 · by 雷蒙（Raymond Hou）· https://github.com/Raymondhou0917/claude-code-resources · CC BY-NC-SA 4.0 -->

# 裝修工程接案主管的 AI 分身記憶

> 這裡存我跟 AI 之間跨 session 的偏好、經驗、踩坑紀錄。
> AI 每次 session 開始會自動讀這個檔案。

---

## 用戶偏好

（還是空的，等你跟 AI 合作幾次後自然會長出來）

---

## Feedback（AI 學到的原則）

- **雙系統隔離原則**：使用者同時有 Windows 11（PC）與 macOS（MacBook Pro M3 Pro），兩邊透過 Dropbox 同步專案資料夾。在 Windows 操作時不得修改 Mac 專屬設定（如 `~/.nvm/`、Mac 路徑的 MCP 設定）；在 Mac 操作時同理不動 Windows 設定（如 `C:\Users\deco01\nodejs\`、`-win` 結尾的 MCP 設定）。設定檔若有平台差異，以當前執行平台為準，不要跨平台套用。

---

## 工作流 SOP

### /project-import — 工程專案資料夾匯入
- **觸發**：使用者提供 Dropbox 專案資料夾路徑
- **功能**：自動掃描 → 依 A-I 分類移檔 → 建 Notion 專案頁面 → 建折疊標題
- **Skill 檔**：`.claude/commands/project-import.md`
- **關鍵**：heading_2 toggleable 需用 Node.js 直接呼叫 Notion API（MCP 工具不支援）
- **Notion Projects DB**：`3355cac1-0351-4ef4-8eb1-8b8f0bb619c3`
- **實際驗證案例**：羅東聖母醫院S棟5樓耳鼻喉科（2026-05-15）、南投基督教醫院（2026-05-15）

---

## Dropbox API

| 項目 | 值 |
|---|---|
| 申請頁面 | https://www.dropbox.com/developers/apps |
| Token 有效期 | 約 4 小時，需手動重新產生 |
| Token 位置 | Settings → OAuth 2 → Generate access token |
| 必要 Permission | `sharing.write`（在 Permissions 頁籤勾選）|
| 建立/取得分享連結腳本 | `D:\Dropbox\Tu-agent\000_Agent\scripts\dropbox_notion_links.mjs` |

---

## 踩坑筆記

- `mcp__notion-win__API-patch-block-children` 只支援 `paragraph` / `bulleted_list_item`，無法建立 `heading_2 toggleable`。需用 Node.js + Notion REST API 直接建立。

---

## 環境速查表

| 項目             | 值                                             |
| :--------------- | :--------------------------------------------- |
| AI 分身母資料夾  | `/Users/tuzhenghong/Tu-agent`（symlink → `~/Dropbox/Tu-agent`） |
| 建立日期         | `2026-04-30`                                   |
| Skills symlink   | ✅ `~/.claude/skills` → `000_Agent/skills/`    |
| 記憶系統啟用     | ✅                                             |
| 日記功能         | ✅ `300_Journal/` 已建立                       |

<!-- AI 分身起始助手紀錄:END -->
