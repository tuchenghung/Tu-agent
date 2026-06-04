# 自動控制架構模組 — 控制點表、DDC 架構圖、DXF 匯出

# 矽品CHC案實測 I/O 點數（來源：無塵室空調監控系統IO點數表.md）
# MAU：22點/2台（一用一備對）→ 每台 11 點
# EXF：5點/台；D/C（乾盤管）：2點/分區；FFU：1點/台（僅狀態）
CTRL_POINTS = {
    "MAU": [
        # DO=1, AO=3, DI=3, AI=4 → 共 11 點/台（兩台=22點，符合知識庫）
        ("FC",   "開/停機",             "DO"),
        ("CCV",  "冰水閥（比例）",      "AO"),
        ("HCV",  "熱水閥（比例）",      "AO"),
        ("INV",  "變頻器控制",          "AO"),
        ("FS",   "運轉確認",            "DI"),
        ("FT",   "跳脫（過電流）",      "DI"),
        ("DPS",  "過濾器差壓（初+中效）","DI"),
        ("SAT",  "送風溫度",            "AI"),
        ("SAH",  "送風濕度",            "AI"),
        ("SP",   "室內靜壓",            "AI"),
        ("FINV", "VFD 頻率回饋",        "AI"),
    ],
    "EXF": [
        # 5點/台
        ("FC",   "開/停機",       "DO"),
        ("INV",  "變頻器控制",    "AO"),
        ("FS",   "運轉確認",      "DI"),
        ("FT",   "跳脫",          "DI"),
        ("FINV", "VFD 頻率回饋",  "AI"),
    ],
    "RCU": [
        ("TI",  "迴風溫度",    "AI"),
        ("TO",  "出風溫度",    "AI"),
        ("CCV", "冷盤管閥",    "AO"),
        ("FC",  "風車啟停",    "DO"),
        ("FS",  "風車故障",    "DI"),
    ],
    "AHU": [
        ("TI",  "迴風溫度",    "AI"),
        ("HI",  "迴風濕度",    "AI"),
        ("TO",  "出風溫度",    "AI"),
        ("DPS", "過濾器差壓",  "DI"),
        ("CCV", "冷盤管閥",    "AO"),
        ("FC",  "送風機啟停",  "DO"),
        ("FS",  "送風機故障",  "DI"),
        ("SP",  "靜壓感測",    "AI"),
        ("VFD", "變頻器控制",  "AO"),
    ],
    "FCU": [
        ("TI",  "室溫感測",    "AI"),
        ("CCV", "冷盤管閥",    "AO"),
        ("FC",  "風機啟停",    "DO"),
        ("FS",  "風機故障",    "DI"),
    ],
    "D/C": [
        # 乾式盤管每分區 2 點（AO+AI）
        ("MV",  "比例式電動閥（MV）", "AO"),
        ("TI",  "室內溫度感測",       "AI"),
    ],
    "FFU": [
        # Fan Filter Unit 每台 1 點（只監狀態，非個別調速）
        ("FS",  "運轉狀態確認",        "DI"),
    ],
    "Chiller": [
        ("START",    "主機啟停",        "DO"),
        ("STATUS",   "主機狀態",        "DI"),
        ("FAULT",    "主機故障",        "DI"),
        ("CHWST",    "冰水出口溫度",    "AI"),
        ("CHWRT",    "冰水回水溫度",    "AI"),
        ("CHWFLOW",  "冰水流量",        "AI"),
    ],
}


def build_control_schedule(system_type: str, equipment: dict) -> list:
    """
    依系統型式建立控制點表。
    equipment: {mau_count, rcu_count, ahu_count, fcu_count, dc_count, ffu_count}
    回傳: [{device, tag, description, io_type, count, total}, ...]
    """
    rows = []
    mau_n = equipment.get("mau_count", 0)
    rcu_n = equipment.get("rcu_count", 0)
    ahu_n = equipment.get("ahu_count", 0)
    fcu_n = equipment.get("fcu_count", 0)
    dc_n  = equipment.get("dc_count", 0)
    ffu_n = equipment.get("ffu_count", 0)

    def add_pts(device, count, key):
        for tag, desc, io_type in CTRL_POINTS.get(key, []):
            rows.append({
                "device": device,
                "tag": tag,
                "description": desc,
                "io_type": io_type,
                "count": count,
                "total": count,
            })

    if mau_n > 0:
        add_pts(f"MAU × {mau_n}台", mau_n, "MAU")
    if rcu_n > 0:
        add_pts(f"RCU × {rcu_n}台", rcu_n, "RCU")
    if ahu_n > 0:
        add_pts(f"AHU × {ahu_n}台", ahu_n, "AHU")
    if fcu_n > 0:
        add_pts(f"FCU × {fcu_n}台", fcu_n, "FCU")
    if dc_n > 0:
        # 乾盤管：每台視為一個控制分區（AO+AI各1）
        add_pts(f"D/C 乾盤管 × {dc_n}分區", dc_n, "D/C")
    if ffu_n > 0:
        # FFU：每台 DI×1（運轉狀態），不做個別調速
        add_pts(f"FFU × {ffu_n}台", ffu_n, "FFU")
    add_pts("冰水主機 × 1台", 1, "Chiller")

    return rows


def io_summary(schedule: list) -> dict:
    ai = di = ao = do_ = 0
    for r in schedule:
        n = r["count"]
        t = r["io_type"]
        if t == "AI":  ai += n
        elif t == "DI": di += n
        elif t == "AO": ao += n
        elif t == "DO": do_ += n
    return {"AI": ai, "DI": di, "AO": ao, "DO": do_,
            "total": ai + di + ao + do_}


# ── matplotlib DDC 架構圖 ─────────────────────────────────────────

