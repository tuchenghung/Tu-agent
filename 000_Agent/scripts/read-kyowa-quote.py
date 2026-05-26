#!/usr/bin/env python3
"""讀取礁溪杏和醫院門診中心整修工程 V7 報價單 — 取得各大項小計"""
import xlrd, sys
sys.stdout.reconfigure(encoding='utf-8')

# 讀最新版 V7
XLS = r'D:\Dropbox\宏祐\規劃中案件\礁溪杏和醫院3F門診中心及7F復健中心整修工程\D預算報價\20260306-礁溪杏和醫院3F門診中心及7F復健中心整修工程V7.xlsx'

wb = xlrd.open_workbook(XLS, formatting_info=False)
print("Sheets:", wb.sheet_names())

for sname in wb.sheet_names()[:5]:
    ws = wb.sheet_by_name(sname)
    print(f"\n{'='*60}")
    print(f"【{sname}】 {ws.nrows}r × {ws.ncols}c")

    # 找有數值的行，特別關注小計/合計/章節標題
    keywords = ['小計','合計','甲','乙','假設','拆除','裝修','機電','消防','空調','弱電','氣體',
                '工程費','利潤','間接','稅','總計','總價','直接','品管','職安','室裝','毛利']
    for i in range(min(ws.nrows, 300)):
        row_vals = [ws.cell_value(i, j) for j in range(ws.ncols)]
        row_str = ' '.join(str(v)[:40] for v in row_vals if v not in ('', 0, 0.0))
        if any(kw in row_str for kw in keywords) and row_str.strip():
            print(f"  R{i+1}: {row_str[:120]}")
