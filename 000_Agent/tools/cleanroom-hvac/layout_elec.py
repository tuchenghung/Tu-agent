# 空調電力單線圖模組 — 升級 electrical.py，加入 SLD 繪圖 + DXF 匯出
from electrical import calc_circuit, calc_panel_nfb, build_hvac_circuits


def draw_sld(ax, circuits: list, panel: dict):
    """
    空調電力單線圖（SLD）— matplotlib 版。
    由上到下：MDP → 子配電盤 → 各分路 → 設備
    """
    import matplotlib.patches as mpatches
    ax.set_facecolor("#12121f")
    ax.axis("off")

    if not circuits:
        ax.text(0.5, 0.5, "請先輸入設備資料", ha="center", va="center",
                color="white", fontsize=12, transform=ax.transAxes)
        return

    n = len(circuits)
    col_w = max(1.2, 10.0 / (n + 1))
    ax.set_xlim(-0.5, n * col_w + 0.5)
    ax.set_ylim(-1, 8)

    # MDP 匯流排
    ax.plot([-0.5, n * col_w], [7, 7], color="#f4c430", lw=3)
    ax.text((n * col_w) / 2, 7.25, "空調配電盤 (ACP)", ha="center",
            color="#f4c430", fontsize=9, fontweight="bold")

    # 總 NFB
    nfb_label = f"總NFB\n{panel.get('panel_nfb_at','?')}A/{panel.get('panel_nfb_af','?')}"
    ax.text(-0.5, 7, nfb_label, ha="right", va="center",
            color="white", fontsize=7)

    for i, c in enumerate(circuits):
        x = i * col_w + col_w / 2

        # 垂直匯流排線
        ax.plot([x, x], [7, 5.5], color="#aaaacc", lw=1.5)

        # NFB 方塊
        rect = mpatches.FancyBboxPatch(
            (x - 0.35, 5.0), 0.7, 0.8,
            boxstyle="round,pad=0.05",
            facecolor="#264653", edgecolor="#4ecdc4", linewidth=1.2,
        )
        ax.add_patch(rect)
        ax.text(x, 5.4, f"NFB\n{c['nfb_at']}A", ha="center", va="center",
                color="white", fontsize=6)

        # 垂直線到設備
        ax.plot([x, x], [5.0, 3.5], color="#aaaacc", lw=1.2)

        # 線徑標注
        ax.text(x + 0.12, 4.25, f"{c['wire_mm2']}mm²\nEMT φ{c['emt_phi']}",
                ha="left", va="center", color="#e9c46a", fontsize=5.5)

        # 設備方塊
        color = "#2a9d8f" if "MAU" in c["name"] else \
                "#e63946" if "FFU" in c["name"] else \
                "#457b9d" if "泵" in c["name"] else "#06d6a0"
        eq_rect = mpatches.FancyBboxPatch(
            (x - 0.45, 2.5), 0.9, 1.0,
            boxstyle="round,pad=0.05",
            facecolor=color, edgecolor="white", linewidth=1.0, alpha=0.9,
        )
        ax.add_patch(eq_rect)
        label = c["name"].replace(" ", "\n")
        ax.text(x, 3.0, f"{label}\n{c['kw']}kW",
                ha="center", va="center", color="white", fontsize=5.5)

        # 電壓/啟動方式
        ax.text(x, 2.3, f"{c['voltage']}V {c['phase']}\n{c['start_method']}",
                ha="center", va="top", color="#a8dadc", fontsize=5.5)

        # 接地線
        ax.plot([x, x], [2.5, 1.5], color="#06d6a0", lw=0.8, ls="--")
        ax.plot([x - 0.15, x + 0.15], [1.5, 1.5], color="#06d6a0", lw=0.8)
        ax.text(x, 1.3, f"E={c['gnd_mm2']}mm²",
                ha="center", va="top", color="#06d6a0", fontsize=5)

    # 合計
    kva = panel.get("total_kva", 0)
    at = panel.get("panel_nfb_at", 0)
    ax.text((n * col_w) / 2, 0.5,
            f"設備總 kVA：{kva} kVA | 總 NFB：{at}A | "
            f"計算電流：{panel.get('total_required_a', 0):.1f}A",
            ha="center", color="#e9c46a", fontsize=8)

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
