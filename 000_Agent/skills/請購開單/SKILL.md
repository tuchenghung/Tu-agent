# 請購開單 Skill

觸發方式：`/請購開單`

輸入 `/請購開單`，自動找到 Dropbox 專案資料夾、複製最新請購單為範本並改名、填好基本欄位讓你謄寫品項；完成後告訴 AI，自動輸出 PDF 並開啟 Outlook 郵件視窗。

---

## 平台設定

```
平台偵測：uname -s 2>/dev/null || echo Windows
Windows → $NODE = C:\Users\deco01\nodejs\node.exe
Mac    → $NODE = ~/.nvm/versions/node/v24.14.1/bin/node
```

本 Skill 目前僅支援 **Windows**（Excel/Outlook COM 需要 Windows 桌面應用）。

---

## STEP 1：找到專案資料夾

用 **AskUserQuestion** 詢問專案關鍵字。

執行 Node.js 腳本掃描（寫入暫存檔執行，避免中文編碼問題）：

```js
// 寫入 D:\Dropbox\Tu-agent\000_Agent\scripts\find_project.mjs 再執行
import fs from 'fs';
const ROOTS = ['D:\\Dropbox\\宏祐', 'D:\\Dropbox\\yushi'];
const keyword = process.argv[2];
const results = [];
for (const root of ROOTS) {
  if (!fs.existsSync(root)) continue;
  for (const d of fs.readdirSync(root, { withFileTypes: true })) {
    if (d.isDirectory() && d.name.includes(keyword)) {
      results.push({ root, name: d.name, full: root + '\\' + d.name });
    }
  }
}
console.log(JSON.stringify(results));
```

執行：`"C:\Users\deco01\nodejs\node.exe" find_project.mjs "{關鍵字}"`

- 找到 1 個 → 直接使用，記為 `$PROJECT_FOLDER`
- 找到多個 → 用 AskUserQuestion 讓使用者選
- 找不到 → 提示使用者確認路徑

---

## STEP 2：複製最新請購單並建立新資料夾

### 2a. 找最新子資料夾

```js
// 寫入暫存腳本執行
import fs from 'fs';
import path from 'path';

const ROOTS = ['D:\\Dropbox\\宏祐', 'D:\\Dropbox\\yushi'];
const P_DIR = path.join(PROJECT_FOLDER, 'P請購單');
if (!fs.existsSync(P_DIR)) { console.error('找不到 P請購單 資料夾'); process.exit(1); }

// 只取名稱開頭為 8 位數字（YYYYMMDD）的子資料夾，過濾「標單」等非日期資料夾
function getDateDirs(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter(d => d.isDirectory() && /^\d{8}/.test(d.name))
    .map(d => ({ name: d.name, full: path.join(dir, d.name) }))
    .sort((a, b) => b.name.localeCompare(a.name));
}

let dirs = getDateDirs(P_DIR);

// 若目前專案 P請購單 為空，掃描所有專案找最新範本
if (dirs.length === 0) {
  console.error('P請購單 無日期子資料夾，掃描其他專案...');
  const allDirs = [];
  for (const root of ROOTS) {
    if (!fs.existsSync(root)) continue;
    for (const proj of fs.readdirSync(root, { withFileTypes: true })) {
      if (!proj.isDirectory()) continue;
      const pDir = path.join(root, proj.name, 'P請購單');
      for (const d of getDateDirs(pDir)) allDirs.push(d);
    }
  }
  allDirs.sort((a, b) => b.name.localeCompare(a.name));
  if (allDirs.length === 0) { console.error('所有專案均無請購單範本，請手動提供'); process.exit(1); }
  dirs = allDirs;
  console.error('找到跨專案範本：' + dirs[0].full);
}

console.log(JSON.stringify(dirs[0])); // 最新的
```

### 2b. 詢問新名稱

用 **AskUserQuestion** 詢問：
> 「新請購單資料夾名稱？（預設：`YYYYMMDD{施工項目}請購單`）」

記為 `$NEW_FOLDER_NAME`，`$NEW_FOLDER_PATH = P請購單\{NEW_FOLDER_NAME}`

### 2c. 複製、清理、改名 xlsx

