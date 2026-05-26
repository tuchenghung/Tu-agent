#!/usr/bin/env python3
"""Check cell types in 機電標單 標單詳細表 機電 using xlrd"""
import xlrd

src = r'C:\Users\deco01\Downloads\機電標單.xls'
rb = xlrd.open_workbook(src, formatting_info=False)

print("Sheets:", rb.sheet_names())

# Check 標單詳細表 機電
ws = rb.sheet_by_name('標單詳細表 機電')
print(f"\n標單詳細表 機電: {ws.nrows} rows x {ws.ncols} cols")

# cell types: 0=empty, 1=text, 2=number, 3=date, 5=error, 6=blank
type_names = {0:'empty',1:'text',2:'number',3:'date',5:'error',6:'blank'}

# Scan for rows with 參.一.9 onwards - show all cols 0-6
print("\n=== 參.一.9 以後 所有行 (col0-5) ===")
in_me = False
count = 0
for i in range(ws.nrows):
    c0 = str(ws.cell_value(i, 0)).strip() if ws.ncols > 0 else ''
    if '參.一.9' in c0 or '參.一.10' in c0:
        in_me = True
    if not in_me:
        continue
    if count > 100:
        break

    row_vals = []
    for j in range(min(8, ws.ncols)):
        ct = ws.cell_type(i, j)
        cv = ws.cell_value(i, j)
        row_vals.append(f"[{type_names.get(ct,'?')}:{cv}]")
    print(f"R{i+1}: {' '.join(row_vals)}")
    count += 1

# Also check: any non-zero price in whole sheet
print("\n=== 所有單價(col4) > 0 的行 ===")
found = 0
for i in range(ws.nrows):
    if ws.ncols > 4:
        ct = ws.cell_type(i, 4)
        cv = ws.cell_value(i, 4)
        if ct == 2 and cv != 0:
            c0 = ws.cell_value(i, 0)
            c1 = ws.cell_value(i, 1)
            print(f"R{i+1}: [{c0}] {str(c1)[:30]} 單價={cv}")
            found += 1
if not found:
    print("無任何 > 0 的單價")
