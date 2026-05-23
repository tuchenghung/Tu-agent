#!/usr/bin/env python3
"""
fill-xls-values.py
把數值填入現有 XLS 並完整保留原始格式（顏色/字型/邊框/千分位）

用法：
  1. 修改下方 CONFIG 區塊（SRC / DST / SHEET_NAME / FILLS）
  2. 確認已建立 xlrd 1.2 虛擬環境（見底部說明）
  3. /tmp/xlrd1_env/bin/python3 fill-xls-values.py

技術說明：400_Knowledge/AI工作流/2026-05-23_XLS格式保留填入數值.md
"""

# ─── CONFIG ───────────────────────────────────────────────────────────────────

SRC = "來源_空白模板.xls"       # 原始有格式的空白 XLS
DST = "輸出_已填入版.xls"       # 輸出檔案路徑
SHEET_NAME = "工作表1"          # 要修改的工作表名稱

# 填入清單：{0-indexed row: (E欄值, 是否公式欄位在F欄)}
# COL_VALUE: 填入數值的欄位索引（0-based）
# COL_FORMULA: 填入 =COL_D_LETTER*COL_VALUE_LETTER 公式的欄位索引（0-based），None 表示不填公式
COL_VALUE = 4    # E 欄（單價）
COL_FORMULA = 5  # F 欄（複價 = D*E），None 代表不填公式

FILLS = {
    # 0-based row : 數值
    # 44: 1000,
    # 49: 1900,
}

# ─── 以下不需修改 ──────────────────────────────────────────────────────────────

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


def fill_xls(src, dst, sheet_name, fills, col_value, col_formula=None):
    print(f"讀取：{src}")
    rb = xlrd.open_workbook(src, formatting_info=True)
    wb = xlcopy(rb)

    sheet_idx = rb.sheet_names().index(sheet_name)
    ws_w = wb.get_sheet(sheet_idx)
    rows_dict = ws_w._Worksheet__rows

    errors = []
    for row_0, value in fills.items():
        row_obj = rows_dict.get(row_0)
        if row_obj is None:
            errors.append(f"Row {row_0+1} 不存在")
            continue

        cells = row_obj._Row__cells
        target_cell = cells.get(col_value)
        if target_cell is None:
            errors.append(f"Row {row_0+1} col {col_value+1} 無 cell")
            continue

        xf_idx = target_cell.xf_idx

        # 填入數值
        cells[col_value] = xc.NumberCell(row_0, col_value, xf_idx, float(value))

        # 填入公式（如果有指定 col_formula）
        if col_formula is not None:
            old = cells.get(col_formula)
            xf_f = old.xf_idx if old else xf_idx
            # 公式：col D（0-based 3）* col_value 的英文字母
            col_d_letter = chr(ord('A') + col_value - 1)  # E欄前一欄 = D
            col_v_letter = chr(ord('A') + col_value)
            formula_str = f'{col_d_letter}{row_0+1}*{col_v_letter}{row_0+1}'
            cells[col_formula] = xc.FormulaCell(row_0, col_formula, xf_f,
                                                 xlwt.Formula(formula_str))
            print(f"  row {row_0+1}: 值={value}  公式={formula_str}")
        else:
            print(f"  row {row_0+1}: 值={value}")

    if errors:
        print("\n⚠️  錯誤：")
        for e in errors: print(f"  {e}")

    print(f"\n儲存至：{dst}")
    wb.save(dst)
    print("完成 ✅")


if __name__ == '__main__':
    fill_xls(SRC, DST, SHEET_NAME, FILLS, COL_VALUE, COL_FORMULA)


# ─── 環境建立（第一次執行前）──────────────────────────────────────────────────
# python3 -m venv /tmp/xlrd1_env
# /tmp/xlrd1_env/bin/pip install "xlrd==1.2.0" xlwt xlutils
# 執行：/tmp/xlrd1_env/bin/python3 fill-xls-values.py
