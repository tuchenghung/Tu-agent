# windows-startup-check.ps1
# Claude Code 跨裝置同步 — Windows 開機自動偵測
# 放在 Dropbox 裡，由 windows-startup-reminder.bat 呼叫
# 已設定完成後會靜默退出，不再跳視窗

$ErrorActionPreference = "SilentlyContinue"

# ── 偵測 symlink 狀態 ──────────────────────────────────────────────
$claudeDir  = "$env:USERPROFILE\.claude"
$skillsLink = Join-Path $claudeDir "skills"
$settingsLink = Join-Path $claudeDir "settings.json"

function Is-Symlink($path) {
    $item = Get-Item $path -Force -ErrorAction SilentlyContinue
    return ($item -ne $null) -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
}

$skillsOk   = Is-Symlink $skillsLink
$settingsOk = Is-Symlink $settingsLink

# ── 已設定完成 → 靜默退出 ──────────────────────────────────────────
if ($skillsOk -and $settingsOk) { exit 0 }

# ── 找 Dropbox 母體路徑 ────────────────────────────────────────────
$possiblePaths = @(
    "$env:USERPROFILE\Dropbox\Tu-agent",
    "$env:USERPROFILE\OneDrive\Dropbox\Tu-agent"
)
$MOTHER = $null
foreach ($p in $possiblePaths) {
    if (Test-Path $p) { $MOTHER = $p; break }
}

$motherStatus = if ($MOTHER) { "✅ 找到：$MOTHER" } else { "❌ 尚未找到（Dropbox 可能還在同步）" }

# ── 組合設定指令 ───────────────────────────────────────────────────
if ($MOTHER) {
    $setupCmd = @"
`$MOTHER = "$MOTHER"
New-Item -ItemType Directory -Force -Path "`$env:USERPROFILE\.claude" | Out-Null
New-Item -ItemType SymbolicLink -Force -Path "`$env:USERPROFILE\.claude\settings.json"    -Target "`$MOTHER\.claude\settings.json"
New-Item -ItemType SymbolicLink -Force -Path "`$env:USERPROFILE\.claude\commands"         -Target "`$MOTHER\.claude\commands"
New-Item -ItemType SymbolicLink -Force -Path "`$env:USERPROFILE\.claude\keybindings.json" -Target "`$MOTHER\.claude\keybindings.json"
New-Item -ItemType SymbolicLink -Force -Path "`$env:USERPROFILE\.claude\skills"           -Target "`$MOTHER\000_Agent\skills"
Write-Host "✅ 完成！請重新開啟 Claude Code。"
"@
} else {
    $setupCmd = "（請先確認 Dropbox 已安裝並同步完成，再重新開機執行此提醒）"
}

# ── 顯示提醒視窗 ───────────────────────────────────────────────────
$title = "⚠️  Claude Code 尚未設定跨裝置同步"

$body = @"
偵測到此 Windows 電腦的 Claude Code 尚未連結 AI 分身設定。

Dropbox 母體：$motherStatus

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
請用「系統管理員」身份開啟 PowerShell，
貼上以下指令執行（一次性，之後開機不再提醒）：

$setupCmd

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
點「是」→ 自動開啟系統管理員 PowerShell
點「否」→ 關閉，下次開機再提醒
"@

$result = [System.Windows.Forms.MessageBox]::Show(
    $body,
    $title,
    [System.Windows.Forms.MessageBoxButtons]::YesNo,
    [System.Windows.Forms.MessageBoxIcon]::Warning
)

# ── 點「是」→ 開啟系統管理員 PowerShell ──────────────────────────
if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
    if ($MOTHER) {
        # 把指令寫成暫存腳本讓使用者直接執行
        $tmpScript = "$env:TEMP\claude-setup-symlinks.ps1"
        $setupCmd | Out-File -FilePath $tmpScript -Encoding UTF8
        Start-Process powershell.exe -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$tmpScript`"" -Verb RunAs
    } else {
        [System.Windows.Forms.MessageBox]::Show(
            "請先安裝 Dropbox 並等待 Tu-agent 資料夾同步完成後，再重新開機執行此提醒。",
            "Dropbox 尚未就緒",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Information
        )
    }
}
