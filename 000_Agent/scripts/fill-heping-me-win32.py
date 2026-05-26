#!/usr/bin/env python3
"""
fill-heping-me-win32.py
用 win32com 操控 Excel，只填入 E 欄（單價），保留所有現有公式
"""

import xlrd
import win32com.client
import os, time

ME_SRC = r'C:\Users\deco01\Downloads\機電標單.xls'
COMBINED = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260524-廠商報價三家合併版.xls'
SHEET_NAME = '標單詳細表'
ME_SHEET = '標單詳細表 機電'
COL_ITEM = 0
COL_PRICE = 4   # E: 單價 (0-based)

# ─── Step 1: Extract item→unit price from 機電標單 標單詳細表 機電 ───
rb_me = xlrd.open_workbook(ME_SRC, formatting_info=False)
ws_me = rb_me.sheet_by_name(ME_SHEET)

me_prices = {}  # 項次 → 單價
for i in range(ws_me.nrows):
    if ws_me.cell_type(i, 0) != 1:
        continue
    item = str(ws_me.cell_value(i, 0)).strip()
    if not item or '.' not in item:
        continue
    if not any(item.startswith(ch) for ch in ['參', '肆', '伍']):
        continue
    if ws_me.ncols > COL_PRICE:
        p_type = ws_me.cell_type(i, COL_PRICE)
        p_val = ws_me.cell_value(i, COL_PRICE)
        if p_type == 2 and p_val > 0:
            me_prices[item] = p_val

print(f'機電標單 有單價項次：{len(me_prices)} 筆')

# ─── Step 2: Scan 合併版 標單詳細表 for matching rows ───
rb_c = xlrd.open_workbook(COMBINED, formatting_info=False)
ws_c = rb_c.sheet_by_name(SHEET_NAME)

# Build: item → (row_1based, existing_price)
fills = {}  # 項次 → (excel_row_1based, price)
for i in range(ws_c.nrows):
    if ws_c.cell_type(i, 0) != 1:
        continue
    item = str(ws_c.cell_value(i, 0)).strip()
    if not item or '.' not in item:
        continue
    if not any(item.startswith(ch) for ch in ['參', '肆', '伍']):
        continue
    if item in me_prices:
        fills[item] = (i + 1, me_prices[item])  # 1-based row for Excel

print(f'合併版 可填入：{len(fills)} 筆')

# ─── Step 3: Use win32com to fill cells ───
xl = win32com.client.Dispatch("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

abs_path = os.path.abspath(COMBINED)
wb = xl.Workbooks.Open(abs_path)
ws = None
for sh in wb.Sheets:
    if sh.Name == SHEET_NAME:
        ws = sh
        break

if ws is None:
    print(f'找不到工作表：{SHEET_NAME}')
    wb.Close(False)
    xl.Quit()
    exit(1)

col_e = 5  # Excel column E = 5 (1-based)
col_f = 6  # Excel column F = 6 (1-based)

filled = 0
for item, (row_1, price) in sorted(fills.items(), key=lambda x: x[1][0]):
    # Set unit price E
    ws.Cells(row_1, col_e).Value = price
    # Set formula F = D*E (複價)
    ws.Cells(row_1, col_f).Formula = f'=D{row_1}*E{row_1}'
    print(f'  R{row_1} [{item}]: 單價={price:,.0f}  複價=D{row_1}*E{row_1}')
    filled += 1

print(f'\n填入 {filled} 筆，儲存中...')
wb.Save()
wb.Close(False)
xl.Quit()
print('完成')
