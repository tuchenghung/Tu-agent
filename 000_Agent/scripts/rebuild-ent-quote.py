import sys
sys.stdout.reconfigure(encoding='utf-8')
import win32com.client as win32

TARGET = r'D:\Dropbox\宏祐\規劃中案件\202605-羅東聖母醫院S棟5樓耳鼻喉科整修工程\D預算報價\20260526-羅東聖母醫院S棟5樓耳鼻喉科整修工程報價.xlsx'

import pythoncom
pythoncom.CoInitialize()
xl = win32.Dispatch('Excel.Application')
xl.Visible = False
xl.DisplayAlerts = False
import os
wb = xl.Workbooks.Open(os.path.abspath(TARGET))
ws = wb.Sheets('耳鼻喉科')

# ── Colors: R + G*256 + B*65536 ──
BLUE   = int(189 + 215*256 + 238*65536)  # #BDD7EE 大工種標題
GREEN  = int(198 + 224*256 + 180*65536)  # #C6E0B4 子工種標題
YELL   = int(255 + 242*256 + 204*65536)  # #FFF2CC 小計列
ORANGE = int(255 + 192*256 +   0*65536)  # #FFC000 大計列
WHITE  = int(255 + 255*256 + 255*65536)

def wv(r, c, v):   ws.Cells(r, c).Value = v
def wf(r, c, fml): ws.Cells(r, c).Formula = fml

def bold(r, c1=1, c2=11):
    for c in range(c1, c2+1): ws.Cells(r, c).Font.Bold = True

def bg(r, color, c1=1, c2=11):
    for c in range(c1, c2+1): ws.Cells(r, c).Interior.Color = color

def item(r, code, name, unit, qty=1):
    wv(r, 1, code); wv(r, 2, name); wv(r, 3, unit); wv(r, 4, qty)
    wf(r, 6, f'=IF(OR(D{r}="",E{r}=""),"",D{r}*E{r})')
    wf(r, 10, f'=IF(OR(H{r}="",I{r}=""),"",H{r}*I{r})')
    wf(r, 11, f'=IF(F{r}="","",F{r}-IF(J{r}="",0,J{r}))')

def subsect_hdr(r, code, name):
    wv(r, 1, code); wv(r, 2, name)
    bold(r); bg(r, GREEN)

def subsect_subtot(r, name, rs, re):
    wv(r, 2, name)
    wf(r, 6, f'=IFERROR(SUMIF(F{rs}:F{re},"<>",F{rs}:F{re}),0)')
    wf(r, 6, f'=SUM(F{rs}:F{re})')
    wf(r, 10, f'=SUM(J{rs}:J{re})')
    wf(r, 11, f'=F{r}-J{r}')
    bold(r); bg(r, YELL)

def sect_hdr(r, code, name):
    wv(r, 1, code); wv(r, 2, name)
    bold(r); bg(r, BLUE)

def sect_subtot(r, name, sub_rows):
    wv(r, 2, name)
    parts = '+'.join(f'F{sr}' for sr in sub_rows)
    wf(r, 6, f'={parts}')
    parts_j = '+'.join(f'J{sr}' for sr in sub_rows)
    wf(r, 10, f'={parts_j}')
    wf(r, 11, f'=F{r}-J{r}')
    bold(r); bg(r, ORANGE)

# ── Clear rows 9+ ──
ws.Range('A9:N300').ClearContents()
ws.Range('A9:N300').Interior.ColorIndex = -4142
ws.Range('A9:N300').Font.Bold = False
ws.Range('A9:N300').Font.Color = 0

# ============================================================
# DETAIL SECTION (row 40+)
# ============================================================
r = 40

# ── 甲.壹 假設工程 ──
sect_hdr(r, '甲.壹', '假設工程'); r += 1
rs = r
item(r, '甲.壹.一.1', '施工測量，工地放樣', '式', 1); r += 1
item(r, '甲.壹.一.2', '施工防護措施，施工圍籬', 'M', 0); r += 1
item(r, '甲.壹.一.3', '施工臨時水電設施及費用', '式', 1); r += 1
item(r, '甲.壹.一.4', '工區結構物及設施復原', '式', 1); r += 1
subsect_subtot(r, '假設工程小計', rs, r-1); S1 = r; r += 2