def draw_ctrl_diagram(ax, system_type: str, equipment: dict, io_sum: dict):
    import matplotlib.patches as mpatches

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_facecolor("#12121f")
    ax.axis("off")

    def box(x, y, w, h, label, color="#264653", fs=8):
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor="white", linewidth=1.2, alpha=0.9,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                color="white", fontsize=fs, fontweight="bold")

    def link(x1, y1, x2, y2, label="", color="#aaaacc"):
        ax.annotate("", (x2, y2), (x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.3))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, label,
                    ha="center", color=color, fontsize=6.5)

    # BMS/監控主機
    box(4.5, 6.5, 3.0, 1.0, "BMS 監控主機\n中央管理系統", "#1d3461", fs=9)

    # DDC 控制器
    box(1.5, 4.5, 2.2, 0.9, "DDC 控制器\n(MAU/AHU)", "#2a9d8f")
    box(5.0, 4.5, 2.2, 0.9, "DDC 控制器\n(RCU/FCU)", "#e9c46a")
    box(8.5, 4.5, 2.2, 0.9, "DDC 控制器\n(Chiller)", "#457b9d")

    # 通訊匯流排
    ax.plot([1.5, 10.7], [5.8, 5.8], color="#f4c430", lw=2.5, ls="--")
    ax.text(6.0, 5.95, "Modbus / BACnet 通訊匯流排", ha="center",
            color="#f4c430", fontsize=7)
    ax.plot([2.6, 6.0], [5.8, 6.5], color="#aaaacc", lw=1)
    ax.plot([6.0, 6.0], [5.8, 6.5], color="#aaaacc", lw=1)
    ax.plot([9.6, 6.0], [5.8, 6.5], color="#aaaacc", lw=1)

    link(2.6, 5.4, 2.6, 5.8)
    link(6.1, 5.4, 6.1, 5.8)
    link(9.6, 5.4, 9.6, 5.8)

    # 設備層
    mau_n = equipment.get("mau_count", 0)
    rcu_n = equipment.get("rcu_count", 0) + equipment.get("ahu_count", 0)
    fcu_n = equipment.get("fcu_count", 0)

    if mau_n:
        box(0.5, 2.8, 2.0, 0.9, f"MAU × {mau_n}台\n外氣處理機", "#e63946")
        link(2.5, 4.5, 2.0, 3.7, "", "#aaaacc")
    if rcu_n:
        box(4.0, 2.8, 2.0, 0.9, f"RCU/AHU × {rcu_n}台\n循環空調", "#06d6a0")
        link(6.1, 4.5, 5.0, 3.7, "", "#aaaacc")
    if fcu_n:
        box(6.5, 2.8, 2.0, 0.9, f"FCU × {fcu_n}台\n風機盤管", "#9b59b6")
        link(6.5, 4.5, 7.5, 3.7, "", "#aaaacc")

    box(8.0, 2.8, 2.0, 0.9, "Chiller × 1台\n冰水主機", "#264653")
    link(9.6, 4.5, 9.0, 3.7, "", "#aaaacc")

    # 感測器層
    ax.text(1.5, 2.5, "感測器", color="#a8dadc", fontsize=7, ha="center")
    sensor_items = ["溫/濕度", "壓差開關", "流量計"]
    for j, s in enumerate(sensor_items):
        x = 0.5 + j * 1.2
        box(x, 1.5, 1.0, 0.7, s, "#37474f", fs=6)
        ax.plot([x + 0.5, 1.5], [2.2, 2.5], color="#aaaacc", lw=0.8)

    # IO 統計
    io_txt = (f"I/O 點數統計：AI={io_sum.get('AI',0)}  DI={io_sum.get('DI',0)}"
              f"  AO={io_sum.get('AO',0)}  DO={io_sum.get('DO',0)}"
              f"  合計={io_sum.get('total',0)}點")
    ax.text(6.0, 0.5, io_txt, ha="center", color="#e9c46a", fontsize=8)

    ax.set_title(f"自動控制架構圖｜{system_type}", color="white",
                 fontsize=10, pad=8)


# ── DXF 匯出 ────────────────────────────────────────────────────

def export_ctrl_dxf(system_type: str, io_sum: dict, save_path: str):
    from dxf_writer import create_doc, add_rect, add_text, add_pipe

    doc, msp = create_doc(f"自動控制架構圖 — {system_type}")

    # BMS 主機
    add_rect(msp, 4000, 7000, 3000, 800, layer="AC-CTRL")
    add_text(msp, "BMS 監控主機", 4100, 7400, height=200, layer="AC-TEXT")

    # Modbus 匯流排
    add_pipe(msp, [(0, 6000), (12000, 6000)], layer="AC-CTRL")
    add_text(msp, "Modbus/BACnet 通訊匯流排", 5500, 6100, height=150, layer="AC-TEXT")

    # DDC 控制器
    controllers = ["DDC-MAU/AHU", "DDC-RCU/FCU", "DDC-Chiller"]
    for j, c in enumerate(controllers):
        x = j * 4000
        add_rect(msp, x + 200, 4500, 2000, 800, layer="AC-CTRL")
        add_text(msp, c, x + 300, 4900, height=150, layer="AC-TEXT")
        add_pipe(msp, [(x + 1200, 5300), (x + 1200, 6000)], layer="AC-CTRL")

    # IO 統計
    add_text(msp,
             f"I/O: AI={io_sum.get('AI',0)} DI={io_sum.get('DI',0)} "
             f"AO={io_sum.get('AO',0)} DO={io_sum.get('DO',0)} "
             f"合計={io_sum.get('total',0)}點",
             0, 3500, height=180, layer="AC-TEXT")

    doc.saveas(save_path)
