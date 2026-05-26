#!/usr/bin/env python3
"""
fill-heping-me-full.py
從 機電標單.xls 標單詳細表 機電，讀取所有 xlrd 可讀到的單價（含 formula cached values）
填入 合併版 標單詳細表，依項次精確比對
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

ME_SRC = r'C:\Users\deco01\Downloads\機電標單.xls'
COMBINED_SRC = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260524-廠商報價三家合併版.xls'
COMBINED_DST = r'C:\Users\deco01\Downloads\20260524-廠商報價三家合併版_機電填入.xls'
SHEET_NAME = '標單詳細表'
ME_SHEET = '標單詳細表 機電'
COL_ITEM = 0
COL_VALUE = 4   # E: 單價
COL_FORMULA = 5 # F: 複價 = D * E

# ─── Step 1: Extract item→unit price from 機電標單 標單詳細表 機電 ───
rb_me = xlrd.open_workbook(ME_SRC, formatting_info=False)
ws_me = rb_me.sheet_by_name(ME_SHEET)

me_prices = {}  # 項次 → 單價
for i in range(ws_me.nrows):
    c0_type = ws_me.cell_type(i, 0)
    c0_val = ws_me.cell_value(i, 0)
    if c0_type != 1:  # must be text
        continue
    item = str(c0_val).strip()
    if not item or not any(item.startswith(ch) for ch in ['參', '肆', '伍']):
        continue
    if '.' not in item:  # skip section headers like 參.一
        continue
    # unit price at col 4
    if ws_me.ncols > COL_VALUE:
        p_type = ws_me.cell_type(i, COL_VALUE)
        p_val = ws_me.cell_value(i, COL_VALUE)
        if p_type == 2 and p_val > 0:
            me_prices[item] = p_val

print(f'機電標單 有單價項次：{len(me_prices)} 筆')

# ─── Step 2: Scan 合併版 標單詳細表 for matching rows ───
rb_c = xlrd.open_workbook(COMBINED_SRC, formatting_info=True)
wb_c = xlcopy(rb_c)
ws_c_r = rb_c.sheet_by_name(SHEET_NAME)
sheet_idx = rb_c.sheet_names().index(SHEET_NAME)
ws_c_w = wb_c.get_sheet(sheet_idx)
rows_dict = ws_c_w._Worksheet__rows

fills = {}  # row0 → price
unmatched_in_combined = []

for i in range(ws_c_r.nrows):
    c0_type = ws_c_r.cell_type(i, 0)
    c0_val = ws_c_r.cell_value(i, 0)
    if c0_type != 1:
        continue
    item = str(c0_val).strip()
    if not item or '.' not in item:
        continue
    if not any(item.startswith(ch) for ch in ['參', '肆', '伍']):
        continue

    # Check if already has a price
    existing_price = 0
    if ws_c_r.ncols > COL_VALUE:
        ep_type = ws_c_r.cell_type(i, COL_VALUE)
        ep_val = ws_c_r.cell_value(i, COL_VALUE)
        if ep_type == 2 and ep_val > 0:
            existing_price = ep_val

    if item in me_prices:
        price = me_prices[item]
        fills[i] = price
    else:
        unmatched_in_combined.append(item)

print(f'合併版 可填入：{len(fills)} 筆')
print(f'合併版 無對應報價：{len(unmatched_in_combined)} 筆')

# ─── Step 3: Fill values ───
errors = []
filled = 0
for row_0, value in sorted(fills.items()):
    row_obj = rows_dict.get(row_0)
    if row_obj is None:
        errors.append(f'Row {row_0+1} 不存在')
        continue

    cells = row_obj._Row__cells

    # Get xf_idx
    xf_idx = None
    for try_col in [COL_VALUE, COL_FORMULA, 3, 2]:
        c = cells.get(try_col)
        if c is not None:
            xf_idx = c.xf_idx
            break
    if xf_idx is None:
        xf_idx = 0

    # Fill 單價
    cells[COL_VALUE] = xc.NumberCell(row_0, COL_VALUE, xf_idx, float(value))

    # Fill 複價 formula
    xf_f = cells.get(COL_FORMULA)
    xf_f = xf_f.xf_idx if xf_f else xf_idx
    row_1 = row_0 + 1
    formula_str = f'D{row_1}*E{row_1}'
    cells[COL_FORMULA] = xc.FormulaCell(row_0, COL_FORMULA, xf_f,
                                         xlwt.Formula(formula_str))

    item_label = ws_c_r.cell_value(row_0, 0)
    print(f'  R{row_0+1} [{item_label}]: 單價={value:,.0f}')
    filled += 1

if errors:
    print('\n錯誤：')
    for e in errors:
        print(f'  {e}')

print(f'\n儲存至：{COMBINED_DST}')
wb_c.save(COMBINED_DST)
print(f'完成，填入 {filled} 筆')

if unmatched_in_combined:
    print(f'\n無對應報價的項次（合計 {len(unmatched_in_combined)} 筆）：')
    for u in unmatched_in_combined[:20]:
        print(f'  {u}')
    if len(unmatched_in_combined) > 20:
        print(f'  ... 還有 {len(unmatched_in_combined)-20} 筆')
