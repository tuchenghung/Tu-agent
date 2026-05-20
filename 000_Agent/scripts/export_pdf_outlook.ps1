$xlsxPath  = "D:\Dropbox\宏祐\20260511羅東聖母醫院防火門維修案\P請購單\20260520防火門維修請購單\20260520防火門維修請購單.xlsx"
$pdfPath   = "D:\Dropbox\宏祐\20260511羅東聖母醫院防火門維修案\P請購單\20260520防火門維修請購單\20260520防火門維修請購單.pdf"
$caseName  = "20260511羅東聖母醫院防火門維修案"
$workType  = "鐵工"

# ─── 匯出 PDF（第 1 頁）───
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $wb = $excel.Workbooks.Open($xlsxPath)
    $wb.ExportAsFixedFormat(0, $pdfPath, 0, $false, $false, 1, 1)
    $wb.Close()
    Write-Host "PDF_PATH:$pdfPath"
} catch {
    Write-Host "PDF_ERROR:$($_.Exception.Message)"
} finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}

# ─── 開啟 Outlook 郵件 ───
try {
    $outlook = New-Object -ComObject Outlook.Application
    $mail = $outlook.CreateItem(0)

    $mail.Subject = "${caseName}${workType}請購單"
    $mail.Body    = ""

    # 收件者（olTo = 1）
    foreach ($name in @("凃政宏")) {
        $r = $mail.Recipients.Add($name)
        $r.Type = 1
    }
    # 副本（olCC = 2）
    foreach ($name in @("游勝基", "鄭至男", "楊芳瑜")) {
        $r = $mail.Recipients.Add($name)
        $r.Type = 2
    }
    $mail.Recipients.ResolveAll() | Out-Null

    $mail.Attachments.Add($pdfPath)

    $vendorDir = Join-Path (Split-Path $pdfPath -Parent) "廠商報價"
    if (Test-Path $vendorDir) {
        $quoteFiles = Get-ChildItem -Path $vendorDir -File
        foreach ($f in $quoteFiles) {
            $mail.Attachments.Add($f.FullName)
            Write-Host "QUOTE_ATTACHED:$($f.Name)"
        }
    }

    $mail.Display()
    Write-Host "OUTLOOK_DONE"
} catch {
    Write-Host "OUTLOOK_ERROR:$($_.Exception.Message)"
}