# ── 甲.貳 拆除工程 ──
sect_hdr(r, '甲.貳', '拆除工程'); r += 1
rs = r
item(r, '甲.貳.一.1', '既有天花板/地板拆除', '式', 1); r += 1
item(r, '甲.貳.一.2', '既有隔間牆拆除', '式', 1); r += 1
item(r, '甲.貳.一.3', '既有水電/燈具拆除', '式', 1); r += 1
item(r, '甲.貳.一.4', '既有出回風口拆除', '式', 1); r += 1
item(r, '甲.貳.一.5', '拆除廢棄物清運', '式', 1); r += 1
subsect_subtot(r, '拆除工程小計', rs, r-1); S2 = r; r += 2

# ── 甲.叁 裝修工程 ──
sect_hdr(r, '甲.叁', '裝修工程'); r += 1
s3_subs = []

subsect_hdr(r, '甲.叁.一', '隔間工程'); r += 1
rs = r
item(r, '甲.叁.一.1', '單骨雙面矽酸鈣輕隔間 (60K岩棉)', '㎡', 0); r += 1
item(r, '甲.叁.一.2', '單骨單面矽酸鈣輕隔間', '㎡', 0); r += 1
item(r, '甲.叁.一.3', '玻璃隔間', '㎡', 0); r += 1
subsect_subtot(r, '隔間工程小計', rs, r-1); s3_subs.append(r); r += 1

subsect_hdr(r, '甲.叁.二', '天花板工程'); r += 1
rs = r
item(r, '甲.叁.二.1', '明架矽酸鈣天花板', '㎡', 0); r += 1
item(r, '甲.叁.二.2', '暗架矽酸鈣天花板', '㎡', 0); r += 1
item(r, '甲.叁.二.3', '矽酸鈣板平頂天花板', '㎡', 0); r += 1
subsect_subtot(r, '天花板工程小計', rs, r-1); s3_subs.append(r); r += 1

subsect_hdr(r, '甲.叁.三', '地面工程'); r += 1
rs = r
item(r, '甲.叁.三.1', '地坪自平水泥', '㎡', 0); r += 1
item(r, '甲.叁.三.2', 'PVC無縫地板', '㎡', 0); r += 1
item(r, '甲.叁.三.3', 'PVC踢腳板', 'm', 0); r += 1
item(r, '甲.叁.三.4', '防滑地磚', '㎡', 0); r += 1
subsect_subtot(r, '地面工程小計', rs, r-1); s3_subs.append(r); r += 1

subsect_hdr(r, '甲.叁.四', '牆面工程'); r += 1
rs = r
item(r, '甲.叁.四.1', '牆面油漆粉刷 (一底二度)', '㎡', 0); r += 1
item(r, '甲.叁.四.2', '美耐板牆面', '㎡', 0); r += 1
item(r, '甲.叁.四.3', '磁磚牆面', '㎡', 0); r += 1
subsect_subtot(r, '牆面工程小計', rs, r-1); s3_subs.append(r); r += 1

subsect_hdr(r, '甲.叁.五', '門窗工程'); r += 1
rs = r
item(r, '甲.叩.五.1', '不鏽鋼框單開木門', '樘', 0); r += 1
item(r, '甲.叁.五.2', '不鏽鋼框橫拉木門', '樘', 0); r += 1
item(r, '甲.叁.五.3', '不鏽鋼框自動玻璃門', '樘', 0); r += 1
subsect_subtot(r, '門窗工程小計', rs, r-1); s3_subs.append(r); r += 1

subsect_hdr(r, '甲.叁.六', '櫥櫃工程'); r += 1
rs = r
item(r, '甲.叁.六.1', '系統高櫃', '座', 0); r += 1
item(r, '甲.叁.六.2', '系統吊櫃', '座', 0); r += 1
item(r, '甲.叁.六.3', '系統矮櫃', '座', 0); r += 1
item(r, '甲.叁.六.4', '人造石桌面', '才', 0); r += 1
subsect_subtot(r, '櫥櫃工程小計', rs, r-1); s3_subs.append(r); r += 1

