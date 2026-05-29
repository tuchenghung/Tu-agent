#!/usr/bin/env python3
"""
標案廠商報價匯入正式報價單.py
廠商報價 XLS → 三家合併版標單 完整流程

流程：
  Step 1  備份合併版（覆蓋 .bak）
  Step 2  複製廠商報價到 F供應商報價與資料/廠商報價/，依命名規則改名
  Step 3  從來源 XLS 讀取所有含「.」的項次 → 單價（xlrd，含 formula cached values）
  Step 4  掃描合併版目標工作表，比對項次找到對應行號
  Step 5  用 win32com 填入 E欄（單價）+ F欄（=D*E 公式），保留所有現有公式
  Step 6  儲存並輸出摘要
"""

import os, shutil
import xlrd
import win32com.client

# ═══════════════════════════════════════════════════════════════
# CONFIG — 每次新廠商報價時修改這裡
# ═══════════════════════════════════════════════════════════════

# 【來源】廠商報價 XLS
SRC_FILE  = r'C:\Users\deco01\Downloads\機電標單.xls'
SRC_SHEET = '標單詳細表 機電'   # 來源 XLS 的工作表名稱

# 【廠商資訊】用於存檔命名：YYYYMMDD-廠商簡稱-工種.xls
VENDOR_DATE  = '20260524'    # 報價單上的日期
VENDOR_NAME  = '嵩泰機電'    # 廠商簡稱
VENDOR_TRADE = '機電工程'    # 工種名稱

# 【目標】三家合併版 XLS
COMBINED_FILE  = r'D:\Dropbox\宏祐\規劃中案件\202605-市醫和平院區醫療大樓8樓婦兒科病房整修\D預算報價\20260524-廠商報價三家合併版.xls'
COMBINED_SHEET = '標單詳細表'  # 要填入的工作表名稱

# 【欄位】0-based（預設：E=4 單價，F=5 複價）
COL_PRICE   = 4
COL_FORMULA = 5

# ═══════════════════════════════════════════════════════════════
# 以下不需修改
# ═══════════════════════════════════════════════════════════════

def find_vendor_folder(combined_path):
    """從合併版路徑（D預算報價/）往上一層找案件根目錄，組出廠商報價資料夾路徑"""
    case_root = os.path.dirname(os.path.dirname(combined_path))
    return os.path.join(case_root, '廠商報價')

def step1_backup():
    bak = COMBINED_FILE + '.bak'
    print(f'[Step 1] 備份合併版')
    print(f'  {COMBINED_FILE}')
    print(f'  → {bak}')
    shutil.copy2(COMBINED_FILE, bak)
    print('  OK\n')

def step2_archive():
    ext  = os.path.splitext(SRC_FILE)[1]
    name = f'{VENDOR_DATE}-{VENDOR_NAME}-{VENDOR_TRADE}{ext}'
    dst  = os.path.join(find_vendor_folder(COMBINED_FILE), name)
    print(f'[Step 2] 存檔廠商報價')
    print(f'  來源：{SRC_FILE}')
    print(f'  存至：{dst}')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(SRC_FILE, dst)
    print('  OK\n')

def step3_extract():
    print(f'[Step 3] 讀取來源報價（{SRC_SHEET}）')
    wb = xlrd.open_workbook(SRC_FILE, formatting_info=False)
    ws = wb.sheet_by_name(SRC_SHEET)
    prices = {}
    zero_count = 0
    for i in range(ws.nrows):
        if ws.cell_type(i, 0) != 1:
            continue
        item = str(ws.cell_value(i, 0)).strip()
        if '.' not in item:          # 只取明細行，跳過章節標題
            continue
        if ws.ncols <= COL_PRICE:
            continue
        pt = ws.cell_type(i, COL_PRICE)
        pv = ws.cell_value(i, COL_PRICE)
        if pt == 2 and pv > 0:
            prices[item] = pv
        elif pt == 2 and pv == 0:
            zero_count += 1
    print(f'  有單價：{len(prices)} 筆  單價為 0 跳過：{zero_count} 筆\n')
    return prices

def step4_map(prices):
    print(f'[Step 4] 掃描合併版（{COMBINED_SHEET}），比對項次')
    wb = xlrd.open_workbook(COMBINED_FILE, formatting_info=False)
    ws = wb.sheet_by_name(COMBINED_SHEET)
    row_map  = {}   # item → 1-based row
    no_match = []
    for i in range(ws.nrows):
        if ws.cell_type(i, 0) != 1:
            continue
        item = str(ws.cell_value(i, 0)).strip()
        if item in prices:
            row_map[item] = i + 1
    for item in prices:
        if item not in row_map:
            no_match.append(item)
    print(f'  可填入：{len(row_map)} 筆')
    if no_match:
        print(f'  來源有但合併版找不到（{len(no_match)} 筆）：')
        for m in no_match[:10]:
            print(f'    {m}')
        if len(no_match) > 10:
            print(f'    ... 還有 {len(no_match)-10} 筆')
    print()
    return row_map

def step5_fill(prices, row_map):
    print(f'[Step 5] win32com 填入單價與 =D*E 公式')
    xl = win32com.client.Dispatch('Excel.Application')
    xl.Visible = False
    xl.DisplayAlerts = False
    wb = xl.Workbooks.Open(os.path.abspath(COMBINED_FILE))

    ws_xl = next((sh for sh in wb.Sheets if sh.Name == COMBINED_SHEET), None)
    if ws_xl is None:
        print(f'  錯誤：找不到工作表 {COMBINED_SHEET}')
        wb.Close(False); xl.Quit(); return

    col_e = COL_PRICE   + 1   # 轉成 1-based
    col_f = COL_FORMULA + 1

    for item, row in sorted(row_map.items(), key=lambda x: x[1]):
        price = prices[item]
        ws_xl.Cells(row, col_e).Value   = price
        ws_xl.Cells(row, col_f).Formula = f'=D{row}*E{row}'
        print(f'  R{row} [{item}]: 單價={price:,.0f}')

    wb.Save()
    wb.Close(False)
    xl.Quit()
    print(f'\n  填入 {len(row_map)} 筆，儲存完成')

# ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('=' * 60)
    print(f'  來源：{SRC_FILE}')
    print(f'        工作表：{SRC_SHEET}')
    print(f'  廠商：{VENDOR_DATE}-{VENDOR_NAME}-{VENDOR_TRADE}')
    print(f'  目標：{COMBINED_FILE}')
    print(f'        工作表：{COMBINED_SHEET}')
    print('=' * 60 + '\n')

    step1_backup()
    step2_archive()
    prices  = step3_extract()
    row_map = step4_map(prices)
    step5_fill(prices, row_map)

    print('\n完成')
