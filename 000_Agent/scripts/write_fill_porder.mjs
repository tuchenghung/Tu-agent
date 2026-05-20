import fs from 'fs';

const xlsxPath   = 'D:\\Dropbox\\宏祐\\20251104羅東聖母中醫診所規劃案\\P請購單\\20260520測試請購單\\20260520測試請購單.xlsx';
const today      = new Date().toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '/');
const workType   = '泥作';
const budget     = 20000.0;
const budgetItem = '裝修';
const warranty   = '2年';
const vendor     = '銓聯工程';

const ps1 = `\$xlsxPath   = "${xlsxPath}"
\$today      = "${today}"
\$workType   = "${workType}"
\$budget     = "${budget}"
\$budgetItem = "${budgetItem}"
\$warranty   = "${warranty}"
\$vendor     = "${vendor}"

\$excel = New-Object -ComObject Excel.Application
\$excel.Visible = \$false
\$excel.DisplayAlerts = \$false

try {
    \$wb = \$excel.Workbooks.Open(\$xlsxPath)
    \$ws = \$wb.Sheets.Item(1)

    \$ws.Cells.Item(1,  3).Value2 = \$today
    \$ws.Cells.Item(3, 12).Value2 = \$workType
    \$ws.Cells.Item(3, 14).Value2 = \$budget
    \$ws.Cells.Item(4, 14).Value2 = \$budgetItem
    \$ws.Cells.Item(5, 14).Value2 = \$warranty
    \$ws.Cells.Item(8, 14).Value2 = \$vendor

    \$wb.Save()
    \$wb.Close()
    Write-Host "DONE"
} catch {
    Write-Host "ERROR:\$(\$_.Exception.Message) AT \$(\$_.InvocationInfo.ScriptLineNumber)"
} finally {
    \$excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject(\$excel) | Out-Null
}
`;

// Write with UTF-8 BOM so PowerShell reads Chinese correctly
const BOM = Buffer.from([0xEF, 0xBB, 0xBF]);
const content = Buffer.from(ps1, 'utf8');
fs.writeFileSync('D:\\Dropbox\\Tu-agent\\000_Agent\\scripts\\fill_porder.ps1', Buffer.concat([BOM, content]));
console.log('PS1 written with BOM');
