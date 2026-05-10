@echo off
:: windows-startup-reminder.bat
:: 放進 Windows 開機啟動資料夾：
::   shell:startup  → 僅目前使用者
::   shell:common startup → 所有使用者（需系統管理員）
::
:: 操作方式：
::   1. Win + R → 輸入 shell:startup → Enter
::   2. 把這個 .bat 檔的「捷徑」複製貼上到開啟的資料夾
::   3. 完成後每次開機自動執行，設定好 symlink 後靜默退出

:: ── 找 PowerShell 腳本位置 ──────────────────────────────────────
:: 這個 .bat 放在 Dropbox 裡，腳本路徑相對於它自身推算
set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%windows-startup-check.ps1"

:: 如果找不到（Dropbox 未同步），靜默退出
if not exist "%PS_SCRIPT%" exit /b 0

:: ── 載入 Windows Forms（顯示對話框需要）────────────────────────
:: 以隱藏視窗方式執行 PowerShell，避免一閃而過的黑框
powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -Command ^
    "Add-Type -AssemblyName System.Windows.Forms; & '%PS_SCRIPT%'"
