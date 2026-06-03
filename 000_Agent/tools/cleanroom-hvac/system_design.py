# 空調系統選型模組
# 根據潔淨等級、面積、樓層、用途給出建議系統型式

from reference_data import ACH_TABLE

SYSTEM_OPTIONS = [
    "CH+MAU+FFU",
    "CH+MAU+RCU",
    "CH+MAU+D/C",
    "CH+MAU+AHU",
    "CH+FCU+AHU",
    "VRF+AHU",
    "Split+FCU",
]

# 系統型式說明
SYSTEM_DESC = {
    "CH+MAU+FFU":   "冰水機組 + 外氣處理機 + 風機過濾單元\n適用：ISO 5~6 高潔淨度，FFU 提供均勻層流",
    "CH+MAU+RCU":   "冰水機組 + 外氣處理機 + 循環冷卻盤管\n適用：ISO 6~7，RCU 局部循環，MAU 補充新風",
    "CH+MAU+D/C":   "冰水機組 + 外氣處理機 + 乾盤管\n適用：ISO 7~8，乾盤管只除熱不除濕，MAU 除濕",
    "CH+MAU+AHU":   "冰水機組 + 外氣處理機 + 空調箱\n適用：ISO 7~8 或高換氣率，AHU 全頂送",
    "CH+FCU+AHU":   "冰水機組 + 風機盤管 + 空調箱\n適用：一般辦公、醫院、廠辦",
    "VRF+AHU":      "變頻多聯機 + 全熱交換外氣機\n適用：中小型辦公，節能且彈性高",
    "Split+FCU":    "分離式主機 + 風機盤管\n適用：小坪數、低預算場所",
}

# 規則表：(min_area_m2, max_area_m2, cleanroom_classes, system)
_RULES = [
    # 高潔淨度 → FFU
    (0, 99999, {"Class 100 (ISO 5)", "Class 1,000 (ISO 6)"}, "CH+MAU+FFU"),
    # ISO 7 → RCU（中面積）
    (0, 5000, {"Class 10,000 (ISO 7)"}, "CH+MAU+RCU"),
    (5000, 99999, {"Class 10,000 (ISO 7)"}, "CH+MAU+D/C"),
    # ISO 8 → D/C（節省成本）
    (0, 99999, {"Class 100,000 (ISO 8)"}, "CH+MAU+D/C"),
    # 一般空調 大面積 → FCU+AHU
    (1000, 99999, {"一般空調 (ISO 9)"}, "CH+FCU+AHU"),
    # 一般空調 中小 → VRF
    (200, 999, {"一般空調 (ISO 9)"}, "VRF+AHU"),
    # 小型 → Split
    (0, 199, {"一般空調 (ISO 9)"}, "Split+FCU"),
]


def recommend_system(rooms: list, building: dict) -> dict:
    """
    輸入房間清單與建築資訊，回傳建議系統清單。
    rooms: [{name, area_m2, class, is_cleanroom}, ...]
    building: {floors, total_area_m2}
    回傳: [{zone, class, area_m2, recommended, reason, alternatives}, ...]
    """
    total = building.get("total_area_m2", sum(r["area_m2"] for r in rooms))
    results = []

    # 依潔淨等級分組
    groups: dict[str, list] = {}
    for r in rooms:
        c = r.get("class", "一般空調 (ISO 9)")
        groups.setdefault(c, []).append(r)

    for cls, rlist in groups.items():
        area = sum(r["area_m2"] for r in rlist)
        names = [r["name"] for r in rlist]
        rec = _apply_rules(area, cls)
        alts = [s for s in SYSTEM_OPTIONS if s != rec][:3]
        reason = _build_reason(area, cls, rec)
        results.append({
            "zone": "、".join(names) if len(names) <= 4 else f"{names[0]}等{len(names)}間",
            "class": cls,
            "area_m2": round(area, 1),
            "recommended": rec,
            "reason": reason,
            "alternatives": alts,
        })

    return results


def _apply_rules(area_m2: float, cls: str) -> str:
    for amin, amax, classes, system in _RULES:
        if cls in classes and amin <= area_m2 < amax:
            return system
    return "CH+FCU+AHU"


def _build_reason(area_m2: float, cls: str, system: str) -> str:
    lines = [SYSTEM_DESC.get(system, "")]
    ping = area_m2 / 3.3058
    lines.append(f"空間面積：{area_m2:.0f} m²（約 {ping:.0f} 坪）")
    ach = ACH_TABLE.get(cls, {})
    if ach:
        lines.append(f"ACH 需求：{ach['ach_min']}~{ach['ach_max']} 次/hr")
    return "\n".join(lines)


# ── 系統架構圖（matplotlib schematic）────────────────────────────