```js
import fs from 'fs';
import path from 'path';

const SRC = '最新資料夾完整路徑';
const DST = '新資料夾完整路徑';
const NEW_NAME = '新資料夾名稱';

// 複製整個資料夾
function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const item of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, item.name);
    const d = path.join(dst, item.name);
    if (item.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}
copyDir(SRC, DST);

// 清除舊 PDF 和已填好的 xlsx（保留空白 xlsx）
// 判斷「空白 xlsx」：檔案大小最小的 xlsx = 空白範本
const xlsxFiles = fs.readdirSync(DST).filter(f => f.endsWith('.xlsx'));
xlsxFiles.sort((a, b) => fs.statSync(path.join(DST, a)).size - fs.statSync(path.join(DST, b)).size);
const blankXlsx = xlsxFiles[0]; // 最小的視為空白範本

for (const f of fs.readdirSync(DST)) {
  const fp = path.join(DST, f);
  if (f.endsWith('.pdf')) { fs.unlinkSync(fp); continue; }
  if (f.endsWith('.xlsx') && f !== blankXlsx) { fs.unlinkSync(fp); continue; }
}

// 空白 xlsx 改名為新資料夾名稱
if (blankXlsx) {
  fs.renameSync(path.join(DST, blankXlsx), path.join(DST, NEW_NAME + '.xlsx'));
  console.log('xlsx 改名為:', NEW_NAME + '.xlsx');
}

// 確認廠商報價子資料夾
const VENDOR_DIR = path.join(DST, '廠商報價');
if (fs.existsSync(VENDOR_DIR)) {
  for (const f of fs.readdirSync(VENDOR_DIR)) fs.unlinkSync(path.join(VENDOR_DIR, f));
} else {
  fs.mkdirSync(VENDOR_DIR);
}
console.log('廠商報價資料夾已清空/建立');
console.log('XLSX_PATH:' + path.join(DST, NEW_NAME + '.xlsx'));
```

記下 `$XLSX_PATH`（新 xlsx 完整路徑）。

### 2d. 詢問是否放入廠商報價單

用 **AskUserQuestion**：
> 「是否要將廠商報價單放入廠商報價資料夾？」
> 選項：是（請提供檔案路徑）/ 否

若「是」→ 請使用者輸入報價單路徑，用 Node.js `fs.copyFileSync` 複製到 `廠商報價\`，記為 `$QUOTE_FILE_PATH`。

---

## STEP 3：收集開單資料 → 填入 Excel

### 3a. 收集資料

用 **單次 AskUserQuestion 一次問全部 4 個欄位**（AskUserQuestion 支援最多 4 題同時問）：

1. **施工項目／工種**
   - 選項：機電、空調、木作、水電（涵蓋常用工種）
   - 使用者若直接輸入「其他」→ 取其他欄中的文字

2. **預算金額**
   - 選項：100000、200000、500000（常見金額）
   - 使用者若直接輸入「其他」→ 取其他欄中的數字

3. **廠商保固**
   - 選項：1年、2年、3年（常見年限）

4. **建議廠商名稱**
   - 選項：從廠商報價資料夾的檔案推算廠商名稱（若有）；否則提供空選項讓使用者填

**關鍵原則：每個選項只列真實常用值，不放「自訂」選項。使用者若要輸入非選項的值，直接用 AskUserQuestion 右下角的「其他」文字欄填入，不再彈出第二個問題。**

預算項目（說明文字）單獨一次問，或合併在廠商那題的說明裡。

### 3b. PowerShell Excel COM 填入

```powershell
# 寫入暫存 ps1 執行（避免中文傳參問題）
$xlsxPath = "完整xlsx路徑"
$today    = Get-Date -Format "yyyy/MM/dd"
$workType = "施工項目"
$budget   = "預算金額"
$budgetItem = "預算項目"
$warranty = "廠商保固"
$vendor   = "建議廠商"

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $wb = $excel.Workbooks.Open($xlsxPath)
    $ws = $wb.Sheets.Item(1)

    $ws.Cells.Item(1,  3).Value2 = $today      # C1  提出日期
    $ws.Cells.Item(3, 12).Value2 = $workType   # L3  工程種類
    $ws.Cells.Item(3, 14).Value2 = $budget     # N3  預算金額
    $ws.Cells.Item(4, 14).Value2 = $budgetItem # N4  預算項目
    $ws.Cells.Item(5, 14).Value2 = $warranty   # N5  廠商保固
    $ws.Cells.Item(8, 14).Value2 = $vendor     # N8  建議廠商

    $wb.Save()
    $wb.Close($false)
    Write-Host "✅ Excel 填入完成"
} catch {
    Write-Host "❌ 錯誤：$($_.Exception.Message)"
} finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}
```

填完後通知使用者：
> 「✅ Excel 已填好基本資料，請開啟以下檔案謄寫品項內容，完成後告訴我：
> `{$XLSX_PATH}`」

---

## STEP 4：使用者完成 → 匯出 PDF → 開啟 Outlook 郵件

### 4a. 等待使用者回覆「完成」

### 4b. 匯出 PDF

```powershell
# 寫入暫存 ps1 執行
$xlsxPath = "完整xlsx路徑"
$pdfPath  = $xlsxPath -replace '\.xlsx$', '.pdf'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $wb = $excel.Workbooks.Open($xlsxPath)
    $wb.ExportAsFixedFormat(0, $pdfPath, 0, $false, $false, 1, 1)  # 只輸出第 1 頁
    $wb.Close($false)
    Write-Host "PDF_PATH:$pdfPath"
} catch {
    Write-Host "❌ 錯誤：$($_.Exception.Message)"
} finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}
```

回報：「✅ PDF 已輸出：`{$PDF_PATH}`」

### 4c. 開啟 Outlook 新郵件

```powershell
# 寫入暫存 ps1 執行
$pdfPath      = "PDF完整路徑"
$quotePath    = "廠商報價單路徑（若無則留空）"
$caseName     = "案件名稱"
$workType     = "施工項目"

