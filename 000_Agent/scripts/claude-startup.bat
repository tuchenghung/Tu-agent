@echo off
set "PS_SCRIPT=%USERPROFILE%\Dropbox\Tu-agent\000_Agent\scripts\windows-startup-check.ps1"
if not exist "%PS_SCRIPT%" set "PS_SCRIPT=D:\Dropbox\Tu-agent\000_Agent\scripts\windows-startup-check.ps1"
if not exist "%PS_SCRIPT%" exit /b 0
powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
