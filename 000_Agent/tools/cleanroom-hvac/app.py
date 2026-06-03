"""
無塵室空調設計系統
================================
輸入平面圖 → 系統規劃 → 設備計算 → 圖面輸出 → 報價
"""

import io
import math
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from calculations import (
    ping_to_m2, calc_volume, calc_airflow, calc_rt,
    select_chw_pipe, calc_cost, calc_mau_count,
)
from electrical import calc_circuit, calc_panel_nfb, build_hvac_circuits
from reference_data import ACH_TABLE, PING_TO_M2, COST
from floor_plan import parse_dxf, make_empty_fp, draw_floorplan
from system_design import (
    recommend_system, draw_system_diagram, export_system_dxf, SYSTEM_OPTIONS, SYSTEM_DESC,
)
from layout_duct import plan_duct_routes, draw_duct_layout, export_duct_dxf
from layout_pipe import build_pipe_schedule, draw_pipe_schematic, export_pipe_dxf
from layout_elec import draw_sld, export_sld_dxf
from layout_ctrl import (
    build_control_schedule, io_summary, draw_ctrl_diagram, export_ctrl_dxf,
)
from quotation import calc_quote, to_excel, draw_quote_chart

# ── 頁面設定 ─────────────────────────────────────────────────────
st.set_page_config(page_title="無塵室空調設計系統", layout="wide", page_icon="❄️")

st.markdown("""
<style>
.stTabs [data-baseweb="tab"]{font-size:13px; padding:6px 14px;}
.metric-box{background:#1e2130;border-radius:8px;padding:10px;margin:4px;}
</style>
""", unsafe_allow_html=True)

st.title("❄️ 無塵室空調設計系統")
st.caption("平面圖輸入 → 系統規劃 → 計算 → 圖面（DXF可下載） → 報價")

# ── Session State 初始化 ─────────────────────────────────────────
def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("fp", None)           # floor plan data
_init("rooms", [])          # confirmed room list
_init("building", {})       # floor/building info
_init("system_recs", [])    # system recommendations
_init("chosen_system", "CH+MAU+RCU")
_init("inputs", {})         # HVAC calc inputs
_init("results", {})        # HVAC calc results
_init("equipment", {})      # equipment counts
_init("circuits", [])       # electrical circuits
_init("panel", {})          # panel NFB
_init("ctrl_schedule", [])  # control point schedule
_init("io_sum", {})
_init("pipe_data", {})
_init("duct_routes", [])
_init("quote", {})

# ── Helper ───────────────────────────────────────────────────────
def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.read()


