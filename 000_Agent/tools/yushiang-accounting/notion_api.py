"""Notion API 資料存取層"""
import os
import streamlit as st
from notion_client import Client
from datetime import datetime
import pandas as pd

# ── DB IDs ────────────────────────────────────────────────────────────────────
DB_PROJECTS        = "3355cac1-0351-4ef4-8eb1-8b8f0bb619c3"  # Projects（專案與指標）
DB_FINANCE         = "2f97aebd-089f-80f7-9607-df6dc41ab3bd"  # 案件財務管理
DB_CONTRACTS       = "3337aebd-089f-80d1-aa42-f85b80c119b9"  # 發包管理
DB_SUPPLIERS       = "8ed44912-2c9e-4c9a-bbd1-d7bbc1933b3b"  # 供應商資料庫
DB_REVENUE         = os.getenv("NOTION_DB_REVENUE") or "3767aebd-089f-81d8-a4a0-df836a89e70d"
DB_PAYMENTS        = os.getenv("NOTION_DB_PAYMENTS") or "3767aebd-089f-819c-866e-e5bc4ef8e041"

COMPANY_FILTER = "YUSHI"  # Projects 公司別篩選


def _secret(key: str, default: str = "") -> str:
    """讀取環境變數，fallback 到 Streamlit secrets"""
    val = os.getenv(key, "")
    if not val:
        try:
            val = st.secrets.get(key, default)
        except Exception:
            val = default
    return val


@st.cache_resource
def get_notion_client():
    token = _secret("NOTION_TOKEN")
    if not token:
        st.error("❌ 找不到 NOTION_TOKEN，請設定環境變數或 Streamlit secrets")
        st.stop()
    return Client(auth=token)


def _query_all(notion: Client, db_id: str, filter_obj=None) -> list:
    """分頁讀取資料庫所有記錄"""
    results, cursor = [], None
    while True:
        kwargs = {"database_id": db_id, "page_size": 100}
        if filter_obj:
            kwargs["filter"] = filter_obj
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = notion.databases.query(**kwargs)
        results.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]
    return results


# ── 取值輔助 ──────────────────────────────────────────────────────────────────
def _num(props, key) -> float:
    p = props.get(key, {})
    if p.get("type") == "number":
        return p.get("number") or 0.0
    if p.get("type") == "formula":
        return p["formula"].get("number") or 0.0
    if p.get("type") == "rollup":
        return p["rollup"].get("number") or 0.0
    return 0.0


def _text(props, key) -> str:
    p = props.get(key, {})
    t = p.get("type", "")
    if t == "title":
        return "".join(r["plain_text"] for r in p.get("title", []))
    if t == "rich_text":
        return "".join(r["plain_text"] for r in p.get("rich_text", []))
    if t == "formula":
        return p["formula"].get("string", "")
    if t == "rollup":
        arr = p["rollup"].get("array", [])
        return ", ".join(
            "".join(r["plain_text"] for r in item.get("title", []))
            for item in arr if item.get("type") == "title"
        )
    return ""


def _select(props, key) -> str:
    p = props.get(key, {})
    s = p.get("select") or p.get("status")
    return s["name"] if s else ""


def _date(props, key) -> str:
    p = props.get(key, {})
    d = p.get("date")
    return d["start"] if d else ""


def _relation_ids(props, key) -> list:
    p = props.get(key, {})
    return [r["id"] for r in p.get("relation", [])]


