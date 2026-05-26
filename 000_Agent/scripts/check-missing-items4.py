#!/usr/bin/env python3
import xlrd, os

d = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價'
files = os.listdir(d)
print('files:', files)

COMBINED = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260524-廠商報價三家合併版.xls'
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
print('合併版 sheets:', rb1.sheet_names())
for i in range(ws1.nrows):
    c0 = str(ws1.cell_value(i,0)).strip() if ws1.cell_type(i,0)==1 else ''
    if c0 in targets:
        dump_ctx(ws1, i, f'合併版 {c0}')

# 20260523 file (use bytes path)
f23_path = os.path.join(d, files[1])  # second file is 20260523
print(f'\n20260523 path: {repr(f23_path)}')
rb2 = xlrd.open_workbook(f23_path)
print('20260523 sheets:', rb2.sheet_names())
if SHEET in [str(s) for s in rb2.sheet_names()]:
    ws2 = rb2.sheet_by_name(SHEET)
    for i in range(ws2.nrows):
        c0 = str(ws2.cell_value(i,0)).strip() if ws2.cell_type(i,0)==1 else ''
        if c0 in targets:
            dump_ctx(ws2, i, f'20260523 {c0}')
else:
    print('Sheet 標單詳細表 not found in 20260523')
    for sn in rb2.sheet_names():
        ws = rb2.sheet_by_name(sn)
        for i in range(ws.nrows):
            c0 = str(ws.cell_value(i,0)).strip() if ws.cell_type(i,0)==1 else ''
            if c0 in targets:
                dump_ctx(ws, i, f'20260523[{sn}] {c0}')
