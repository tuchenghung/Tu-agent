"""佑祥工程 — 財務記帳系統"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()
import notion_api as na

st.set_page_config(
    page_title="佑祥工程財務系統",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 密碼保護 ──────────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get("authenticated"):
        return True
    st.title("佑祥工程財務系統")
    pwd = st.text_input("請輸入密碼", type="password")
    if st.button("登入"):
        if pwd == "chocmay7361":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("密碼錯誤")
    return False

if not check_password():
    st.stop()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {
    background: #f8f9fa; border-radius: 12px; padding: 16px;
    border-left: 4px solid #1f77b4; margin-bottom: 8px;
}
.metric-card.danger  { border-left-color: #d62728; }
.metric-card.success { border-left-color: #2ca02c; }
.metric-card.warn    { border-left-color: #ff7f0e; }
.metric-value { font-size: 1.8rem; font-weight: 700; }
.metric-label { font-size: 0.85rem; color: #6c757d; }
</style>
""", unsafe_allow_html=True)


# ── 工具函數 ──────────────────────────────────────────────────────────────────
def fmt_ntd(v: float) -> str:
    return f"NT${v:,.0f}"


def status_badge(s: str) -> str:
    colors = {
        "進行中": "🟡", "已完成": "🟢", "設計規劃中": "🔵",
        "待收": "⚪", "已收": "🟢", "部分收": "🟡",
        "已付款": "🟢", "待發包": "⚪", "已發包": "🔵",
    }
    return f"{colors.get(s,'⚫')} {s}"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏗️ 佑祥工程")
    st.caption("財務記帳系統")
    st.divider()

    page = st.radio("選擇頁面", [
        "📊 財務總覽",
        "💰 案件收款",
        "🔧 廠商付款",
        "📈 現金流量",
        "📋 財務報表",
    ])

    st.divider()
    bank_balance = st.number_input(
        "🏦 公司銀行餘額（手動輸入）",
        min_value=0,
        value=st.session_state.get("bank_balance", 0),
        step=10000,
        format="%d",
        key="bank_balance_input",
    )
    st.session_state["bank_balance"] = bank_balance

    st.divider()
    if st.button("🔄 重新整理資料", use_container_width=True):
        na.clear_cache()
        st.rerun()
    st.caption(f"資料快取 5 分鐘")

    if not na.DB_REVENUE:
        st.warning("⚠️ 業主收款記錄 DB 尚未設定\n\n建好後在 `.env` 加入\n`NOTION_DB_REVENUE=<id>`")
    if not na.DB_PAYMENTS:
        st.warning("⚠️ 廠商付款明細 DB 尚未設定\n\n建好後在 `.env` 加入\n`NOTION_DB_PAYMENTS=<id>`")


# ── 載入資料 ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_all_data():
    df_fin = na.load_finance_projects()
    if df_fin.empty:
        return df_fin, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    fin_ids = tuple(df_fin["id"].tolist())
    df_con = na.load_contracts(fin_ids)
    df_rev = na.load_revenue(fin_ids)
    con_ids = tuple(df_con["id"].tolist()) if not df_con.empty else ()
    df_pay = na.load_vendor_payments(con_ids)
    return df_fin, df_con, df_rev, df_pay


try:
    df_fin, df_con, df_rev, df_pay = get_all_data()
