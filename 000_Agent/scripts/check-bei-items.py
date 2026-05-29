#!/usr/bin/env python3
import xlrd

ws = xlrd.open_workbook(r'C:\Users\deco01\Downloads\機電標單.xls').sheet_by_name('標單詳細表 機電')

targets = ['貳.一.9', '貳.七.3']
for i in range(ws.nrows):
    c0 = str(ws.cell_value(i,0)).strip() if ws.cell_type(i,0)==1 else ''
    if c0 in targets:
        row = [ws.cell_value(i,j) for j in range(min(8, ws.ncols))]
        print(f'R{i+1} [{c0}]: {row}')
        print(f'  單位={ws.cell_value(i,2)}  數量={ws.cell_value(i,3)}  單價={ws.cell_value(i,4)}  複價={ws.cell_value(i,5)}')
