#!/usr/bin/env python3
import xlrd, win32com.client, os

COMBINED = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260524-廠商報價三家合併版.xls'
SHEET = '標單詳細表'

# prices from 機電標單
fills = {
    '貳.一.9': 100000,
    '貳.七.3': 15000,
}

# find rows in 合併版
rb = xlrd.open_workbook(COMBINED)
ws = rb.sheet_by_name(SHEET)
row_map = {}  # item → 1-based row
for i in range(ws.nrows):
    c0 = str(ws.cell_value(i,0)).strip() if ws.cell_type(i,0)==1 else ''
    if c0 in fills:
        row_map[c0] = i + 1

print('找到行號：', row_map)

# fill via win32com
xl = win32com.client.Dispatch("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False
wb = xl.Workbooks.Open(os.path.abspath(COMBINED))
ws_xl = None
for sh in wb.Sheets:
    if sh.Name == SHEET:
        ws_xl = sh
        break

for item, price in fills.items():
    row = row_map.get(item)
    if not row:
        print(f'找不到 {item}')
        continue
    ws_xl.Cells(row, 5).Value = price          # E: 單價
    ws_xl.Cells(row, 6).Formula = f'=D{row}*E{row}'  # F: 複價
    print(f'  R{row} [{item}]: 單價={price:,}  複價=D{row}*E{row}')

wb.Save()
wb.Close(False)
xl.Quit()
print('完成')