subsect_hdr(r, '甲.叁.七', '雜項工程'); r += 1
rs = r
item(r, '甲.叁.七.1', '矽利康填縫 (全工區)', '式', 1); r += 1
item(r, '甲.叁.七.2', '現場清潔 (含定期清理)', '式', 1); r += 1
item(r, '甲.叁.七.3', '完工清潔/打蠟', '式', 1); r += 1
item(r, '甲.叁.七.4', '防撞護角', '組', 0); r += 1
subsect_subtot(r, '雜項工程小計', rs, r-1); s3_subs.append(r); r += 1

sect_subtot(r, '裝修工程小計', s3_subs); S3 = r; r += 2

# ── 甲.肆 機電工程 ──
sect_hdr(r, '甲.肆', '機電工程'); r += 1
s4_subs = []

subsect_hdr(r, '甲.肆.一', '電盤工程'); r += 1
rs = r
item(r, '甲.肆.一.1', '110V/220V 電源盤配線安裝', '組', 0); r += 1
item(r, '甲.肆.一.2', '電源盤管路配管', '式', 1); r += 1
subsect_subtot(r, '電盤工程小計', rs, r-1); s4_subs.append(r); r += 1

subsect_hdr(r, '甲.肆.二', '電力插座工程'); r += 1
rs = r
item(r, '甲.肆.二.1', '110V 插座配置', '式', 1); r += 1
item(r, '甲.肆.二.2', '220V 插座配置', '式', 1); r += 1
item(r, '甲.肆.二.3', '燈具插座電源迴路', '回', 0); r += 1
item(r, '甲.肆.二.4', '空調電源迴路', '回', 0); r += 1
subsect_subtot(r, '電力插座工程小計', rs, r-1); s4_subs.append(r); r += 1

subsect_hdr(r, '甲.肆.三', '開關燈具工程'); r += 1
rs = r
item(r, '甲.肆.三.1', 'LED 平板燈 (60x60)', '盞', 0); r += 1
item(r, '甲.肆.三.2', 'LED 崁燈/筒燈', '盞', 0); r += 1
item(r, '甲.肆.三.3', '開關配置', '式', 1); r += 1
item(r, '甲.肆.三.4', '緊急出口燈/指示燈', '只', 0); r += 1
subsect_subtot(r, '開關燈具工程小計', rs, r-1); s4_subs.append(r); r += 1

subsect_hdr(r, '甲.肆.四', '給排水工程'); r += 1
rs = r
item(r, '甲.肆.四.1', '洗手台/水槽給水排水配管', '式', 1); r += 1
item(r, '甲.肆.四.2', '感應式龍頭', '組', 0); r += 1
item(r, '甲.肆.四.3', '管線穿牆防火填塞', '式', 1); r += 1
subsect_subtot(r, '給排水工程小計', rs, r-1); s4_subs.append(r); r += 1

subsect_hdr(r, '甲.肆.五', '衛浴設備工程'); r += 1
rs = r
item(r, '甲.肆.五.1', '馬桶', '座', 0); r += 1
item(r, '甲.肆.五.2', '洗手台', '座', 0); r += 1
item(r, '甲.肆.五.3', '衛浴配件 (扶手/皂盒/烘手機)', '式', 1); r += 1
subsect_subtot(r, '衛浴設備工程小計', rs, r-1); s4_subs.append(r); r += 1

sect_subtot(r, '機電工程小計', s4_subs); S4 = r; r += 2

# ── 甲.伍 弱電工程 ──
sect_hdr(r, '甲.伍', '弱電工程'); r += 1
s5_subs = []

subsect_hdr(r, '甲.伍.一', '門禁工程'); r += 1
rs = r
item(r, '甲.伍.一.1', '門禁主機安裝', '式', 1); r += 1
item(r, '甲.伍.一.2', '門禁讀卡器', '組', 0); r += 1
item(r, '甲.伍.一.3', '門禁管線配管配線', '式', 1); r += 1
subsect_subtot(r, '門禁工程小計', rs, r-1); s5_subs.append(r); r += 1

subsect_hdr(r, '甲.伍.二', '監視工程'); r += 1
rs = r
item(r, '甲.伍.二.1', '監視攝影機 (IP Cam)', '台', 0); r += 1
item(r, '甲.伍.二.2', '錄影主機/顯示器', '式', 1); r += 1
item(r, '甲.伍.二.3', '監視管線配管配線', '式', 1); r += 1
subsect_subtot(r, '監視工程小計', rs, r-1); s5_subs.append(r); r += 1

