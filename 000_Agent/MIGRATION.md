# AI 大腦遷移手冊

> 由 pro-kit 07 生成 · 2026-05-10
> 未來換新電腦、換新 AI 時，照這份走就能一鍵接管。

---

## 當前架構

| 項目 | 內容 |
|------|------|
| 母體資料夾 | `~/Library/CloudStorage/Dropbox/Tu-agent` |
| 同步管道 | Dropbox（Mac + Windows 混合用戶） |
| GitHub repo | `https://github.com/tuchenghong/Tu-agent.git`（私有） |
| 體檢腳本 | `000_Agent/scripts/sync-health.sh` |
| 檢查頻率 | 每週一次（週五複盤日） |

## ~/.claude/ symlink 對照表

| `~/.claude/` 路徑 | 指向（母體） |
|-------------------|-------------|
| `skills` | `Dropbox/Tu-agent/000_Agent/skills` |
| `settings.json` | `Dropbox/Tu-agent/.claude/settings.json` |
| `commands` | `Dropbox/Tu-agent/.claude/commands` |
| `keybindings.json` | `Dropbox/Tu-agent/.claude/keybindings.json` |

## 情境 1：換一台新 Mac

1. 新 Mac 登入同一個 Dropbox 帳號，等同步完成（可能需要幾分鐘到幾小時）
2. 確認 `~/Library/CloudStorage/Dropbox/Tu-agent/` 已出現
3. 執行以下指令重建 symlink：

```bash
MOTHER="$HOME/Library/CloudStorage/Dropbox/Tu-agent"

# 建立 ~/.claude/ 如不存在
mkdir -p "$HOME/.claude"

# 建立四個 symlink
ln -sf "$MOTHER/.claude/settings.json"    "$HOME/.claude/settings.json"
ln -sf "$MOTHER/.claude/commands"         "$HOME/.claude/commands"
ln -sf "$MOTHER/.claude/keybindings.json" "$HOME/.claude/keybindings.json"
ln -sf "$MOTHER/000_Agent/skills"         "$HOME/.claude/skills"

echo "✅ symlink 建立完成"
```

4. 執行體檢：`bash $MOTHER/000_Agent/scripts/sync-health.sh`
5. 重新登入 Claude Code：`claude auth login`（認證是每台電腦各自的）

## 情境 2：換一台 Windows 電腦

1. 安裝 Dropbox for Windows，等同步完成
2. 找到 Dropbox 路徑（通常是 `C:\Users\你的名字\Dropbox\Tu-agent`）
3. 用 PowerShell（系統管理員）建立 symlink：

```powershell
$MOTHER = "$env:USERPROFILE\Dropbox\Tu-agent"

# 建立 .claude 資料夾
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"

# 建立四個 symlink
New-Item -ItemType SymbolicLink -Force -Path "$env:USERPROFILE\.claude\settings.json"    -Target "$MOTHER\.claude\settings.json"
New-Item -ItemType SymbolicLink -Force -Path "$env:USERPROFILE\.claude\commands"         -Target "$MOTHER\.claude\commands"
New-Item -ItemType SymbolicLink -Force -Path "$env:USERPROFILE\.claude\keybindings.json" -Target "$MOTHER\.claude\keybindings.json"
New-Item -ItemType SymbolicLink -Force -Path "$env:USERPROFILE\.claude\skills"           -Target "$MOTHER\000_Agent\skills"

Write-Host "✅ symlink 建立完成"
```

> **Windows 注意**：需要開發者模式或以系統管理員身份執行 PowerShell。
> 設定方法：設定 → 更新與安全性 → 開發人員專用 → 開發人員模式

4. 重新登入 Claude Code

## 情境 3：換新 AI 大腦（Codex / Gemini / 未來新產品）

你的 `CLAUDE.md` 已是一份 AI 無關的規則文件。要給新 AI 讀，只需要：

1. 確認新 AI 的規則檔命名慣例：
   - Cursor → `.cursorrules`
   - Codex → `AGENTS.md`
   - Gemini CLI → `GEMINI.md`

2. 建立對應的 symlink：
```bash
MOTHER="$HOME/Library/CloudStorage/Dropbox/Tu-agent"
ln -s "$MOTHER/CLAUDE.md" "$MOTHER/AGENTS.md"   # 給 Codex
ln -s "$MOTHER/CLAUDE.md" "$MOTHER/GEMINI.md"   # 給 Gemini CLI
```

3. Skills / memory 的復用程度取決於新 AI 是否支援同等機制

## 情境 4：從備份還原（出事時）

```bash
# 移除當前損壞的 .claude/
rm -rf ~/.claude

# 從備份還原
mv ~/claude-backup-YYYYMMDD-HHMMSS ~/.claude

# 然後重新規劃再跑一次 pro-kit 07
```

備份位置：`~/claude-backup-20260510-151735`（pro-kit 07 執行時建立）

---

> 如有任何問題，先跑 `000_Agent/scripts/sync-health.sh` 診斷。
