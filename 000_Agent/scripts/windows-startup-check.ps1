Add-Type -AssemblyName System.Windows.Forms

function Is-Symlink($path) {
    $item = Get-Item $path -Force -ErrorAction SilentlyContinue
    return ($item -ne $null) -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
}

$claudeDir    = "$env:USERPROFILE\.claude"
$skillsLink   = Join-Path $claudeDir "skills"
$settingsLink = Join-Path $claudeDir "settings.json"
$commandsLink = Join-Path $claudeDir "commands"

$skillsOk   = Is-Symlink $skillsLink
$settingsOk = Is-Symlink $settingsLink
$commandsOk = Is-Symlink $commandsLink

if ($skillsOk -and $commandsOk) { exit 0 }

$possiblePaths = @(
    "D:\Dropbox\Tu-agent",
    "C:\Dropbox\Tu-agent",
    "E:\Dropbox\Tu-agent",
    "$env:USERPROFILE\Dropbox\Tu-agent"
)

$MOTHER = $null
foreach ($p in $possiblePaths) {
    if (Test-Path $p) { $MOTHER = $p; break }
}

if ($MOTHER) {
    $motherLine = "Found: $MOTHER"
    $cmd1 = "New-Item -ItemType SymbolicLink -Force -Path `"$env:USERPROFILE\.claude\skills`" -Target `"$MOTHER\000_Agent\skills`""
    $cmd2 = "cmd /c mklink /J `"$env:USERPROFILE\.claude\commands`" `"$MOTHER\.claude\commands`""
    $cmd3 = "Copy-Item `"$MOTHER\.claude\settings.json`" `"$env:USERPROFILE\.claude\settings.json`" -Force"
    $body = "Claude Code symlinks not configured on this PC.`n`nDropbox: $motherLine`n`nRun these in Admin PowerShell:`n`n$cmd1`n`n$cmd2`n`n$cmd3`n`nClick YES to open Admin PowerShell."
} else {
    $body = "Claude Code symlinks not configured.`nDropbox folder not found. Please install Dropbox and wait for sync.`n`nClick OK to close."
}

$result = [System.Windows.Forms.MessageBox]::Show(
    $body,
    "Claude Code - Setup Required",
    [System.Windows.Forms.MessageBoxButtons]::YesNo,
    [System.Windows.Forms.MessageBoxIcon]::Warning
)

if ($result -eq [System.Windows.Forms.DialogResult]::Yes -and $MOTHER) {
    $tmp = "$env:TEMP\claude-symlinks.ps1"
    @"
New-Item -ItemType SymbolicLink -Force -Path "$env:USERPROFILE\.claude\skills" -Target "$MOTHER\000_Agent\skills"
cmd /c mklink /J "$env:USERPROFILE\.claude\commands" "$MOTHER\.claude\commands"
Copy-Item "$MOTHER\.claude\settings.json" "$env:USERPROFILE\.claude\settings.json" -Force
Write-Host "Done. Please restart Claude Code." -ForegroundColor Green
Read-Host "Press Enter to close"
"@ | Out-File -FilePath $tmp -Encoding UTF8
    Start-Process powershell.exe -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$tmp`"" -Verb RunAs
}