subsect_hdr(r, '甲.伍.三', '資訊電話工程'); r += 1
rs = r
item(r, '甲.伍.三.1', '資訊電信配線安裝', '式', 1); r += 1
item(r, '甲.伍.三.2', 'RJ45 網路插座', '點', 0); r += 1
item(r, '甲.伍.三.3', '電話插座', '點', 0); r += 1
subsect_subtot(r, '資訊電話工程小計', rs, r-1); s5_subs.append(r); r += 1

subsect_hdr(r, '甲.伍.四', '護士呼叫工程'); r += 1
rs = r
item(r, '甲.伍.四.1', '護士呼叫主機', '式', 1); r += 1
item(r, '甲.伍.四.2', '床頭呼叫器', '組', 0); r += 1
item(r, '甲.伍.四.3', '走廊顯示燈', '只', 0); r += 1
subsect_subtot(r, '護士呼叫工程小計', rs, r-1); s5_subs.append(r); r += 1

subsect_hdr(r, '甲.伍.五', '緊急求救工程'); r += 1
rs = r
item(r, '甲.伍.五.1', '緊急求救按鈕 (拉繩式)', '組', 0); r += 1
item(r, '甲.伍.五.2', '緊急求救管線配線', '式', 1); r += 1
subsect_subtot(r, '緊急求救工程小計', rs, r-1); s5_subs.append(r); r += 1

subsect_hdr(r, '甲.伍.六', '同步鐘'); r += 1
rs = r
item(r, '甲.伍.六.1', '同步時鐘主機', '式', 1); r += 1
item(r, '甲.伍.六.2', '子鐘', '台', 0); r += 1
subsect_subtot(r, '同步鐘工程小計', rs, r-1); s5_subs.append(r); r += 1

subsect_hdr(r, '甲.伍.七', '氣體工程'); r += 1
rs = r
item(r, '甲.伍.七.1', '醫療氣體管路配管 (O₂/N₂O/負壓)', '式', 1); r += 1
item(r, '甲.伍.七.2', '氣體插座安裝', '點', 0); r += 1
item(r, '甲.伍.七.3', '氣體管路試壓測試', '式', 1); r += 1
subsect_subtot(r, '氣體工程小計', rs, r-1); s5_subs.append(r); r += 1

sect_subtot(r, '弱電工程小計', s5_subs); S5 = r; r += 2

# ── 甲.陸 空調工程 ──
sect_hdr(r, '甲.陸', '空調工程'); r += 1
s6_subs = []

subsect_hdr(r, '甲.陸.一', '空調設備工程'); r += 1
rs = r
item(r, '甲.陸.一.1', '1對1分離吊隱式空調 (4.0KW)', '台', 0); r += 1
item(r, '甲.陸.一.2', '1對1分離吊隱式空調 (10KW)', '台', 0); r += 1
item(r, '甲.陸.一.3', '全熱交換機', '台', 0); r += 1
subsect_subtot(r, '空調設備工程小計', rs, r-1); s6_subs.append(r); r += 1

subsect_hdr(r, '甲.陸.二', '冰水管工程'); r += 1
rs = r
item(r, '甲.陸.二.1', '冰水主管配管安裝', '式', 1); r += 1
item(r, '甲.陸.二.2', '冰水管保溫', '式', 1); r += 1
subsect_subtot(r, '冰水管工程小計', rs, r-1); s6_subs.append(r); r += 1

subsect_hdr(r, '甲.陸.三', '風管工程'); r += 1
rs = r
item(r, '甲.陸.三.1', '室內機銅管/控制線/EMT 安裝', '台', 0); r += 1
item(r, '甲.陸.三.2', '室外機安裝 (含安裝架)', '台', 0); r += 1
item(r, '甲.陸.三.3', '集風箱/出風口/回風口安裝', '台', 0); r += 1
item(r, '甲.陸.三.4', '排水工程', '台', 0); r += 1
item(r, '甲.陸.三.5', '洗孔工程', '式', 1); r += 1
subsect_subtot(r, '風管工程小計', rs, r-1); s6_subs.append(r); r += 1

