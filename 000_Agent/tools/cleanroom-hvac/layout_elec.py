# 空調電力單線圖模組 — 升級 electrical.py，加入 SLD 繪圖 + DXF 匯出
from electrical import calc_circuit, calc_panel_nfb, build_hvac_circuits


def draw_sld(ax, circuits: list, panel: dict):
    """
    空調電力單線圖（SLD）— matplotlib 版。
    格式參考：ACP-401 實際竣工圖（電力系統.pdf）
    上方：匯流排 + 各分路 NFB/MS/設備；下方：電路明細表
    """
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines

    ax.set_facecolor("#12121f")
    ax.axis("off")

    if not circuits:
        ax.text(0.5, 0.5, "請先輸入設備資料", ha="center", va="center",
                color="white", fontsize=12, transform=ax.transAxes)
        return

    n = len(circuits)
    col_w = max(1.5, 14.0 / max(n, 1))
    total_w = n * col_w
    ax.set_xlim(-1.0, total_w + 0.5)
    ax.set_ylim(-3.5, 9.5)   # 下方留 3.5 單位放電路表格

    # ── 電源標題 ────────────────────────────────────────────────
    at  = panel.get("panel_nfb_at", "?")
    af  = panel.get("panel_nfb_af", "?")
    kva = panel.get("total_kva", 0)
    ax.text(total_w / 2, 9.2,
            f"Power From MACP  3Ø-4W-380/220V-60Hz",
            ha="center", color="#aaaacc", fontsize=7)
    ax.text(total_w / 2, 8.8,
            f"空調配電盤 (ACP)  |  總NFB: 3-{at}/{af}  |  計算電流: {panel.get('total_required_a',0):.1f}A  |  {kva} kVA",
            ha="center", color="#f4c430", fontsize=8, fontweight="bold")
    ax.text(-0.9, 8.3, panel.get("calc_note", ""), color="#aaaacc", fontsize=6.5, va="top")

    # ── 主匯流排 ────────────────────────────────────────────────
    bus_y = 8.0
    ax.plot([-0.5, total_w], [bus_y, bus_y], color="#f4c430", lw=4)

    for i, c in enumerate(circuits):
        x = i * col_w + col_w / 2

        # 垂直降落線（匯流排→NFB）
        ax.plot([x, x], [bus_y, 6.8], color="#aaaacc", lw=1.5)

        # NFB 符號（圓圈）+ 標示 "3-AT/AF"
        nfb_label = c.get("nfb_label", f"3-{c['nfb_at']}/{c.get('nfb_af','?')}")
        circle = mpatches.Circle((x, 6.55), 0.22, facecolor="#264653",
                                  edgecolor="#4ecdc4", linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x + 0.28, 6.55, nfb_label, va="center", color="#4ecdc4", fontsize=5.5)

        # NFB → MS 連線
        ax.plot([x, x], [6.33, 5.8], color="#aaaacc", lw=1.2)

        # MS（電磁接觸器）方塊
        ms_rect = mpatches.FancyBboxPatch(
            (x - 0.28, 5.4), 0.56, 0.4,
            boxstyle="round,pad=0.04",
            facecolor="#1d3461", edgecolor="#7ecffa", linewidth=1.0,
        )
        ax.add_patch(ms_rect)
        ax.text(x, 5.6, "MS", ha="center", va="center", color="#7ecffa", fontsize=5.5)

        # 若有 VFD（Y-△ 啟動 → 用 INV 符號）
        start = c.get("start_method", "MS")
        if start == "Y-△":
            inv_rect = mpatches.FancyBboxPatch(
                (x - 0.28, 4.85), 0.56, 0.35,
                boxstyle="round,pad=0.04",
                facecolor="#264653", edgecolor="#f4a261", linewidth=1.0,
            )
            ax.add_patch(inv_rect)
            ax.text(x, 5.02, "Y-△", ha="center", va="center",
                    color="#f4a261", fontsize=5)
            eq_top = 4.85
        else:
            eq_top = 5.4

        # MS → 設備連線
        ax.plot([x, x], [eq_top, 4.2], color="#aaaacc", lw=1.2)

        # 線材規格標注（靠右）
        wire_spec = c.get("wire_spec", f"{c['wire_mm2']}mm²")
        ax.text(x + 0.08, 4.6, wire_spec, va="center",
                color="#e9c46a", fontsize=4.5, style="italic")

        # 設備方塊
        if "MAU" in c["name"]:   clr = "#2a9d8f"
        elif "FFU" in c["name"]: clr = "#e63946"
        elif "泵" in c["name"]:  clr = "#457b9d"
        elif "AHU" in c["name"]: clr = "#9b5de5"
        else:                     clr = "#06d6a0"

        eq_rect = mpatches.FancyBboxPatch(
            (x - 0.42, 3.2), 0.84, 1.0,
            boxstyle="round,pad=0.05",
            facecolor=clr, edgecolor="white", linewidth=1.0, alpha=0.9,
        )
        ax.add_patch(eq_rect)
        label = c["name"].replace(" ", "\n")
        ax.text(x, 3.7, f"{label}", ha="center", va="center",
                color="white", fontsize=5.0, fontweight="bold")

        # 接地線
        ax.plot([x, x], [3.2, 2.6], color="#06d6a0", lw=0.8, ls="--")
        gnd_bar_w = 0.18
        for dx in [-gnd_bar_w, 0, gnd_bar_w]:
            ax.plot([x + dx - 0.05, x + dx + 0.05], [2.55, 2.55],
                    color="#06d6a0", lw=1.0 - abs(dx) * 2)
        ax.text(x, 2.4, f"E={c['gnd_mm2']}mm²",
                ha="center", va="top", color="#06d6a0", fontsize=4.5)

    # ── 下方電路明細表（對應 ACP-401 SLD 格式） ─────────────────
    table_y = -0.3
    col_labels = ["CIRCUIT\nNO.", "DESCRIPTION", "LOAD\n(kW)", "CURRENT\n(A)",
                  "VOLTAGE\n(V)", "PHASE", "WIRE SPEC"]
    col_widths = [0.6, 2.0, 0.8, 0.8, 0.8, 0.7, 2.0]
    col_x_starts = [-1.0]
    for w in col_widths[:-1]:
        col_x_starts.append(col_x_starts[-1] + w)

    # 表頭
    for j, (lbl, cx) in enumerate(zip(col_labels, col_x_starts)):
        ax.text(cx + col_widths[j] / 2, table_y, lbl,
                ha="center", va="top", color="#f4c430", fontsize=5.5,
                fontweight="bold")

    row_h = 0.55
    # 表格外框
    table_total_w = sum(col_widths)
    ax.add_patch(mpatches.FancyBboxPatch(
        (-1.0, table_y - (len(circuits) + 0.5) * row_h),
        table_total_w, (len(circuits) + 0.5) * row_h + 0.1,
        boxstyle="square,pad=0",
        facecolor="#1a1a2e", edgecolor="#555", linewidth=0.8, zorder=0,
    ))

    for i, c in enumerate(circuits):
        ry = table_y - (i + 1.0) * row_h
        row_bg = "#23233a" if i % 2 == 0 else "#1a1a2e"
        ax.add_patch(mpatches.Rectangle(
            (-1.0, ry), table_total_w, row_h,
            facecolor=row_bg, edgecolor="none", zorder=1,
        ))
        row_vals = [
            str(i + 1),
            c["name"],
            str(c["kw"]),
            str(round(c["flc_a"], 1)),
            str(c["voltage"]),
            c["phase"],
            c.get("wire_spec", f"{c['wire_mm2']}mm²"),
        ]
        for j, (val, cx) in enumerate(zip(row_vals, col_x_starts)):
            ax.text(cx + col_widths[j] / 2, ry + row_h / 2, val,
                    ha="center", va="center", color="white", fontsize=5.2, zorder=2)

    # 表格分隔線（列）
    for i in range(len(circuits) + 1):
        ry = table_y - i * row_h
        ax.plot([-1.0, -1.0 + table_total_w], [ry, ry],
                color="#444", lw=0.5, zorder=3)

    ax.set_title("空調電力單線圖（SLD）", color="white", fontsize=10, pad=8)


