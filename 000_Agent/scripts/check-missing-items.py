#!/usr/bin/env python3
import xlrd

COMBINED = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260524-廠商報價三家合併版.xls'
SHEET_NAME = '標單詳細表'

rb = xlrd.open_workbook(COMBINED, formatting_info=False)
ws = rb.sheet_by_name(SHEET_NAME)

targets = ['貳.一.9', '貳.七.3']

for i in range(ws.nrows):
    c0 = str(ws.cell_value(i, 0)).strip() if ws.cell_type(i, 0) == 1 else ''
    if c0 in targets or any(c0.startswith(t) for t in targets):
        row_data = [ws.cell_value(i, j) for j in range(min(8, ws.ncols))]
        print(f'R{i+1}: {row_data}')
    # Also show surrounding context for these targets
    if c0 in targets:
        print(f'  → 單位={ws.cell_value(i,2)}  數量={ws.cell_value(i,3)}  單價={ws.cell_value(i,4)}  複價={ws.cell_value(i,5)}')
