# 管路設計模組 — 冰水/冷卻/排水管系統圖（matplotlib + DXF）
from reference_data import CHW_PIPE


def build_pipe_schedule(rt: dict, floors: int = 1) -> dict:
    """
    計算各管路規格。
    回傳: {chw, cw, drain, summary}
    """
    total_rt = rt["total_rt"]

    # 冰水管 (CHW)
    chw_size = _select_chw(total_rt)
    chw_flow_gpm = round(total_rt * 2.4, 1)

    # 冷卻水管 (CW)
    cw_rt = total_rt  # 同 RT 但流量 3 GPM/RT
    cw_size = _select_cw(cw_rt)
    cw_flow_gpm = round(total_rt * 3.0, 1)

    # 排水管（冷凝水）— 每 RT 約 0.5 GPH
    drain_size = _select_drain(total_rt)

    return {
        "chw": {"size": chw_size, "flow_gpm": chw_flow_gpm,
                "flow_cmh": round(chw_flow_gpm * 0.2271, 1)},
        "cw":  {"size": cw_size,  "flow_gpm": cw_flow_gpm,
                "flow_cmh": round(cw_flow_gpm * 0.2271, 1)},
        "drain": {"size": drain_size},
        "total_rt": total_rt,
        "floors": floors,
    }


def _select_chw(rt: float) -> str:
    for max_rt, size in CHW_PIPE:
        if rt <= max_rt:
            return size
    return '> 8"'


# 冷卻水管（3 GPM/RT，比冰水管大一級）
_CW_PIPE = [
    (5, '1-1/4"'), (8, '1-1/2"'), (15, '2"'), (28, '2-1/2"'),
    (45, '3"'), (90, '4"'), (165, '5"'), (270, '6"'), (420, '8"'),
]


def _select_cw(rt: float) -> str:
    for max_rt, size in _CW_PIPE:
        if rt <= max_rt:
            return size
    return '> 8"'


def _select_drain(rt: float) -> str:
    if rt <= 10:
        return '3/4"'
    if rt <= 30:
        return '1"'
    if rt <= 80:
        return '1-1/4"'
    return '1-1/2"'


# ── matplotlib 管路系統圖 ─────────────────────────────────────────

def draw_pipe_schematic(ax, pipe_data: dict, system_type: str = "CH+MAU+RCU"):
    import matplotlib.patches as mpatches

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.set_facecolor("#12121f")
    ax.axis("off")

    def box(x, y, w, h, label, color="#2a9d8f", fs=8):
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor="white", linewidth=1.0, alpha=0.9,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                color="white", fontsize=fs, fontweight="bold")

    def pipe(x1, y1, x2, y2, label="", color="#4ecdc4", lw=2.5, ls="-"):
        ax.annotate("", (x2, y2), (x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                   connectionstyle="arc3,rad=0"))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 0.18, label, ha="center", va="bottom",
                    color=color, fontsize=7)

    chw = pipe_data["chw"]
    cw = pipe_data["cw"]
    drain = pipe_data["drain"]
    rt = pipe_data["total_rt"]

    # Chiller
    box(0.5, 4.5, 1.8, 1.2, f"Chiller\n{rt:.0f} RT", "#1d3461")
    # Pump
    box(3.0, 5.0, 1.2, 0.8, "冰水泵\nCHWP", "#264653")
    # AHU/RCU
    box(5.5, 4.5, 1.5, 1.2, "AHU/RCU\n空調箱", "#2a9d8f")
    # Cooling tower
    box(0.5, 1.5, 1.8, 1.2, "冷卻水塔\nCooling Tower", "#e76f51")
    # Condensing pump
    box(3.0, 1.8, 1.2, 0.8, "冷卻泵\nCWP", "#a8dadc")
    # MAU
    box(5.5, 2.0, 1.5, 1.0, "MAU\n外氣機", "#457b9d")
    # Drain
    box(8.5, 3.5, 1.5, 0.8, "排水管", "#6c757d")

    # CHW pipes
    pipe(2.3, 5.1, 3.0, 5.1, f"CHW去管\n{chw['size']} {chw['flow_gpm']} GPM",
         color="#4ecdc4")
    pipe(4.2, 5.2, 5.5, 5.1, f"{chw['size']}", color="#4ecdc4")
    pipe(5.5, 4.6, 4.2, 4.6, "回水", color="#74b9ff")
    pipe(4.2, 4.6, 2.3, 4.8, f"CHW回管\n{chw['size']}", color="#74b9ff")

    # CW pipes
    pipe(2.3, 2.1, 3.0, 2.1, f"CW去\n{cw['size']} {cw['flow_gpm']} GPM",
         color="#e9c46a")
    pipe(0.5 + 1.8, 1.9, 0.5, 1.9, f"{cw['size']}", color="#fd9843")

    # MAU → 排水
    pipe(7.0, 2.5, 8.5, 3.8, f"冷凝水\n{drain['size']}", color="#9b59b6")

    # 說明
    legend = [
        mpatches.Patch(color="#4ecdc4", label=f"冰水去管 CHW {chw['size']}"),
        mpatches.Patch(color="#74b9ff", label=f"冰水回管 CHW {chw['size']}"),
        mpatches.Patch(color="#e9c46a", label=f"冷卻水管 CW {cw['size']}"),
        mpatches.Patch(color="#9b59b6", label=f"排水管 {drain['size']}"),
    ]
    ax.legend(handles=legend, loc="lower right",
              facecolor="#2d2d44", edgecolor="#666", labelcolor="white", fontsize=7)

    ax.set_title(
        f"冰水/冷卻水管路系統圖｜{rt:.0f} RT\n"
        f"CHW {chw['size']} {chw['flow_gpm']}GPM｜"
        f"CW {cw['size']} {cw['flow_gpm']}GPM｜"
        f"排水 {drain['size']}",
        color="white", fontsize=9, pad=6,
    )


# ── DXF 匯出 ────────────────────────────────────────────────────

def export_pipe_dxf(pipe_data: dict, fp: dict, save_path: str):
    from dxf_writer import create_doc, add_walls, add_pipe, add_rect, add_text

    doc, msp = create_doc("冰水管路配置圖")
    add_walls(msp, fp.get("walls", []))

    bbox = fp.get("bbox", (0, 0, 10000, 10000))
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) / 2

    chw = pipe_data["chw"]
    cw = pipe_data["cw"]

    # CHW 主幹（縱向，靠近主幹風管旁）
    offset = 300
    add_pipe(msp, [(cx + offset, y0), (cx + offset, y1)], layer="AC-PIPE-CHW")
    add_pipe(msp, [(cx + offset * 2, y0), (cx + offset * 2, y1)], layer="AC-PIPE-CHW")
    add_text(msp, f"CHW去 {chw['size']} {chw['flow_gpm']}GPM",
             cx + offset + 50, (y0 + y1) / 2, height=120, layer="AC-TEXT")

    # CW 主幹
    add_pipe(msp, [(cx - offset, y0), (cx - offset, y1)], layer="AC-PIPE-CW")
    add_text(msp, f"CW {cw['size']} {cw['flow_gpm']}GPM",
             cx - offset + 50, (y0 + y1) / 2, height=120, layer="AC-TEXT")

    doc.saveas(save_path)