def draw_system_diagram(ax, system_type: str, n_rooms: int = 3):
    """繪製空調系統架構示意圖（箭頭 + 方塊）。"""
    import matplotlib.patches as mpatches
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_facecolor("#12121f")
    ax.axis("off")

    def box(x, y, w, h, label, color="#2a9d8f", fontsize=8):
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor="white", linewidth=1.2, alpha=0.9,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label,
                ha="center", va="center", color="white",
                fontsize=fontsize, fontweight="bold")

    def arrow(x1, y1, x2, y2, label=""):
        ax.annotate("", (x2, y2), (x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#aaaacc", lw=1.5))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 0.15, label, ha="center", va="bottom",
                    color="#e9c46a", fontsize=7)

    parts = system_type.split("+")

    if "FFU" in system_type:
        box(0.5, 4.0, 1.5, 1.0, "冰水主機\nChiller", "#1d3461")
        box(0.5, 2.0, 1.5, 1.0, "外氣\nMAU", "#2a9d8f")
        box(3.5, 3.0, 1.5, 1.0, "FFU\n風機過濾", "#e63946")
        box(6.5, 3.0, 2.5, 1.0, f"無塵室 × {n_rooms}", "#457b9d")
        arrow(2.0, 4.5, 3.5, 3.5, "冰水")
        arrow(2.0, 2.5, 3.5, 3.5, "新風")
        arrow(5.0, 3.5, 6.5, 3.5, "潔淨氣流")

    elif "RCU" in system_type:
        box(0.5, 4.0, 1.5, 1.0, "冰水主機\nChiller", "#1d3461")
        box(0.5, 2.0, 1.5, 1.0, "外氣\nMAU", "#2a9d8f")
        box(3.5, 4.0, 1.5, 1.0, "循環\nRCU", "#e9c46a")
        box(6.5, 3.0, 2.5, 1.0, f"無塵室 × {n_rooms}", "#457b9d")
        arrow(2.0, 4.5, 3.5, 4.5, "冰水")
        arrow(2.0, 2.5, 6.5, 3.0, "新風正壓")
        arrow(5.0, 4.5, 6.5, 4.0, "循環冷風")

    elif "D/C" in system_type:
        box(0.5, 4.0, 1.5, 1.0, "冰水主機\nChiller", "#1d3461")
        box(0.5, 2.0, 1.5, 1.0, "外氣\nMAU", "#2a9d8f")
        box(3.5, 4.0, 1.5, 1.0, "乾盤管\nD/C", "#f4a261")
        box(6.5, 3.0, 2.5, 1.0, f"無塵室 × {n_rooms}", "#457b9d")
        arrow(2.0, 4.5, 3.5, 4.5, "冰水(高溫)")
        arrow(2.0, 2.5, 6.5, 3.0, "除濕新風")
        arrow(5.0, 4.5, 6.5, 4.0, "顯熱冷卻")

    elif "FCU" in system_type:
        box(0.5, 4.0, 1.5, 1.0, "冰水主機\nChiller", "#1d3461")
        box(0.5, 2.0, 1.5, 1.0, "全熱\nAHU", "#2a9d8f")
        box(3.5, 4.0, 1.5, 1.0, "FCU\n風機盤管", "#06d6a0")
        box(6.5, 3.0, 2.5, 1.0, f"各空間 × {n_rooms}", "#457b9d")
        arrow(2.0, 4.5, 3.5, 4.5, "冰水")
        arrow(2.0, 2.5, 6.5, 3.0, "新風")
        arrow(5.0, 4.5, 6.5, 4.0, "冷氣")

    elif "VRF" in system_type:
        box(0.5, 3.5, 1.5, 1.2, "室外機\nVRF", "#1d3461")
        box(0.5, 1.5, 1.5, 1.0, "全熱\nAHU", "#2a9d8f")
        box(3.5, 3.5, 1.5, 1.0, "室內機\n× n", "#9b5de5")
        box(6.5, 3.0, 2.5, 1.0, f"各空間 × {n_rooms}", "#457b9d")
        arrow(2.0, 4.1, 3.5, 4.0, "冷媒")
        arrow(2.0, 2.0, 6.5, 3.0, "新風")
        arrow(5.0, 4.0, 6.5, 3.8, "冷氣")

    else:
        box(0.5, 4.0, 1.5, 1.0, "Split\n主機", "#1d3461")
        box(3.5, 4.0, 1.5, 1.0, "FCU", "#06d6a0")
        box(6.5, 3.5, 2.5, 1.0, f"空間 × {n_rooms}", "#457b9d")
        arrow(2.0, 4.5, 3.5, 4.5, "冷媒")
        arrow(5.0, 4.5, 6.5, 4.0, "冷氣")

    ax.set_title(f"系統架構示意圖｜{system_type}", color="white",
                 fontsize=10, pad=8)


# ── DXF 匯出：系統架構圖 ─────────────────────────────────────────

def export_system_dxf(system_type: str, save_path: str):
    from dxf_writer import create_doc, add_rect, add_text, add_pipe
    doc, msp = create_doc(f"空調系統架構圖 — {system_type}")

    # 簡易方塊圖（座標單位 mm）
    def box_dxf(x, y, w, h, label, layer="AC-EQUIP"):
        add_rect(msp, x, y, w, h, layer=layer)
        add_text(msp, label, x + 50, y + h / 2, height=150, layer="AC-TEXT")

    box_dxf(0, 3000, 1000, 600, "冰水主機 Chiller")
    box_dxf(2000, 3000, 1000, 600, "MAU 外氣機")
    box_dxf(4000, 3000, 1000, 600, system_type.split("+")[-1])
    box_dxf(6500, 2500, 1500, 1600, "各空調區")

    # 連接線
    add_pipe(msp, [(1000, 3300), (2000, 3300)], layer="AC-PIPE-CHW")
    add_pipe(msp, [(2000, 3300), (4000, 3300)], layer="AC-DUCT-SUP")
    add_pipe(msp, [(5000, 3300), (6500, 3300)], layer="AC-DUCT-SUP")

    doc.saveas(save_path)
