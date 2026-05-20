$xlsxPath  = "D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\P請購單\20260520測試請購單\20260520測試請購單.xlsx"
$pdfPath   = "D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\P請購單\20260520測試請購單\20260520測試請購單.pdf"
$quotePath = "D:\Dropbox\宏祐\20251104羅東聖母中醫診所規劃案\P請購單\20260520測試請購單\廠商報價\地坪水泥粉光-銓聯.xls"
$caseName  = "20251104羅東聖母中醫診所規劃案"
$workType  = "泥作"

# ─── 匯出 PDF ───
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

    $mail.To      = "陳岱妤; 黃婉姍"
    $mail.CC      = "游勝基; 鄭至男; 楊芳瑜"
    $mail.Subject = "${caseName}${workType}請購單"
    $mail.Body    = ""

    $mail.Attachments.Add($pdfPath)
    if ($quotePath -ne "" -and (Test-Path $quotePath)) {
        $mail.Attachments.Add($quotePath)
        Write-Host "QUOTE_ATTACHED"
    }

    $mail.Display()
    Write-Host "OUTLOOK_DONE"
} catch {
    Write-Host "OUTLOOK_ERROR:$($_.Exception.Message)"
}
