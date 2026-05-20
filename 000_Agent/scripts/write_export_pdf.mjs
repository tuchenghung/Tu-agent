import fs from 'fs';

const xlsxPath = 'D:\\Dropbox\\宏祐\\20260511羅東聖母醫院防火門維修案\\P請購單\\20260520防火門維修請購單\\20260520防火門維修請購單.xlsx';
const pdfPath  = xlsxPath.replace('.xlsx', '.pdf');
const caseName = '20260511羅東聖母醫院防火門維修案';
const workType = '鐵工';

const ps1 = `\$xlsxPath  = "${xlsxPath}"
\$pdfPath   = "${pdfPath}"
\$caseName  = "${caseName}"
\$workType  = "${workType}"

# ─── 匯出 PDF（第 1 頁）───
\$excel = New-Object -ComObject Excel.Application
\$excel.Visible = \$false
\$excel.DisplayAlerts = \$false

try {
    \$wb = \$excel.Workbooks.Open(\$xlsxPath)
    \$wb.ExportAsFixedFormat(0, \$pdfPath, 0, \$false, \$false, 1, 1)
    \$wb.Close()
    Write-Host "PDF_PATH:\$pdfPath"
} catch {
    Write-Host "PDF_ERROR:\$(\$_.Exception.Message)"
} finally {
    \$excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject(\$excel) | Out-Null
}

# ─── 開啟 Outlook 郵件 ───
try {
    \$outlook = New-Object -ComObject Outlook.Application
    \$mail = \$outlook.CreateItem(0)

    \$mail.Subject = "\${caseName}\${workType}請購單"
    \$mail.Body    = ""

    # 收件者（olTo = 1）
    foreach (\$addr in @("purchase3@richlins.com.tw", "purchase2@richlins.com.tw")) {
        \$r = \$mail.Recipients.Add(\$addr)
        \$r.Type = 1
    }
    # 副本（olCC = 2）
    foreach (\$addr in @("yu@richlins.com.tw", "account01@richlins.com.tw")) {
        \$r = \$mail.Recipients.Add(\$addr)
        \$r.Type = 2
    }
    \$mail.Recipients.ResolveAll() | Out-Null

    \$mail.Attachments.Add(\$pdfPath)

    \$vendorDir = Join-Path (Split-Path \$pdfPath -Parent) "廠商報價"
    if (Test-Path \$vendorDir) {
        \$quoteFiles = Get-ChildItem -Path \$vendorDir -File
        foreach (\$f in \$quoteFiles) {
            \$mail.Attachments.Add(\$f.FullName)
            Write-Host "QUOTE_ATTACHED:\$(\$f.Name)"
        }
    }

    \$mail.Display()
    Write-Host "OUTLOOK_DONE"
} catch {
    Write-Host "OUTLOOK_ERROR:\$(\$_.Exception.Message)"
}
`;

const BOM = Buffer.from([0xEF, 0xBB, 0xBF]);
fs.writeFileSync('D:\\Dropbox\\Tu-agent\\000_Agent\\scripts\\export_pdf_outlook.ps1', Buffer.concat([BOM, Buffer.from(ps1, 'utf8')]));
console.log('PS1 written');