# ── DXF 匯出：SLD ────────────────────────────────────────────────

def export_sld_dxf(circuits: list, panel: dict, save_path: str):
    from dxf_writer import create_doc, add_rect, add_text, add_pipe

    doc, msp = create_doc("空調電力單線圖")

    # 匯流排
    add_pipe(msp, [(-500, 8000), (len(circuits) * 2000 + 500, 8000)],
             layer="AC-ELEC")
    add_text(msp, f"空調配電盤 ACP | 總NFB {panel.get('panel_nfb_at','?')}A",
             0, 8300, height=200, layer="AC-TEXT")

    for i, c in enumerate(circuits):
        x = i * 2000

        # 垂直主線
        add_pipe(msp, [(x, 8000), (x, 2000)], layer="AC-ELEC")

        # NFB 方塊
        add_rect(msp, x - 200, 6500, 400, 600, layer="AC-ELEC")
        add_text(msp, f"NFB {c['nfb_at']}A/{c['nfb_af']}", x - 180, 6700,
                 height=150, layer="AC-TEXT")

        # 線徑
        add_text(msp, f"{c['wire_mm2']}mm² EMT φ{c['emt_phi']}",
                 x + 80, 5000, height=120, layer="AC-TEXT")

        # 設備方塊
        add_rect(msp, x - 300, 1500, 600, 800, layer="AC-ELEC")
        add_text(msp, c["name"], x - 280, 1900, height=130, layer="AC-TEXT")
        add_text(msp, f"{c['kw']}kW {c['voltage']}V",
                 x - 280, 1650, height=120, layer="AC-TEXT")
        add_text(msp, f"{c['start_method']} E={c['gnd_mm2']}mm²",
                 x - 280, 1450, height=100, layer="AC-TEXT")

    doc.saveas(save_path)
