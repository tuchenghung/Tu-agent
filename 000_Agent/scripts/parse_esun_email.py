#!/usr/bin/env python3
"""
玉山證券交易明細信件解析腳本
用法：python3 parse_esun_email.py [--days N]
輸出：JSON array，每筆成交一個物件
"""
import subprocess, sys, json, re
from datetime import datetime, timedelta

def get_esun_emails(days=1):
    """用 AppleScript 從 Mac Mail 讀取玉山成交通知"""
    script = f"""
tell application "Mail"
    set targetAccount to first account whose name is "Exchange"
    set targetMailbox to first mailbox of targetAccount whose name is "收件匣"
    set allMsgs to messages of targetMailbox
    set cutoff to (current date) - ({days} * days)
    set mailList to {{}}
    set checkCount to count of allMsgs
    if checkCount > 100 then set checkCount to 100
    repeat with i from 1 to checkCount
        set m to item i of allMsgs
        if (sender of m) contains "esun@esunsec.com.tw" and (subject of m) contains "交易明細通知" then
            if (date sent of m) >= cutoff then
                set end of mailList to (content of m)
            end if
        end if
    end repeat
    return mailList
end tell
"""
    try:
        out = subprocess.check_output(['osascript', '-e', script], text=True, timeout=120)
        # AppleScript list returns comma-separated; split carefully
        # Each email content is separated by ", " but content itself has commas
        # Return as raw string and split by known delimiter
        return out.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e}", file=sys.stderr)
        return ""

def parse_email_content(content: str) -> list[dict]:
    """解析信件內文，回傳成交紀錄 list"""
    transactions = []

    # 正規化空白字元（  行分隔符、\xa0 不換行空格 → 標準空格/換行）
    content = content.replace(' ', '\n').replace(' ', '\n').replace('\xa0', ' ')

    # 找成交日期：YYYY/MM/DD 的交易明細
    date_match = re.search(r'(\d{4}/\d{2}/\d{2})\s+的交易明細', content)
    if not date_match:
        return []
    trade_date = date_match.group(1)  # e.g. "2026/05/22"

    # 找資料區：header 結尾標記為"淨收付\n金額\n"，到"總計"結束
    data_match = re.search(r'淨收付\s*\n\s*金額\s*\n(.*?)(?:\s*總計)', content, re.DOTALL)
    if not data_match:
        return []

    data_block = data_match.group(1).strip()
    lines = [l.strip() for l in data_block.split('\n') if l.strip()]

    # 每 14 行一筆成交（標借費/利息/稅款在 HTML 合併為一欄）
    FIELDS_PER_ROW = 14
    field_names = ['交易類別','股票名稱','成交股數','成交單價','成交價金',
                   '手續費','交易稅','自備款','擔保品','融資金',
                   '保證金','券手續費','標借利息稅款','淨收付金額']

    i = 0
    while i + FIELDS_PER_ROW <= len(lines):
        row = lines[i:i+FIELDS_PER_ROW]
        d = dict(zip(field_names, row))
        d['成交日期'] = trade_date

        # 解析股票代號和名稱 e.g. "6940格斯科技"
        name_raw = d['股票名稱']
        code_match = re.match(r'^(\d{4,5})(.*)', name_raw)
        if code_match:
            d['股票代號'] = code_match.group(1)
            d['股票名稱'] = code_match.group(2).strip().rstrip('*')

        # 清理數字（去千分位）
        for key in ['成交股數','成交單價','成交價金','手續費','淨收付金額']:
            d[key] = d[key].replace(',', '').strip()

        transactions.append(d)
        i += FIELDS_PER_ROW

    return transactions

def main():
    days = 1
    if '--days' in sys.argv:
        idx = sys.argv.index('--days')
        days = int(sys.argv[idx+1])

    raw = get_esun_emails(days)
    if not raw:
        print(json.dumps([]))
        return

    # AppleScript 多封信件用 ", " 分隔（粗略處理）
    # 若只有一封直接 parse
    all_txns = []

    # 嘗試直接 parse（單封）
    txns = parse_email_content(raw)
    if txns:
        all_txns.extend(txns)

    print(json.dumps(all_txns, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
