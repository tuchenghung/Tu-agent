#!/usr/bin/env python3
"""
fill-heping-me.py
填入 和平案 機電報價 至 三家合併版 標單詳細表
- 來源：機電標單.xls（標單單價分析表 合計欄）
- 目標：20260524-廠商報價三家合併版.xls（標單詳細表）
- 加成：+10%
"""

import xlrd
import xlwt
import xlwt.Cell as xc
from xlutils.copy import copy as xlcopy

# Patch xlwt Python 3 bug
import xlwt.BIFFRecords as br
_orig = br.NumberFormatRecord.__init__
def _safe(self, idx, fmtstr):
    if fmtstr is None: fmtstr = ''
    _orig(self, idx, fmtstr)
br.NumberFormatRecord.__init__ = _safe

SRC = r"D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260524-廠商報價三家合併版.xls"
DST = r"C:\Users\deco01\Downloads\20260524-廠商報價三家合併版_機電填入.xls"
SHEET_NAME = "標單詳細表"
COL_VALUE = 4   # E: 單價
COL_FORMULA = 5 # F: 複價 = D * E

# row0: price (原廠商價 × 1.1)
# 參.一.1~8: 低壓開關箱設備，肆.五.1~2: 空調管路
FILLS = {
    298: 199952,  # 參.一.1
    301: 75840,   # 參.一.2
    304: 344239,  # 參.一.3
    307: 563527,  # 參.一.4
    310: 120818,  # 參.一.5
    313: 81802,   # 參.一.6
    317: 99004,   # 參.一.7
    321: 51354,   # 參.一.8
    956: 72134,   # 肆.五.1
    959: 66885,   # 肆.五.2
}

print(f"讀取：{SRC}")
rb = xlrd.open_workbook(SRC, formatting_info=True)
wb = xlcopy(rb)

sheet_idx = rb.sheet_names().index(SHEET_NAME)
ws_r = rb.sheet_by_index(sheet_idx)
ws_w = wb.get_sheet(sheet_idx)
rows_dict = ws_w._Worksheet__rows

errors = []
for row_0, value in sorted(FILLS.items()):
    row_obj = rows_dict.get(row_0)
    if row_obj is None:
        errors.append(f"Row {row_0+1} 不存在於 xlwt copy")
        continue

    cells = row_obj._Row__cells

    # Get xf_idx: prefer col4, fallback to col5 (複價 has 0), fallback to col3 (數量)
    xf_idx = None
    for try_col in [COL_VALUE, COL_FORMULA, 3]:
        c = cells.get(try_col)
        if c is not None:
            xf_idx = c.xf_idx
            break

    if xf_idx is None:
        # Last resort: look at xlrd row for xf_idx
        try:
            cell = ws_r.cell(row_0, COL_VALUE)
            xf_idx = ws_r.cell_xf_index(row_0, COL_VALUE)
        except Exception:
            xf_idx = 0

    # Fill 單價 (col4)
    cells[COL_VALUE] = xc.NumberCell(row_0, COL_VALUE, xf_idx, float(value))

    # Fill 複價 formula: D{row}*E{row}
    xf_f = cells.get(COL_FORMULA)
    xf_f = xf_f.xf_idx if xf_f else xf_idx
    row_1 = row_0 + 1
    formula_str = f"D{row_1}*E{row_1}"
    cells[COL_FORMULA] = xc.FormulaCell(row_0, COL_FORMULA, xf_f,
                                         xlwt.Formula(formula_str))

    # Read desc from xlrd for display
    try:
        desc = ws_r.cell_value(row_0, 0)
    except Exception:
        desc = f"row{row_0+1}"
    print(f"  R{row_0+1} [{desc}]: 單價={value:,}  公式={formula_str}")

if errors:
    print("\n錯誤：")
    for e in errors:
        print(f"  {e}")

print(f"\n儲存至：{DST}")
wb.save(DST)
print("完成 ✅")
