$xlsxPath   = "D:\Dropbox\宏祐\20260511羅東聖母醫院防火門維修案\P請購單\20260520防火門維修請購單\20260520防火門維修請購單.xlsx"
$today      = "2026/05/20"
$workType   = "鐵工"
$budget     = "18000"
$budgetItem = "鐵工"
$warranty   = "無"
$vendor     = "鼎堅"

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $wb = $excel.Workbooks.Open($xlsxPath)
    $ws = $wb.Sheets.Item(1)

    $ws.Cells.Item(1,  3).Value2 = $today
    $ws.Cells.Item(3, 12).Value2 = $workType
    $ws.Cells.Item(3, 14).Value2 = $budget
    $ws.Cells.Item(4, 14).Value2 = $budgetItem
    $ws.Cells.Item(5, 14).Value2 = $warranty
    $ws.Cells.Item(8, 14).Value2 = $vendor

    $wb.Save()
    $wb.Close()
    Write-Host "DONE"
} catch {
    Write-Host "ERROR:$($_.Exception.Message) AT $($_.InvocationInfo.ScriptLineNumber)"
} finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}