subsect_hdr(r, '甲.陸.四', '自動控制工程'); r += 1
rs = r
item(r, '甲.陸.四.1', 'DDC 控制主機', '式', 1); r += 1
item(r, '甲.陸.四.2', '溫濕度感測器', '組', 0); r += 1
item(r, '甲.陸.四.3', '自動控制配線配管', '式', 1); r += 1
subsect_subtot(r, '自動控制工程小計', rs, r-1); s6_subs.append(r); r += 1

sect_subtot(r, '空調工程小計', s6_subs); S6 = r; r += 2

# ── 甲.柒 消防工程 ──
sect_hdr(r, '甲.柒', '消防工程'); r += 1
s7_subs = []

subsect_hdr(r, '甲.柒.一', '火警自動警報系統'); r += 1
rs = r
item(r, '甲.柒.一.1', '偵煙式探測器 (局限型二種)', '只', 0); r += 1
item(r, '甲.柒.一.2', '火警探測器移位安裝工料費', '式', 1); r += 1
item(r, '甲.柒.一.3', '測試調整', '式', 1); r += 1
item(r, '甲.柒.一.4', '總機原廠設定及調整', '式', 1); r += 1
subsect_subtot(r, '火警自動警報系統小計', rs, r-1); s7_subs.append(r); r += 1

subsect_hdr(r, '甲.柒.二', '緊急廣播設備工程'); r += 1
rs = r
item(r, '甲.柒.二.1', '緊急廣播喇叭 3W-L級 (崁頂式)', '只', 0); r += 1
item(r, '甲.柒.二.2', '緊急廣播移位安裝工料費', '式', 1); r += 1
subsect_subtot(r, '緊急廣播設備工程小計', rs, r-1); s7_subs.append(r); r += 1

subsect_hdr(r, '甲.柒.三', '避難設備工程'); r += 1
rs = r
item(r, '甲.柒.三.1', '停電緊急照明燈 LED (崁頂式)', '只', 0); r += 1
item(r, '甲.柒.三.2', '緊急照明燈安裝工料費', '式', 1); r += 1
item(r, '甲.柒.三.3', '逃生指示設備含施工料費', '式', 1); r += 1
subsect_subtot(r, '避難設備工程小計', rs, r-1); s7_subs.append(r); r += 1

subsect_hdr(r, '甲.柒.四', '撒水滅火設備工程'); r += 1
rs = r
item(r, '甲.柒.四.1', '優美型撒水頭 (含美化蓋板)', '只', 0); r += 1
item(r, '甲.柒.四.2', '撒水頭移位安裝工料費', '式', 1); r += 1
item(r, '甲.柒.四.3', '管路試水試壓 (含排水放水)', '式', 1); r += 1
subsect_subtot(r, '撒水滅火設備工程小計', rs, r-1); s7_subs.append(r); r += 1

subsect_hdr(r, '甲.柒.五', '排煙設備工程'); r += 1
rs = r
item(r, '甲.柒.五.1', '新設排煙閘門含設備安裝', '只', 0); r += 1
item(r, '甲.柒.五.2', '排煙風管修改含施工料費', '式', 1); r += 1
item(r, '甲.柒.五.3', '新設排煙格柵及安裝', '只', 0); r += 1
subsect_subtot(r, '排煙設備工程小計', rs, r-1); s7_subs.append(r); r += 1

sect_subtot(r, '消防工程小計', s7_subs); S7 = r; r += 1

print(f'Detail section written. Last row: {r}')
print(f'Subtotal rows: 壹={S1} 貳={S2} 叁={S3} 肆={S4} 伍={S5} 陸={S6} 柒={S7}')

# ============================================================
# SUMMARY SECTION (rows 9-37)
# ============================================================
# Column mapping: A=1,B=2,C=3,D=4,E=5,F=6,G=7,H=8,I=9,J=10,K=11

# Row 9: 甲 直接工程費 (label)
wv(9, 1, '甲'); wv(9, 2, '直接工程費'); bold(9); bg(9, BLUE)