def make_fig(figsize=(14, 7)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#12121f")
    return fig, ax


# ════════════════════════════════════════════════════════════════
TABS = st.tabs([
    "① 平面圖輸入",
    "② 空間確認",
    "③ 系統架構",
    "④ 設備規劃",
    "⑤ 管路設計",
    "⑥ 風管配置",
    "⑦ 電力規劃",
    "⑧ 自動控制",
    "⑨ 報價",
])

# ════════════════════════════════════════════════════════════════
# Tab ① 平面圖輸入
# ════════════════════════════════════════════════════════════════
with TABS[0]:
    st.subheader("上傳平面圖")

    col_l, col_r = st.columns([1, 2])
    with col_l:
        input_mode = st.radio("輸入方式", ["上傳 DXF", "上傳 JPG/PNG（手動補面積）", "手動輸入（無圖）"],
                              key="input_mode")

        wall_layers_input = st.text_area(
            "DXF 牆體圖層（一行一個）",
            "C2-RC牆\nC3-輕質隔間\nWALL\n牆體\nPARTITION",
            height=100,
        )
        wall_layers = [l.strip() for l in wall_layers_input.splitlines() if l.strip()]

    with col_r:
        if input_mode == "上傳 DXF":
            uploaded = st.file_uploader("拖曳 DXF 檔案", type=["dxf"])
            if uploaded:
                with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name
                try:
                    with st.spinner("解析 DXF 中…"):
                        fp = parse_dxf(tmp_path, wall_layers=wall_layers)
                    st.session_state["fp"] = fp
                    st.session_state["rooms"] = fp["rooms"]
                    st.success(f"解析完成｜牆線 {len(fp['walls'])} 段｜辨識空間 {len(fp['rooms'])} 個")
                except Exception as e:
                    st.error(f"DXF 解析失敗：{e}")

        elif input_mode == "上傳 JPG/PNG（手動補面積）":
            img_file = st.file_uploader("上傳平面圖圖片", type=["jpg", "jpeg", "png"])
            if img_file:
                st.image(img_file, caption="平面圖（參考用）", use_container_width=True)
                st.info("圖片模式：請在「② 空間確認」手動填寫各房間面積")
                st.session_state["fp"] = make_empty_fp()
                st.session_state["rooms"] = []

        else:  # 手動
            total_area = st.number_input("總面積（m²）", min_value=1.0, value=1700.0, step=10.0)
            if st.button("建立空白專案"):
                st.session_state["fp"] = make_empty_fp(total_area)
                st.session_state["rooms"] = st.session_state["fp"]["rooms"]
                st.success("已建立，請前往②空間確認填寫資料")

    # 平面圖預覽
    fp = st.session_state.get("fp")
    if fp and (fp.get("walls") or fp.get("rooms")):
        st.divider()
        st.subheader("平面圖預覽")
        fig, ax = make_fig((14, 8))
        draw_floorplan(ax, fp)
        ax.set_title("平面圖底圖（牆體 + 空間標注）", color="white", fontsize=10)
        st.pyplot(fig)
        plt.close(fig)


# ════════════════════════════════════════════════════════════════
# Tab ② 空間確認
# ════════════════════════════════════════════════════════════════
with TABS[1]:
    st.subheader("確認空間清單 + 樓層資訊")

    col1, col2 = st.columns([2, 1])
    with col2:
        st.subheader("建築資訊")
        floors = st.number_input("樓層數", min_value=1, value=1)
        floor_ht = st.number_input("標準層高（m）", min_value=2.0, value=3.0, step=0.1)
        bldg_note = st.text_area("備注（用途、特殊條件）", height=80)
        st.session_state["building"] = {
            "floors": floors,
            "floor_height": floor_ht,
            "note": bldg_note,
            "total_area_m2": sum(r.get("area_m2", 0)
                                 for r in st.session_state.get("rooms", [])),
        }

    with col1:
        st.subheader("房間清單")
        rooms = st.session_state.get("rooms", [])

        # 新增房間
        with st.expander("＋ 新增房間"):
            nc1, nc2, nc3 = st.columns(3)
            new_name = nc1.text_input("房間名稱", key="new_name")
            new_area = nc2.number_input("面積（m²）", min_value=0.0, value=20.0, key="new_area")
            new_cls = nc3.selectbox("潔淨等級", list(ACH_TABLE.keys()), key="new_cls")
            if st.button("新增"):
                rooms.append({"name": new_name or f"區域{len(rooms)+1}",
                              "x": 0, "y": 0,
                              "area_m2": new_area,
                              "class": new_cls,
                              "is_cleanroom": new_cls != "一般空調 (ISO 9)"})
                st.session_state["rooms"] = rooms
                st.rerun()

        # 顯示 + 編輯現有房間
        if rooms:
            df_rooms = pd.DataFrame([
                {"#": i, "名稱": r["name"],
                 "面積(m²)": r["area_m2"],
                 "坪數": round(r["area_m2"] / PING_TO_M2, 1),
                 "潔淨等級": r.get("class", "一般空調 (ISO 9)"),
                 "無塵室": "✓" if r.get("is_cleanroom") else ""}
                for i, r in enumerate(rooms)
            ])
            st.dataframe(df_rooms, use_container_width=True, hide_index=True)

            # 總面積
            total = sum(r.get("area_m2", 0) for r in rooms)
            st.metric("總面積", f"{total:.0f} m²",
                      f"約 {total/PING_TO_M2:.0f} 坪")

            # 更新 building total
            st.session_state["building"]["total_area_m2"] = total

            # 刪除
            del_idx = st.number_input("刪除第 # 行（-1 不刪）", min_value=-1,
                                      max_value=len(rooms)-1, value=-1)
            if st.button("刪除") and del_idx >= 0:
                rooms.pop(del_idx)
                st.session_state["rooms"] = rooms
                st.rerun()
        else:
            st.info("尚無房間資料，請在左側新增或先上傳 DXF")


# ════════════════════════════════════════════════════════════════
# Tab ③ 系統架構
# ════════════════════════════════════════════════════════════════
with TABS[2]:
    st.subheader("空調系統型式選定")

    rooms = st.session_state.get("rooms", [])
    building = st.session_state.get("building", {})

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🤖 AI 自動推薦系統型式"):
            if rooms:
                recs = recommend_system(rooms, building)
                st.session_state["system_recs"] = recs
            else:
                st.warning("請先在②空間確認填寫房間資料")

        recs = st.session_state.get("system_recs", [])
        if recs:
            st.subheader("推薦結果")
            for rec in recs:
                with st.container(border=True):
                    st.write(f"**{rec['zone']}**（{rec['class']}，{rec['area_m2']} m²）")
                    st.success(f"建議系統：**{rec['recommended']}**")
                    st.caption(rec["reason"])
                    st.write("其他選項：" + "、".join(rec["alternatives"]))

        st.divider()
        chosen = st.selectbox("確認/修改系統型式", SYSTEM_OPTIONS,
                              index=SYSTEM_OPTIONS.index(st.session_state["chosen_system"])
                              if st.session_state["chosen_system"] in SYSTEM_OPTIONS else 0)
        st.session_state["chosen_system"] = chosen
        st.info(SYSTEM_DESC.get(chosen, ""))

    with col2:
        st.subheader("系統架構圖")
        n_rooms = len(rooms) or 3
        fig, ax = make_fig((8, 5))
        draw_system_diagram(ax, chosen, n_rooms)
        st.pyplot(fig)
        plt.close(fig)

        # DXF 下載
        dxf_buf = io.BytesIO()
        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
            export_system_dxf(chosen, tmp.name)
            with open(tmp.name, "rb") as f:
                dxf_buf.write(f.read())
        st.download_button("⬇ 下載系統架構圖 DXF", dxf_buf.getvalue(),
                           file_name=f"系統架構圖_{chosen}.dxf",
                           mime="application/octet-stream")


# ════════════════════════════════════════════════════════════════
# Tab ④ 設備規劃
# ════════════════════════════════════════════════════════════════
with TABS[3]:
    st.subheader("設備數量規劃")

    rooms = st.session_state.get("rooms", [])
    building = st.session_state.get("building", {})
    system_type = st.session_state.get("chosen_system", "CH+MAU+RCU")
    fp = st.session_state.get("fp")

    total_area = sum(r.get("area_m2", 0) for r in rooms) or 1700.0
    height_m = building.get("floor_height", 3.0)
    class_name = rooms[0].get("class", "Class 10,000 (ISO 7)") if rooms else "Class 10,000 (ISO 7)"

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("計算輸入")
        area_m2 = st.number_input("總面積（m²）", value=float(total_area), step=10.0)
        h = st.number_input("天花高度（m）", value=height_m, step=0.1)
        cls = st.selectbox("主要潔淨等級", list(ACH_TABLE.keys()),
                           index=list(ACH_TABLE.keys()).index(class_name)
                           if class_name in ACH_TABLE else 2)
        exhaust = st.number_input("排氣量（CMH）", value=0.0, step=100.0)
        equip_kw = st.number_input("設備發熱量（kW）", value=0.0, step=10.0)
        custom_ach = st.number_input("自訂 ACH（0=預設）", value=0, min_value=0, max_value=600)
        custom_ach_val = float(custom_ach) if custom_ach > 0 else None

    with col2:
        st.subheader("計算結果")
        vol = calc_volume(area_m2, h)
        af = calc_airflow(vol, cls, system_type, custom_ach_val, exhaust)
        rt = calc_rt(area_m2, cls, system_type, equip_kw)
        chw = select_chw_pipe(rt["total_rt"])
        mau_n = calc_mau_count(af["mau_cmh"])
        duct_m2 = area_m2 * 0.5

        # 依系統型式推算設備台數
        rcu_n, ahu_n, fcu_n, dc_n, ffu_n = 0, 0, 0, 0, 0
        if "RCU" in system_type:
            rcu_n = max(1, math.ceil(area_m2 / 300))
        if "AHU" in system_type:
            ahu_n = max(1, math.ceil(area_m2 / 500))
        if "FCU" in system_type:
            fcu_n = max(1, math.ceil(area_m2 / 20))
        if "D/C" in system_type:
            dc_n = max(1, math.ceil(area_m2 / 200))
        if "FFU" in system_type:
            ffu_n = af["ffu_count"]

        equipment = {
            "mau_count": mau_n,
            "rcu_count": rcu_n,
            "ahu_count": ahu_n,
            "fcu_count": fcu_n,
            "dc_count": dc_n,
            "ffu_count": ffu_n,
        }

        # 儲存
        st.session_state["inputs"] = {
            "area_m2": area_m2, "height_m": h, "volume_m3": vol,
            "class_name": cls, "system_type": system_type,
            "custom_ach": custom_ach_val, "exhaust_cmh": exhaust,
            "equipment_heat_kw": equip_kw, "area_ping": area_m2 / PING_TO_M2,
        }
        st.session_state["results"] = {"airflow": af, "rt": rt, "chw_pipe": chw}
        st.session_state["equipment"] = equipment

        eq_rows = []
        if mau_n: eq_rows.append(("MAU 外氣處理機", mau_n, "台", f"5400 CMH/台"))
        if ahu_n: eq_rows.append(("AHU 空調箱", ahu_n, "台", "依風量選型"))
        if rcu_n: eq_rows.append(("RCU 循環盤管", rcu_n, "台", f"~{af['rcu_cmh']/max(rcu_n,1):.0f} CMH/台"))
        if fcu_n: eq_rows.append(("FCU 風機盤管", fcu_n, "台", f"~{rt['total_rt']/max(fcu_n,1):.1f} RT/台"))
        if ffu_n: eq_rows.append(("FFU 風機過濾單元", ffu_n, "台", "900 CMH/台"))
        if dc_n:  eq_rows.append(("D/C 乾盤管", dc_n, "台", "顯熱冷卻"))
        eq_rows.append(("冰水主機 Chiller", 1, "套", f"{rt['total_rt']:.1f} RT"))
        eq_rows.append(("冰水管主管", 1, "式", chw))

        df_eq = pd.DataFrame(eq_rows, columns=["設備", "數量", "單位", "規格"])
        st.dataframe(df_eq, use_container_width=True, hide_index=True)

        st.metric("冷凍噸", f"{rt['total_rt']} RT")
        st.metric("主機 RT（含參差）", f"{rt['diversity_rt']} RT")
        st.metric("冰水管徑", chw)

    # 設備位置示意
    if fp:
        st.divider()
        st.subheader("設備位置示意圖")
        fig, ax = make_fig((14, 7))
        draw_floorplan(ax, fp)
        # 在 bbox 角落標示機房位置
        bbox = fp.get("bbox", (0, 0, 10000, 10000))
        x0, y0, x1, y1 = bbox
        ew, eh = (x1 - x0) * 0.1, (y1 - y0) * 0.1
        import matplotlib.patches as mpatches
        er = mpatches.Rectangle((x0, y0), ew, eh, linewidth=2,
                                  edgecolor="#e63946", facecolor="#e6394640")
        ax.add_patch(er)
        ax.text(x0 + ew/2, y0 + eh/2, f"機房\nChiller\n{rt['total_rt']:.0f}RT",
                ha="center", va="center", color="white", fontsize=7)
        ax.set_title("設備位置示意（機房建議角落設置）", color="white", fontsize=10)
        st.pyplot(fig)
        plt.close(fig)


# ════════════════════════════════════════════════════════════════
# Tab ⑤ 管路設計
# ════════════════════════════════════════════════════════════════
with TABS[4]:
    st.subheader("冰水管 / 冷卻水管 / 排水管設計")

    res = st.session_state.get("results", {})
    fp = st.session_state.get("fp")
    floors = st.session_state.get("building", {}).get("floors", 1)

    if not res:
        st.info("請先完成 ④ 設備規劃")
    else:
        rt = res["rt"]
        pipe_data = build_pipe_schedule(rt, floors)
        st.session_state["pipe_data"] = pipe_data

        col1, col2, col3 = st.columns(3)
        col1.metric("冰水管 (CHW)", pipe_data["chw"]["size"],
                    f"{pipe_data['chw']['flow_gpm']} GPM / {pipe_data['chw']['flow_cmh']} CMH")
        col2.metric("冷卻水管 (CW)", pipe_data["cw"]["size"],
                    f"{pipe_data['cw']['flow_gpm']} GPM / {pipe_data['cw']['flow_cmh']} CMH")
        col3.metric("排水管", pipe_data["drain"]["size"])

        # 管路系統圖
        fig, ax = make_fig((14, 7))
        draw_pipe_schematic(ax, pipe_data, st.session_state.get("chosen_system", ""))
        st.pyplot(fig)
        plt.close(fig)

        # DXF 下載
        if fp:
            dxf_buf = io.BytesIO()
            with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
                export_pipe_dxf(pipe_data, fp, tmp.name)
                with open(tmp.name, "rb") as f:
                    dxf_buf.write(f.read())
            st.download_button("⬇ 下載管路配置圖 DXF", dxf_buf.getvalue(),
                               file_name="管路配置圖.dxf",
                               mime="application/octet-stream")


# ════════════════════════════════════════════════════════════════
# Tab ⑥ 風管配置
# ════════════════════════════════════════════════════════════════
with TABS[5]:
    st.subheader("風管配置圖")

    fp = st.session_state.get("fp")
    res = st.session_state.get("results", {})
    rooms = st.session_state.get("rooms", [])

    if not res:
        st.info("請先完成 ④ 設備規劃")
    else:
        af = res["airflow"]
        bbox = (fp or make_empty_fp()).get("bbox", (0, 0, 10000, 10000))
        routes = plan_duct_routes(rooms, af, bbox)
        st.session_state["duct_routes"] = routes

        fig, ax = make_fig((14, 8))
        draw_duct_layout(ax, fp or make_empty_fp(), routes)
        st.pyplot(fig)
        plt.close(fig)

        # 風管尺寸表
        rows = [{"類型": r["type"], "說明": r["label"],
                 "管寬(mm)": r["width_mm"]}
                for r in routes if r["type"] != "diffuser"]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # DXF 下載
        dxf_buf = io.BytesIO()
        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
            export_duct_dxf(fp or make_empty_fp(), routes, tmp.name)
            with open(tmp.name, "rb") as f:
                dxf_buf.write(f.read())
        st.download_button("⬇ 下載風管配置圖 DXF", dxf_buf.getvalue(),
                           file_name="風管配置圖.dxf",
                           mime="application/octet-stream")


# ════════════════════════════════════════════════════════════════
# Tab ⑦ 電力規劃
# ════════════════════════════════════════════════════════════════
with TABS[6]:
    st.subheader("空調電力規劃 & 單線圖（SLD）")

    res = st.session_state.get("results", {})
    eq = st.session_state.get("equipment", {})

    if not res:
        st.info("請先完成 ④ 設備規劃")
    else:
        af = res["airflow"]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("設備電力參數")
            mau_kw = st.number_input("MAU 單台馬達 kW", value=15.0, step=0.5)
            mau_n = st.number_input("MAU 台數", value=int(eq.get("mau_count", 0)))
            ahu_kw = st.number_input("AHU/RCU 單台 kW", value=0.0, step=0.5)
            ahu_n = st.number_input("AHU/RCU 台數", value=int(eq.get("ahu_count", 0) + eq.get("rcu_count", 0)))
            ffu_kw = st.number_input("FFU 單台 kW (1φ-220V)",
                                     value=0.1 if eq.get("ffu_count", 0) > 0 else 0.0, step=0.05)
            ffu_n = st.number_input("FFU 台數", value=int(eq.get("ffu_count", 0)))
            pump_kw = st.number_input("冰水泵 kW", value=0.0, step=0.5)
            pump_n = st.number_input("冰水泵 台數", value=0)
            humid_n = st.number_input("加濕器台數（0.1kW/台）", value=0)

        with col2:
            if st.button("計算電力分路 & 繪製 SLD"):
                circuits = build_hvac_circuits(
                    mau_kw=mau_kw, mau_count=int(mau_n),
                    ahu_kw=ahu_kw, ahu_count=int(ahu_n),
                    ffu_kw=ffu_kw, ffu_count=int(ffu_n),
                    pump_kw=pump_kw, pump_count=int(pump_n),
                    humidifier_kw=0.1, humidifier_count=int(humid_n),
                )
                panel = calc_panel_nfb(circuits) if circuits else {}
                st.session_state["circuits"] = circuits
                st.session_state["panel"] = panel

            circuits = st.session_state.get("circuits", [])
            panel = st.session_state.get("panel", {})
            if circuits:
                df_elec = pd.DataFrame([{
                    "設備": c["name"], "kW": c["kw"],
                    "電壓": f"{c['voltage']}V {c['phase']}",
                    "FLC(A)": c["flc_a"], "NFB AT": c["nfb_at"],
                    "線徑mm²": c["wire_mm2"], "EMT φ": c["emt_phi"],
                    "E線mm²": c["gnd_mm2"], "啟動": c["start_method"],
                } for c in circuits])
                st.dataframe(df_elec, use_container_width=True, hide_index=True)
                if panel:
                    st.metric("總 NFB", f"{panel['panel_nfb_at']}A / {panel['panel_nfb_af']}",
                              f"計算電流 {panel['total_required_a']:.1f}A")

        # SLD
        circuits = st.session_state.get("circuits", [])
        panel = st.session_state.get("panel", {})
        if circuits:
            st.divider()
            fig, ax = make_fig((14, 8))
            draw_sld(ax, circuits, panel)
            st.pyplot(fig)
            plt.close(fig)

            dxf_buf = io.BytesIO()
            with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
                export_sld_dxf(circuits, panel, tmp.name)
                with open(tmp.name, "rb") as f:
                    dxf_buf.write(f.read())
            st.download_button("⬇ 下載 SLD DXF", dxf_buf.getvalue(),
                               file_name="空調SLD.dxf",
                               mime="application/octet-stream")


# ════════════════════════════════════════════════════════════════
# Tab ⑧ 自動控制
# ════════════════════════════════════════════════════════════════
with TABS[7]:
    st.subheader("自動控制架構 & 控制點表")

    eq = st.session_state.get("equipment", {})
    system_type = st.session_state.get("chosen_system", "CH+MAU+RCU")

    if not eq:
        st.info("請先完成 ④ 設備規劃")
    else:
        schedule = build_control_schedule(system_type, eq)
        io_sum = io_summary(schedule)
        st.session_state["ctrl_schedule"] = schedule
        st.session_state["io_sum"] = io_sum

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("AI（類比輸入）", io_sum.get("AI", 0))
        col2.metric("DI（數位輸入）", io_sum.get("DI", 0))
        col3.metric("AO（類比輸出）", io_sum.get("AO", 0))
        col4.metric("DO（數位輸出）", io_sum.get("DO", 0))
        st.metric("合計控制點數", io_sum.get("total", 0))

        st.subheader("控制點表")
        df_ctrl = pd.DataFrame(schedule).drop(columns=["total"], errors="ignore")
        df_ctrl = df_ctrl.rename(columns={
            "device": "設備", "tag": "標記", "description": "說明",
            "io_type": "I/O 型別", "count": "台數",
        })
        st.dataframe(df_ctrl, use_container_width=True, hide_index=True)

        st.divider()
        fig, ax = make_fig((14, 8))
        draw_ctrl_diagram(ax, system_type, eq, io_sum)
        st.pyplot(fig)
        plt.close(fig)

        dxf_buf = io.BytesIO()
        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
            export_ctrl_dxf(system_type, io_sum, tmp.name)
            with open(tmp.name, "rb") as f:
                dxf_buf.write(f.read())
        st.download_button("⬇ 下載控制架構圖 DXF", dxf_buf.getvalue(),
                           file_name="自動控制架構圖.dxf",
                           mime="application/octet-stream")


# ════════════════════════════════════════════════════════════════
# Tab ⑨ 報價
# ════════════════════════════════════════════════════════════════
with TABS[8]:
    st.subheader("空調工程報價")

    res = st.session_state.get("results", {})
    eq = st.session_state.get("equipment", {})
    io_sum = st.session_state.get("io_sum", {})
    inp = st.session_state.get("inputs", {})

    if not res:
        st.info("請先完成 ④ 設備規劃")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            markup = st.slider("加價倍率（成本→售價）", 1.10, 1.80, 1.30, step=0.05)
            st.caption("1.30 = 成本 × 1.3 = 售價（約 23% 毛利）")

            if st.button("計算報價"):
                duct_m2 = inp.get("area_m2", 0) * 0.5
                quote = calc_quote(
                    area_m2=inp.get("area_m2", 0),
                    rt_result=res["rt"],
                    airflow_result=res["airflow"],
                    system_type=st.session_state.get("chosen_system", ""),
                    equipment=eq,
                    io_sum=io_sum,
                    duct_m2=duct_m2,
                    markup=markup,
                )
                st.session_state["quote"] = quote

        quote = st.session_state.get("quote", {})
        if quote:
            with col1:
                st.metric("成本合計（未稅）",
                          f"NT$ {quote['subtotal']/10000:.1f} 萬")
                st.metric(f"建議售價（×{quote['markup']}）",
                          f"NT$ {quote['selling']/10000:.1f} 萬",
                          f"每坪 NT$ {quote['unit_price_per_ping']:,.0f}")
                st.metric("含稅售價（+5%）",
                          f"NT$ {quote['selling_with_tax']/10000:.1f} 萬")

            with col2:
                # 圓餅圖
                fig, ax = plt.subplots(figsize=(7, 5))
                fig.patch.set_facecolor("#12121f")
                draw_quote_chart(ax, quote)
                st.pyplot(fig)
                plt.close(fig)

            st.divider()
            st.subheader("報價明細")
            df_q = pd.DataFrame(quote["items"])
            df_q["amount_fmt"] = df_q["amount"].apply(lambda x: f"NT$ {x:,}")
            df_q = df_q.rename(columns={
                "category": "類別", "item": "品項", "unit": "單位",
                "qty": "數量", "unit_price": "單價", "amount_fmt": "金額",
            })
            st.dataframe(df_q[["類別", "品項", "單位", "數量", "單價", "金額"]],
                         use_container_width=True, hide_index=True)

            # Excel 下載
            excel_bytes = to_excel(quote)
            st.download_button(
                "⬇ 下載報價 Excel",
                excel_bytes,
                file_name=f"空調報價_{quote['system_type']}_{int(quote['area_m2'])}m2.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
