# -*- coding: utf-8 -*-
import openpyxl

FILE = r'D:\Dropbox\yushi\規劃中案件\20260608-南崁廠房高架地板工程\D預算報價\20260611南崁廠房高架地板工程.xlsx'

wb = openpyxl.load_workbook(FILE)
ws = wb.active

note = (
    '1、本報價有效期限30天；逾期重新報價。\n'
    '2、報價內容未含膨脹螺絲及斜支撐。\n'
    '3、若需要∮2㎜裸銅線單向間1200mm距接地處理則另行報價。\n'
    '4、本工程未含地面防塵漆。\n'
    '2、付款方式：訂金總工程款30%；空調完成30%；油漆工程完成總工程款30%；驗收完成總工程款10%'
)

ws['B28'] = note
wb.save(FILE)
print('saved')
