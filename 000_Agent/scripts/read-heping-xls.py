#!/usr/bin/env python3
"""讀取和平案標單 — 標單總表 + 詳細表各章小計"""
import xlrd, sys
sys.stdout.reconfigure(encoding='utf-8')

XLS = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\A業主提供資料\20260421-公開招標-20260512下載\臺北市政府工務局_114至115年度和平院區醫療大樓8樓婦兒科病房及產房整修工程(一般急性病房)_01_00\其他\08-1_0408-(空白標單)(V2)114至115年度和平院區醫療大樓8樓婦兒科病房及產房整修工程(一般急性病房)1141228A_bp_rbid.xls'

wb = xlrd.open_workbook(XLS, formatting_info=False)

# ---- 標單總表 ----
ws_sum = wb.sheet_by_name('標單總表')
print("=== 標單總表 (全部列) ===")
for i in range(ws_sum.nrows):
    row = []
    for j in range(ws_sum.ncols):
        v = ws_sum.cell_value(i, j)
        if v not in ('', 0, 0.0):
            row.append(f"[C{j+1}:{str(v)[:40]}]")
    if row:
        print(f"R{i+1}: {' '.join(row)}")

# ---- 標單詳細表 — 找小計/合計行 ----
ws_det = wb.sheet_by_name('標單詳細表')
print(f"\n=== 標單詳細表 ({ws_det.nrows}r x {ws_det.ncols}c) — 含「小計」或「合計」或章節標題的行 ===")
keywords = ['小計', '合計', '壹', '貳', '參', '肆', '伍', '職安衛', '品管', '材料試驗', '稅什費', '室裝', '工程費']
for i in range(ws_det.nrows):
    c0 = str(ws_det.cell_value(i, 0)).strip()
    c1 = str(ws_det.cell_value(i, 1)).strip()
    combined = c0 + c1
    if any(kw in combined for kw in keywords):
        row = []
        for j in range(ws_det.ncols):
            v = ws_det.cell_value(i, j)
            if v not in ('', 0, 0.0):
                row.append(f"[C{j+1}:{str(v)[:50]}]")
        print(f"R{i+1}: {' '.join(row)}")
