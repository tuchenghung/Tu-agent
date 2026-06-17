#!/usr/bin/env python3
"""
旭東環保(1343) 股價警報
每個交易日收盤後自動檢查，跌破 18 元發 macOS 通知 + 寄 Gmail
"""
import urllib.request, json, re, subprocess, datetime, os

STOCK_ID = "1343"
STOCK_NAME = "旭東環保"
SUPPORT_PRICE = 18.0
ALERT_EMAIL = "gemini7361@gmail.com"
LOG_FILE = os.path.expanduser(
    "~/Library/CloudStorage/Dropbox/Tu-agent/000_Agent/scripts/stock_alert_log.txt"
)

def fetch_price():
    url = f"https://histock.tw/stock/{STOCK_ID}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8")
    # histock 格式: id="Price1_lbTPrice"><span>19.30</span>
    m = re.search(r'id="Price1_lbTPrice"><span>([\d.]+)</span>', html)
    if m:
        return float(m.group(1))
    # fallback: og:description 有 "股價 19.30"
    m = re.search(r'股價\s+([\d.]+)', html)
    if m:
        return float(m.group(1))
    return None

def notify_mac(title, message):
    script = f'display notification "{message}" with title "{title}" sound name "Basso"'
    subprocess.run(["osascript", "-e", script])

def send_gmail(price):
    """用 AppleScript 開 Mail.app 草稿（不需要額外 token）"""
    subject = f"⚠️ {STOCK_NAME}({STOCK_ID}) 跌破支撐 {SUPPORT_PRICE} 元警報"
    body = (
        f"{STOCK_NAME}({STOCK_ID}) 今日股價 {price} 元，"
        f"已跌破技術支撐 {SUPPORT_PRICE} 元。\\n\\n"
        f"依照原定停損計畫，請評估是否出場。\\n"
        f"均價 31.13 元，持股 1,400 股。"
    )
    script = f"""
    tell application "Mail"
        set newMsg to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:true}}
        tell newMsg
            make new to recipient with properties {{address:"{ALERT_EMAIL}"}}
        end tell
        send newMsg
    end tell
    """
    subprocess.run(["osascript", "-e", script])

def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now} | {msg}\n")

if __name__ == "__main__":
    today = datetime.date.today()
    if today.weekday() >= 5:  # 跳過週末
        log("週末，跳過")
        exit(0)

    price = fetch_price()
    if price is None:
        log("❌ 無法取得股價，請手動確認")
        notify_mac("股價抓取失敗", f"{STOCK_NAME} 無法取得今日股價")
    elif price < SUPPORT_PRICE:
        msg = f"🚨 {STOCK_NAME} 股價 {price} 元，跌破支撐 {SUPPORT_PRICE} 元！"
        log(msg)
        notify_mac(f"⚠️ {STOCK_NAME} 跌破 {SUPPORT_PRICE}", f"現價 {price} 元，請評估停損")
        send_gmail(price)
    else:
        log(f"✅ {STOCK_NAME} 現價 {price} 元，支撐 {SUPPORT_PRICE} 未破")
