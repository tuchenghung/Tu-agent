"""
Auto-refresh Google OAuth tokens for calendar-win and gmail-win MCPs.
Run via Windows Task Scheduler every 50 minutes.
"""
import json
import urllib.request
import urllib.parse
import time
import datetime
import sys
import os

TOKENS_FILE = r"C:\Users\deco01\.config\google-calendar-mcp\tokens.json"
OAUTH_FILE  = r"C:\Users\deco01\.google-mcp\gcp-oauth.keys.json"
LOG_FILE    = r"C:\Users\deco01\.config\google-calendar-mcp\refresh.log"


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def refresh_tokens():
    with open(TOKENS_FILE, encoding="utf-8") as f:
        tokens = json.load(f)
    with open(OAUTH_FILE, encoding="utf-8") as f:
        oauth = json.load(f)

    creds = oauth.get("installed") or oauth.get("web")
    if not creds:
        log("ERROR: 找不到 OAuth 憑證 (installed/web)")
        return False

    refreshed = False
    for account, token_data in tokens.items():
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            log(f"SKIP {account}: 無 refresh_token")
            continue

        # 還有 10 分鐘以上才到期就跳過
        expiry = token_data.get("expiry_date", 0)
        remaining = (expiry / 1000) - time.time()
        if remaining > 600:
            log(f"OK   {account}: token 還有 {int(remaining/60)} 分鐘有效，跳過")
            continue

        data = urllib.parse.urlencode({
            "client_id":     creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": refresh_token,
            "grant_type":    "refresh_token",
        }).encode()

        try:
            req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
        except Exception as e:
            log(f"ERROR {account}: {e}")
            continue

        new_expiry_ms = int((time.time() + result["expires_in"]) * 1000)
        tokens[account]["access_token"] = result["access_token"]
        tokens[account]["expiry_date"]  = new_expiry_ms

        new_exp = datetime.datetime.fromtimestamp(new_expiry_ms / 1000)
        log(f"OK   {account}: token 刷新成功，新到期 {new_exp.strftime('%H:%M:%S')}")
        refreshed = True

    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)

    return refreshed


if __name__ == "__main__":
    log("=== 開始刷新 Google tokens ===")
    refresh_tokens()
    log("=== 完成 ===")
