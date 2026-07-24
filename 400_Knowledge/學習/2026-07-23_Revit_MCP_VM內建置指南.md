---
建立日期: 2026-07-23
來源: 研究 Demolinator/revit-mcp-plugin (https://github.com/Demolinator/revit-mcp-plugin) README + main.py 原始碼分析
類型: 學習筆記 / 工具建置
---

# Revit MCP 建置指南（方案①：VM 內獨立 Claude Code）

## 背景

- 使用者的 Revit 跑在 **Mac 上的 Parallels 虛擬機（Windows）**，透過 `\\Mac\Dropbox\...` 路徑存取 Mac 本機 Dropbox（從 `.rvt` 檔 BasicFileInfo stream 讀出的最後存檔路徑確認）
- 目標：讓 Claude 能用自然語言操作 Revit 建模
- 選定方案：**revit-mcp-plugin**（Demolinator），走 pyRevit（Python）橋接，不用編譯 C#
- 關鍵限制：`main.py` 的 MCP server 寫死 `host="127.0.0.1"`（見原始碼 `revit-bim/mcp-server/main.py` / 實際路徑 `revit-bim/mcp-server/main.py`），無法從 VM 外部連入 → **必須讓 Claude Code 跟 Revit 待在同一台 VM 裡**，而不是從這台 Mac 的 Claude Code 跨機連線

## 前置需求

| 項目 | 說明 |
|---|---|
| VM 內 Revit 版本 | 需在 VM 內 Revit「說明」畫面確認實際版本（2024/2025/2026/2027），已知本機練習檔 Build=20240307_1300(x64), Format=2025，**推測為 Revit 2024，但務必在 VM 內以 Revit 內建「關於」畫面確認，不要用推測值** |
| VM 需要能上網 | 下載 pyRevit、uv、repo |
| VM 內需安裝 Claude Code | 若 VM 尚未裝，需先在 VM 內的 Windows 裝 Claude Code CLI |

## 安裝步驟

### Step 0：VM 內安裝 pyRevit
1. 關閉 Revit
2. 前往 https://github.com/pyrevitlabs/pyRevit/releases ，下載 Assets 內一般 `.exe` 安裝檔（**不要**下載 `pyRevit_CLI_...` 版本，那個不會掛進 Revit）
3. 執行安裝，全部預設下一步到完成
4. 開啟 Revit，功能區應出現 **pyRevit** 分頁
5. 若沒出現：開命令提示字元，執行 `pyrevit attach master default <你的Revit版本>`（例：`pyrevit attach master default 2024`），再重開 Revit

### Step 1：下載 revit-mcp-plugin
- 有 Git：`git clone https://github.com/Demolinator/revit-mcp-plugin.git`
- 沒 Git：GitHub 頁面 → 綠色 Code 按鈕 → Download ZIP → 解壓縮

### Step 2：一鍵設定
雙擊資料夾內的 `setup-revit-mcp.bat`，會自動：
- 安裝 `uv`（自帶 Python，不動系統 Python）
- 裝好 MCP server 依賴
- 啟用 pyRevit Routes（port 48884）
- 寫入 Claude Desktop 設定（若 VM 內用 Claude Desktop）

> 驗證 Routes：Revit 開著時，瀏覽器開 `http://localhost:48884/`，只要有任何回應（就算是錯誤頁）就代表成功

### Step 3：接上 Claude Code（VM 內）

**方式A（推薦，最簡單）**：在 VM 的 Claude Code CLI 內執行
```
/plugin marketplace add Demolinator/revit-mcp-plugin
/plugin install revit-bim@revit-mcp
```
會自動帶入 48 個 Revit 工具 + BIM skill + 5 個 slash commands。

**方式B（手動）**：在專案資料夾建立 `.mcp.json`
```json
{
  "mcpServers": {
    "revit": {
      "command": "C:\\path\\to\\revit-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\revit-mcp-server\\main.py"]
    }
  }
}
```
路徑改成實際 clone 下來的位置。

### Step 4：確認可用
1. Revit 開著一個專案（pyRevit Routes 隨 Revit 啟動自動載入）
2. 重啟 VM 內的 Claude Code
3. 應該能看到 `revit` 相關工具/指令可用

## 每次使用流程
1. VM 裡開 Revit + 開專案
2. VM 裡開 Claude Code，直接用自然語言下建模指令（如 `/revit-bim:create-element`、`/revit-bim:query-model`）

## 已知限制
- MCP server 只認 VM 內部連線，這個 Mac 上的 Claude Code session **無法**直接操作 Revit，需求要建模時切到 VM 裡的 Claude Code
- Revit 2027 需搭配支援 .NET 10 的 pyRevit build
- 若之後想要「這台 Mac 直接控制 VM 內 Revit」，需改 `main.py` 的 `host="127.0.0.1"` → `"0.0.0.0"` 並處理 VM 防火牆，或改用官方 ngrok 遠端連線腳本 `setup-web-mobile.bat`（流量會繞經公網）

## 參考來源
- https://github.com/Demolinator/revit-mcp-plugin
- https://github.com/Demolinator/revit-mcp-server