# ── 公開查詢函數 ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_finance_projects() -> pd.DataFrame:
    """讀取案件財務管理（YUSHI 公司別）"""
    notion = get_notion_client()

    # 先取 Projects 中公司別為 YUSHI 的案件財務管理 ID 清單
    yushi_pages = _query_all(notion, DB_PROJECTS, {
        "property": "公司別",
        "select": {"equals": COMPANY_FILTER}
    })
    # 取出關聯的財務管理 page IDs
    fin_ids = set()
    for p in yushi_pages:
        for fid in _relation_ids(p["properties"], "案件財務管理"):
            fin_ids.add(fid)

    if not fin_ids:
        return pd.DataFrame()

    # 讀財務管理資料庫全部，再過濾
    all_fin = _query_all(notion, DB_FINANCE)
    rows = []
    for p in all_fin:
        if p["id"] not in fin_ids:
            continue
        props = p["properties"]
        rows.append({
            "id":        p["id"],
            "url":       p["url"],
            "專案名稱":  _text(props, "專案名稱"),
            "承攬金額":  _num(props, "承攬金額"),
            "發包成本":  _num(props, "內部發包成本加總"),
            "其他成本":  _num(props, "其他成本"),
            "已收金額":  _num(props, "已收金額"),
            "毛利":      _num(props, "毛利"),
            "毛利率":    _text(props, "毛利率"),
            "撥款進度":  _num(props, "撥款進度"),
            "狀態":      _select(props, "狀態"),
            "開始日期":  _date(props, "開始日期"),
            "結束日期":  _date(props, "結束日期"),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def load_contracts(finance_ids: tuple) -> pd.DataFrame:
    """讀取發包管理（過濾指定案件）"""
    if not finance_ids:
        return pd.DataFrame()
    notion = get_notion_client()
    all_c = _query_all(notion, DB_CONTRACTS)
    rows = []
    for p in all_c:
        props = p["properties"]
        linked = _relation_ids(props, "專案")
        if not any(fid in finance_ids for fid in linked):
            continue
        rows.append({
            "id":        p["id"],
            "url":       p["url"],
            "廠商名稱":  _text(props, "廠商名稱"),
            "案件名稱":  _text(props, "案件名稱"),
            "工種":      _select(props, "工種"),
            "成本":      _num(props, "成本"),
            "狀態":      _select(props, "狀態"),
            "已撥款":    props.get("是否已撥款", {}).get("checkbox", False),
            "撥款日期":  _date(props, "撥款日期"),
            "備註":      _text(props, "備註"),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def load_revenue(finance_ids: tuple) -> pd.DataFrame:
    """讀取業主收款記錄"""
    if not DB_REVENUE or not finance_ids:
        return pd.DataFrame()
    notion = get_notion_client()
    all_r = _query_all(notion, DB_REVENUE)
    rows = []
    for p in all_r:
        props = p["properties"]
        linked = _relation_ids(props, "案件")
        if not any(fid in finance_ids for fid in linked):
            continue
        rows.append({
            "id":        p["id"],
            "說明":      _text(props, "說明"),
            "案件id":    linked[0] if linked else "",
            "類型":      _select(props, "類型"),
            "應收金額":  _num(props, "應收金額"),
            "實收金額":  _num(props, "實收金額"),
            "應收未收":  _num(props, "應收未收"),
            "收款日期":  _date(props, "收款日期"),
            "狀態":      _select(props, "狀態"),
            "備註":      _text(props, "備註"),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def load_vendor_payments(contract_ids: tuple) -> pd.DataFrame:
    """讀取廠商付款明細"""
    if not DB_PAYMENTS or not contract_ids:
        return pd.DataFrame()
    notion = get_notion_client()
    all_p = _query_all(notion, DB_PAYMENTS)
    rows = []
    for p in all_p:
        props = p["properties"]
        linked = _relation_ids(props, "發包項目")
        if not any(cid in contract_ids for cid in linked):
            continue
        rows.append({
            "id":         p["id"],
            "說明":       _text(props, "說明"),
            "發包id":     linked[0] if linked else "",
            "付款金額":   _num(props, "付款金額"),
            "付款日期":   _date(props, "付款日期"),
            "付款方式":   _select(props, "付款方式"),
            "備註":       _text(props, "備註"),
        })
    return pd.DataFrame(rows)


def clear_cache():
    load_finance_projects.clear()
    load_contracts.clear()
    load_revenue.clear()
    load_vendor_payments.clear()


# ── 寫入函數 ──────────────────────────────────────────────────────────────────
def add_revenue_record(finance_id: str, desc: str, rev_type: str,
                       receivable: float, received: float,
                       recv_date: str, status: str, note: str) -> bool:
    """新增一筆業主收款記錄"""
    notion = get_notion_client()
    props = {
        "說明":     {"title": [{"text": {"content": desc}}]},
        "案件":     {"relation": [{"id": finance_id}]},
        "應收金額": {"number": receivable},
        "實收金額": {"number": received},
        "狀態":     {"select": {"name": status}},
        "備註":     {"rich_text": [{"text": {"content": note}}]},
    }
    if rev_type:
        props["類型"] = {"select": {"name": rev_type}}
    if recv_date:
        props["收款日期"] = {"date": {"start": recv_date}}
    try:
        notion.pages.create(parent={"database_id": DB_REVENUE}, properties=props)
        clear_cache()
        return True
    except Exception as e:
        st.error(f"新增失敗：{e}")
        return False


def add_payment_record(contract_id: str, desc: str, amount: float,
                       pay_date: str, pay_method: str, note: str) -> bool:
    """新增一筆廠商付款明細"""
    notion = get_notion_client()
    props = {
        "說明":     {"title": [{"text": {"content": desc}}]},
        "發包項目": {"relation": [{"id": contract_id}]},
        "付款金額": {"number": amount},
        "備註":     {"rich_text": [{"text": {"content": note}}]},
    }
    if pay_method:
        props["付款方式"] = {"select": {"name": pay_method}}
    if pay_date:
        props["付款日期"] = {"date": {"start": pay_date}}
    try:
        notion.pages.create(parent={"database_id": DB_PAYMENTS}, properties=props)
        clear_cache()
        return True
    except Exception as e:
        st.error(f"新增失敗：{e}")
        return False