except Exception as e:
    st.error(f"載入資料失敗：{e}")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# 頁面 1：財務總覽
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 財務總覽":
    st.title("📊 財務總覽")

    if df_fin.empty:
        st.info("尚無 YUSHI 案件資料，請先在 Notion 建立案件並設定公司別 = YUSHI")
        st.stop()

    # KPI 卡片
    total_contract = df_fin["承攬金額"].sum()
    total_cost     = df_fin["發包成本"].sum() + df_fin["其他成本"].sum()
    total_profit   = df_fin["毛利"].sum()
    avg_margin     = (total_profit / total_contract * 100) if total_contract else 0

    total_received  = df_rev["實收金額"].sum() if not df_rev.empty else 0
    total_receivable= df_rev["應收未收"].sum() if not df_rev.empty else 0
    total_paid      = df_pay["付款金額"].sum() if not df_pay.empty else 0
    total_payable   = df_con["成本"].sum() - total_paid if not df_con.empty else 0

    cols = st.columns(4)
    with cols[0]:
        st.metric("總合約金額", fmt_ntd(total_contract))
    with cols[1]:
        st.metric("總毛利（試算）", fmt_ntd(total_profit),
                  delta=f"{avg_margin:.1f}%",
                  delta_color="normal")
    with cols[2]:
        st.metric("業主應收未收", fmt_ntd(total_receivable),
                  delta="🔴 待收款" if total_receivable > 0 else "✅ 全收",
                  delta_color="off")
    with cols[3]:
        st.metric("廠商應付未付", fmt_ntd(total_payable),
                  delta="🔴 待付款" if total_payable > 0 else "✅ 全付",
                  delta_color="off")

    st.divider()

    # 銀行餘額 + 現金流速覽
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.subheader("🏦 資金概況")
        bank = bank_balance
        net_cash = bank + total_receivable - total_payable
        st.metric("銀行存款", fmt_ntd(bank))
        st.metric("加：應收", fmt_ntd(total_receivable))
        st.metric("減：應付", fmt_ntd(total_payable), delta_color="inverse")
        st.metric("淨現金（預估）", fmt_ntd(net_cash),
                  delta_color="normal" if net_cash >= 0 else "inverse")

    with col_b:
        st.subheader("📁 各案件毛利")
        if not df_fin.empty:
            fig = px.bar(
                df_fin.sort_values("毛利", ascending=True),
                x="毛利", y="專案名稱",
                orientation="h",
                color="毛利率",
                color_discrete_sequence=px.colors.qualitative.Set2,
                text="毛利率",
                labels={"毛利": "毛利 (NT$)", "專案名稱": ""},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 案件列表
    st.subheader("📋 案件一覽")
    display = df_fin[["專案名稱", "承攬金額", "已收金額", "撥款進度", "發包成本", "毛利", "毛利率", "狀態"]].copy()
    display["承攬金額"] = display["承攬金額"].apply(fmt_ntd)
    display["已收金額"] = display["已收金額"].apply(fmt_ntd)
    display["發包成本"] = display["發包成本"].apply(fmt_ntd)
    display["毛利"]    = display["毛利"].apply(fmt_ntd)
    display["撥款進度"] = display["撥款進度"].apply(lambda v: f"{v*100:.1f}%" if v else "0%")
    st.dataframe(display, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# 頁面 2：案件收款
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 案件收款":
    st.title("💰 案件收款追蹤")

    if df_fin.empty:
        st.info("尚無案件資料")
        st.stop()

    project_names = df_fin["專案名稱"].tolist()
    selected = st.selectbox("選擇案件", ["全部"] + project_names)

    # ── 輸入表單 ──────────────────────────────────────────────────────────────
    with st.expander("➕ 新增收款記錄", expanded=False):
        with st.form("form_revenue", clear_on_submit=True):
            f_project = st.selectbox("案件 *", project_names, key="rev_project")
            fc1, fc2 = st.columns(2)
            f_type    = fc1.selectbox("類型", ["開工款", "期中款", "完工款", "追加工程款", "其他"])
            f_status  = fc2.selectbox("狀態", ["已收", "待收", "部分收"])
            fa1, fa2  = st.columns(2)
            f_recv    = fa1.number_input("實收金額 (NT$) *", min_value=0, step=1000)
            f_due     = fa2.number_input("應收金額 (NT$)", min_value=0, step=1000,
                                          help="不填則與實收相同")
            f_date    = st.date_input("收款日期 *", value=date.today())
            f_desc    = st.text_input("說明（例：第一期款）")
            f_note    = st.text_input("備註")
            submitted = st.form_submit_button("✅ 儲存到 Notion", use_container_width=True,
                                              type="primary")
            if submitted:
                if not f_project or f_recv <= 0:
                    st.error("請填寫案件和實收金額")
                else:
                    fin_id = df_fin[df_fin["專案名稱"] == f_project]["id"].iloc[0]
                    due    = f_due if f_due > 0 else f_recv
                    label  = f_desc or f_type
                    ok = na.add_revenue_record(
                        fin_id, label, f_type, due, f_recv,
                        str(f_date), f_status, f_note
                    )
                    if ok:
                        st.success(f"已新增：{label}  NT${f_recv:,.0f}")
                        st.rerun()

    st.divider()

    if not df_rev.empty:
        df_show = df_rev.copy()
        if selected != "全部":
            sel_id = df_fin[df_fin["專案名稱"] == selected]["id"].iloc[0]
            df_show = df_show[df_show["案件id"] == sel_id]

        # 統計
        c1, c2, c3 = st.columns(3)
        c1.metric("應收合計",  fmt_ntd(df_show["應收金額"].sum()))
        c2.metric("已收合計",  fmt_ntd(df_show["實收金額"].sum()))
        c3.metric("應收未收",  fmt_ntd(df_show["應收未收"].sum()))

        st.divider()

        # 表格
        cols_show = ["說明", "類型", "應收金額", "實收金額", "應收未收", "收款日期", "狀態", "備註"]
        cols_show = [c for c in cols_show if c in df_show.columns]
        df_display = df_show[cols_show].copy()
        for col in ["應收金額", "實收金額", "應收未收"]:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(fmt_ntd)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.caption(f"[在 Notion 中編輯 ↗](https://app.notion.com/p/{na.DB_REVENUE.replace('-','')})")
    else:
        if not na.DB_REVENUE:
            st.warning("請先設定 NOTION_DB_REVENUE 環境變數")
        else:
            st.info("尚無收款記錄，請用上方表單新增")


# ══════════════════════════════════════════════════════════════════════════════
# 頁面 3：廠商付款
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔧 廠商付款":
    st.title("🔧 廠商付款追蹤")

    if df_con.empty:
        st.info("尚無發包資料，請先在 Notion 發包管理中建立發包項目")
        st.stop()

    # ── 輸入表單 ──────────────────────────────────────────────────────────────
    with st.expander("➕ 新增付款記錄", expanded=False):
        # 建立下拉清單：顯示 "廠商名稱｜工種" 方便選擇
        if not df_con.empty:
            df_con["_label"] = df_con["廠商名稱"] + "  ｜  " + df_con["案件名稱"] + "  (" + df_con["工種"] + ")"
            contract_options = df_con[["id", "_label"]].drop_duplicates("id")
        else:
            contract_options = pd.DataFrame(columns=["id", "_label"])

        with st.form("form_payment", clear_on_submit=True):
            f_contract = st.selectbox("發包項目（廠商｜案件｜工種）*",
                                       contract_options["_label"].tolist() if not contract_options.empty else ["無"],
                                       key="pay_contract")
            fp1, fp2 = st.columns(2)
            f_amount  = fp1.number_input("付款金額 (NT$) *", min_value=0, step=1000)
            f_method  = fp2.selectbox("付款方式", ["轉帳", "現金", "支票", "票據"])
            f_paydate = st.date_input("付款日期 *", value=date.today())
            f_desc    = st.text_input("說明（例：第一期款）")
            f_note    = st.text_input("備註")
            submitted2 = st.form_submit_button("✅ 儲存到 Notion", use_container_width=True,
                                               type="primary")
            if submitted2:
                if f_amount <= 0 or contract_options.empty:
                    st.error("請選擇發包項目並填寫金額")
                else:
                    sel_row = contract_options[contract_options["_label"] == f_contract]
                    if not sel_row.empty:
                        cid = sel_row.iloc[0]["id"]
                        label = f_desc or f"付款 {str(f_paydate)}"
                        ok = na.add_payment_record(cid, label, f_amount,
                                                   str(f_paydate), f_method, f_note)
                        if ok:
                            st.success(f"已新增：{label}  NT${f_amount:,.0f}")
                            st.rerun()

    st.divider()

    # 應付未付計算
    if not df_pay.empty:
        paid_by_contract = df_pay.groupby("發包id")["付款金額"].sum().reset_index()
        paid_by_contract.columns = ["id", "已付金額"]
        df_con_merged = df_con.merge(paid_by_contract, on="id", how="left")
        df_con_merged["已付金額"] = df_con_merged["已付金額"].fillna(0)
    else:
        df_con_merged = df_con.copy()
        df_con_merged["已付金額"] = df_con_merged["成本"].apply(
            lambda _: 0 if not na.DB_PAYMENTS else 0
        )
        # 若無付款明細 DB，用是否已撥款推算
        df_con_merged["已付金額"] = df_con_merged.apply(
            lambda r: r["成本"] if r["已撥款"] else 0, axis=1
        )

    df_con_merged["應付未付"] = df_con_merged["成本"] - df_con_merged["已付金額"]

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("發包總額",  fmt_ntd(df_con_merged["成本"].sum()))
    c2.metric("已付合計",  fmt_ntd(df_con_merged["已付金額"].sum()))
    c3.metric("應付未付",  fmt_ntd(df_con_merged["應付未付"].sum()))

    st.divider()

    # 待付款廠商優先列表
    st.subheader("⚠️ 尚未付清的發包項目")
    unpaid = df_con_merged[df_con_merged["應付未付"] > 0].sort_values("應付未付", ascending=False)
    if not unpaid.empty:
        cols_u = ["廠商名稱", "案件名稱", "工種", "成本", "已付金額", "應付未付", "狀態", "撥款日期"]
        cols_u = [c for c in cols_u if c in unpaid.columns]
        disp = unpaid[cols_u].copy()
        for col in ["成本", "已付金額", "應付未付"]:
            if col in disp.columns:
                disp[col] = disp[col].apply(fmt_ntd)
        st.dataframe(disp, use_container_width=True, hide_index=True)
    else:
        st.success("全部廠商款項已付清！")

    if not df_pay.empty:
        st.divider()
        st.subheader("📋 付款明細記錄")
        dp = df_pay[["說明", "付款金額", "付款日期", "付款方式", "備註"]].copy()
        dp["付款金額"] = dp["付款金額"].apply(fmt_ntd)
        st.dataframe(dp, use_container_width=True, hide_index=True)

    st.caption(f"[在 Notion 中管理發包 ↗](https://app.notion.com/p/{na.DB_CONTRACTS.replace('-','')})")


# ══════════════════════════════════════════════════════════════════════════════
# 頁面 4：現金流量
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 現金流量":
    st.title("📈 現金流量分析")

    has_rev = not df_rev.empty
    has_pay = not df_pay.empty

    if not has_rev and not has_pay:
        st.info("需要「業主收款記錄」和「廠商付款明細」兩個資料庫才能分析現金流")
        st.stop()

    # 月度彙總
    def to_month(s):
        try:
            return pd.to_datetime(s).strftime("%Y-%m")
        except:
            return None

    rows = []
    if has_rev:
        r = df_rev[df_rev["收款日期"] != ""].copy()
        r["月份"] = r["收款日期"].apply(to_month)
        r = r.dropna(subset=["月份"])
        for m, g in r.groupby("月份"):
            rows.append({"月份": m, "類型": "收入", "金額": g["實收金額"].sum()})

    if has_pay:
        p = df_pay[df_pay["付款日期"] != ""].copy()
        p["月份"] = p["付款日期"].apply(to_month)
        p = p.dropna(subset=["月份"])
        for m, g in p.groupby("月份"):
            rows.append({"月份": m, "類型": "支出", "金額": g["付款金額"].sum()})

    if not rows:
        st.info("尚無含日期的收付款記錄")
        st.stop()

    df_cf = pd.DataFrame(rows).sort_values("月份")

    fig = px.bar(
        df_cf, x="月份", y="金額", color="類型",
        barmode="group",
        color_discrete_map={"收入": "#2ca02c", "支出": "#d62728"},
        title="月度收支對比",
        labels={"金額": "NT$"},
        text_auto=".3s",
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 累積現金流
    pivot = df_cf.pivot_table(index="月份", columns="類型", values="金額", aggfunc="sum").fillna(0)
    if "收入" in pivot.columns and "支出" in pivot.columns:
        pivot["淨現金流"] = pivot["收入"] - pivot["支出"]
        pivot["累積淨流"] = pivot["淨現金流"].cumsum()
        st.subheader("累積現金流")
        fig2 = px.line(pivot.reset_index(), x="月份", y="累積淨流",
                       markers=True, title="累積淨現金流")
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(
            pivot.reset_index().rename(columns={"收入": "收入(NT$)", "支出": "支出(NT$)"}),
            use_container_width=True, hide_index=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# 頁面 5：財務報表
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 財務報表":
    st.title("📋 財務報表")

    year_options = sorted(set(
        pd.to_datetime(df_fin["開始日期"], errors="coerce").dt.year.dropna().astype(int).tolist()
    ), reverse=True) if not df_fin.empty else [date.today().year]
    year_options = year_options or [date.today().year]
    sel_year = st.selectbox("報表年度", year_options)

    st.subheader(f"📄 {sel_year} 年度管理用損益表（工程毛利）")
    st.caption("⚠️ 此為管理用財報，非稅務申報用，數字以承攬金額/1.05 為不含稅基礎")

    if df_fin.empty:
        st.info("無案件資料")
    else:
        # 以開始日期過濾年度
        df_year = df_fin.copy()
        df_year["年度"] = pd.to_datetime(df_year["開始日期"], errors="coerce").dt.year
        df_year = df_year[df_year["年度"] == sel_year]

        if df_year.empty:
            st.info(f"{sel_year} 年度無案件")
        else:
            tax_base   = df_year["承攬金額"].sum() / 1.05
            total_cost = df_year["發包成本"].sum() + df_year["其他成本"].sum()
            gross_p    = tax_base - total_cost
            margin_pct = (gross_p / tax_base * 100) if tax_base else 0

            data = {
                "項目": ["承攬金額（含稅）", "(-) 稅金 (5%)", "淨收入（不含稅）",
                         "(-) 發包成本", "(-) 其他成本", "= 毛利"],
                "金額": [
                    df_year["承攬金額"].sum(),
                    df_year["承攬金額"].sum() - tax_base,
                    tax_base,
                    df_year["發包成本"].sum(),
                    df_year["其他成本"].sum(),
                    gross_p,
                ],
            }
            df_report = pd.DataFrame(data)
            df_report["金額"] = df_report["金額"].apply(fmt_ntd)
            st.dataframe(df_report, use_container_width=True, hide_index=True)
            st.metric(f"毛利率", f"{margin_pct:.1f}%")

    st.divider()
    st.subheader("📊 各案件詳細損益")
    if not df_fin.empty:
        df_detail = df_fin[["專案名稱", "承攬金額", "發包成本", "其他成本", "毛利", "毛利率", "狀態"]].copy()
        for col in ["承攬金額", "發包成本", "其他成本", "毛利"]:
            df_detail[col] = df_detail[col].apply(fmt_ntd)
        st.dataframe(df_detail, use_container_width=True, hide_index=True)

        if st.button("📥 下載 CSV"):
            csv = df_fin.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("確認下載", csv, f"yushi_finance_{sel_year}.csv", "text/csv")
