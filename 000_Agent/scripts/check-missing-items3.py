#!/usr/bin/env python3
import xlrd, os

d = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價'
files = os.listdir(d)

# Find 20260523 file
f23 = [f for f in files if '20260523' in f][0]
SRC23 = os.path.join(d, f23)

COMBINED = os.path.join(d, [f for f in files if '20260524' in f and 'bak' not in f and '合併' not in f and '三家' in f][0])
SHEET = '標單詳細表'

targets = ['貳.一.9', '貳.七.3']

def dump_ctx(ws, row_0, label):
    print(f'\n=== {label} ===')
    for i in range(max(0, row_0-1), min(ws.nrows, row_0+5)):
        row = [ws.cell_value(i,j) for j in range(min(8, ws.ncols))]
        marker = ' <<<' if i == row_0 else ''
        print(f'  R{i+1}{marker}: {row}')

# 合併版
rb1 = xlrd.open_workbook(COMBINED)
ws1 = rb1.sheet_by_name(SHEET)
print('合併版:', COMBINED)
for i in range(ws1.nrows):
    c0 = str(ws1.cell_value(i,0)).strip() if ws1.cell_type(i,0)==1 else ''
    if c0 in targets:
        dump_ctx(ws1, i, f'合併版 {c0}')

# 20260523
rb2 = xlrd.open_workbook(SRC23)
print('\n20260523 sheets:', rb2.sheet_names())
if SHEET in rb2.sheet_names():
    ws2 = rb2.sheet_by_name(SHEET)
    print('20260523:', SRC23)
    for i in range(ws2.nrows):
        c0 = str(ws2.cell_value(i,0)).strip() if ws2.cell_type(i,0)==1 else ''
        if c0 in targets:
            dump_ctx(ws2, i, f'20260523 {c0}')