$outlook = New-Object -ComObject Outlook.Application
$mail = $outlook.CreateItem(0)  # 0 = olMailItem

$mail.Subject = "${caseName}${workType}請購單"
$mail.Body    = ""

# 收件者（olTo = 1）
foreach ($addr in @("purchase3@richlins.com.tw", "purchase2@richlins.com.tw")) {
    $r = $mail.Recipients.Add($addr); $r.Type = 1
}
# 副本（olCC = 2）
foreach ($addr in @("yu@richlins.com.tw", "account01@richlins.com.tw")) {
    $r = $mail.Recipients.Add($addr); $r.Type = 2
}
$mail.Recipients.ResolveAll() | Out-Null

$mail.Attachments.Add($pdfPath)

# 廠商報價：只在廠商報價資料夾有檔案時才附上
$vendorDir = Split-Path $pdfPath -Parent | Join-Path -ChildPath "廠商報價"
if (Test-Path $vendorDir) {
    $quoteFiles = Get-ChildItem -Path $vendorDir -File
    foreach ($f in $quoteFiles) {
        $mail.Attachments.Add($f.FullName)
    }
}

$mail.Display()  # 停在視窗，不自動送出
Write-Host "✅ Outlook 郵件已開啟，請確認後手動按傳送"
```

---

## 錯誤處理

| 狀況 | 處理方式 |
|------|---------|
| 找不到 `P請購單` 資料夾 | 提示使用者確認路徑後重試 |
| xlsx 只有一個（無法判斷空白/填好） | 直接使用，改名後繼續 |
| Excel COM 被佔用（其他程式開著） | 提示「請關閉所有 Excel 視窗後告訴我」，等待後重試 |
| Outlook 未開啟 | COM 會自動啟動 Outlook，稍等片刻 |
| 廠商報價單路徑無效 | 提示重新輸入，或選擇跳過 |

---

## 重要常數

| 項目 | 值 |
|------|---|
| Windows Node | `C:\Users\deco01\nodejs\node.exe` |
| Dropbox 宏祐 | `D:\Dropbox\宏祐` |
| Dropbox yushi | `D:\Dropbox\yushi` |
| Outlook 收件者 | 陳岱妤(行政總務) purchase3@richlins.com.tw; 黃婉姍(採購) purchase2@richlins.com.tw |
| Outlook 副本 | 游勝基 yu@richlins.com.tw; 楊芳瑜(會計1) account01@richlins.com.tw |

---

## 腳本暫存路徑慣例

所有暫存腳本一律寫入 `D:\Dropbox\Tu-agent\000_Agent\scripts\` 再執行，避免 shell 中文編碼問題。