# Rows 10-16: major section summaries → referencing detail subtotals
def summary_row(row, code, name, subtot_row):
    wv(row, 1, code); wv(row, 2, name)
    wv(row, 3, '式'); wv(row, 4, 1)
    wf(row, 5, f'=F{subtot_row}')
    wf(row, 6, f'=E{row}*D{row}')
    wf(row, 10, f'=J{subtot_row}')
    wf(row, 11, f'=F{row}-J{row}')

summary_row(10, '甲.壹', '假設工程', S1)
summary_row(11, '甲.貳', '拆除工程', S2)
summary_row(12, '甲.叁', '裝修工程', S3)
summary_row(13, '甲.肆', '機電工程', S4)
summary_row(14, '甲.伍', '弱電工程', S5)
summary_row(15, '甲.陸', '空調工程', S6)
summary_row(16, '甲.柒', '消防工程', S7)

# Row 17: 直接工程費小計
wv(17, 2, '直接工程費小計')
wf(17, 6, '=SUM(F10:F16)')
wf(17, 10, '=SUM(J10:J16)')
wf(17, 11, '=F17-J17')
bold(17); bg(17, ORANGE)

# Row 18: blank separator

# Row 19: 乙 間接工程費 label
wv(19, 1, '乙'); wv(19, 2, '間接工程費'); bold(19); bg(19, BLUE)

# Row 20: 乙.壹 跑照 (manual)
wv(20, 1, '乙.壹'); wv(20, 2, '兩階段室內裝修審查跑照'); wv(20, 3, '式'); wv(20, 4, 1)
wf(20, 6, '=E20*D20'); wf(20, 10, '=I20*H20'); wf(20, 11, '=F20-J20')

# Row 21: 乙.貳 消防審查 (manual)
wv(21, 1, '乙.貳'); wv(21, 2, '消防圖說審勘及其他作業'); wv(21, 3, '式'); wv(21, 4, 1)
wf(21, 6, '=E21*D21'); wf(21, 10, '=I21*H21'); wf(21, 11, '=F21-J21')

# Row 22: 乙.叁 職安衛 1.5%
wv(22, 1, '乙.叁'); wv(22, 2, '職業安全衛生管理及環境保護費'); wv(22, 3, '式'); wv(22, 4, 1)
wf(22, 5, '=ROUNDUP(F17*1.5%,0)'); wf(22, 6, '=E22*D22')

# Row 23: 乙.肆 品管費 1.5%
wv(23, 1, '乙.肆'); wv(23, 2, '品質管理費'); wv(23, 3, '式'); wv(23, 4, 1)
wf(23, 5, '=ROUNDUP(F17*1.5%,0)'); wf(23, 6, '=E23*D23')

# Row 24: 乙.伍 利潤管理費 7%
wv(24, 1, '乙.伍'); wv(24, 2, '承商工程利潤管理費'); wv(24, 3, '式'); wv(24, 4, 1)
wf(24, 5, '=ROUNDUP(F17*7%,0)'); wf(24, 6, '=E24*D24')

# Row 25: 乙.陸 工程保險 0.5%
wv(25, 1, '乙.陸'); wv(25, 2, '工程保險'); wv(25, 3, '式'); wv(25, 4, 1)
wf(25, 5, '=ROUNDUP(F17*0.5%,0)'); wf(25, 6, '=E25*D25')

# Row 26: 間接工程費小計
wv(26, 2, '間接工程費小計')
wf(26, 6, '=SUM(F20:F25)')
bold(26); bg(26, YELL)

# Row 27: 小計 (直接+間接)
wv(27, 2, '小計'); wf(27, 6, '=F17+F26'); bold(27)

# Row 28: 稅金 5%
wv(28, 2, '稅金（5%）'); wf(28, 6, '=ROUNDUP(F27*5%,0)')

# Row 29: 合計
wv(29, 2, '合計'); wf(29, 6, '=SUM(F27:F28)')
bold(29); bg(29, ORANGE)

# ── Column headers (rows 7-8 kept from original) ──
# Write column 8 header for 成本 section
wv(7, 8, '成本'); wv(7, 9, '單價'); wv(7, 10, '總價'); wv(7, 11, '毛利')

wb.Save()
wb.Close()
xl.Quit()
print('✅ 重建完成！')
print(f'  總行數約: {r} 行')
