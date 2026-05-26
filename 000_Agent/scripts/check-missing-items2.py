#!/usr/bin/env python3
import xlrd

COMBINED = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260524-廠商報價三家合併版.xls'
SRC23 = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260523-廠商報價彙整填入版.xls'
SHEET = '標單詳細表'

def dump_context(ws, row_0, label):
    print(f'\n=== {label} R{row_0+1} 上下文 ===')
    for i in range(max(0, row_0-2), min(ws.nrows, row_0+6)):
        row = [ws.cell_value(i,j) for j in range(min(10, ws.ncols))]
        print(f'  R{i+1}: {row}')

rb1 = xlrd.open_workbook(COMBINED)
ws1 = rb1.sheet_by_name(SHEET)

rb2 = xlrd.open_workbook(SRC23)
ws2 = rb2.sheet_by_name(SHEET)

targets = ['貳.一.9', '貳.七.3']

print('=== 合併版 ===')
for i in range(ws1.nrows):
    c0 = str(ws1.cell_value(i,0)).strip() if ws1.cell_type(i,0)==1 else ''
    if c0 in targets:
        dump_context(ws1, i, f'合併版 {c0}')

print('\n=== 20260523 彙整版 ===')
for i in range(ws2.nrows):
    c0 = str(ws2.cell_value(i,0)).strip() if ws2.cell_type(i,0)==1 else ''
    if c0 in targets:
        dump_context(ws2, i, f'彙整版 {c0}')
