# 風管配置模組 — 主幹+支管路徑規劃、matplotlib 疊圖、DXF 匯出
import math
from reference_data import ACH_TABLE


def plan_duct_routes(rooms: list, airflow_data: dict, bbox: tuple) -> list:
    """
    簡易風管路徑規劃：
    1. 主幹沿 bbox 中線走
    2. 各房間拉支管到主幹最近點
    3. 依風量決定主幹/支管尺寸

    回傳 [{type, pts, width_mm, label}, ...]
    """
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) / 2   # 主幹 X 軸中線（縱向主幹）
    cy = (y0 + y1) / 2   # 橫向主幹 Y 位置

    routes = []
    total_cmh = airflow_data.get("circulation_cmh", 0) or airflow_data.get("mau_cmh", 1)

    # 主幹（縱向）
    main_w = _duct_width(total_cmh)
    routes.append({
        "type": "main",
        "pts": [(cx, y0 + (y1 - y0) * 0.1), (cx, y0 + (y1 - y0) * 0.9)],
        "width_mm": main_w,
        "label": f"主幹 {_duct_label(total_cmh)}",
    })

    # 各房間支管
    for room in rooms:
        if room.get("area_m2", 0) < 1:
            continue
        n_rooms = max(len(rooms), 1)
        room_cmh = total_cmh / n_rooms
        branch_w = _duct_width(room_cmh)

        # 支管端點（房間中心 → 主幹）
        rx, ry = room["x"], room["y"]
        jx = cx  # 接主幹的 X
        jy = ry  # 接主幹的 Y（同高度走橫向支管）

        routes.append({
            "type": "branch",
            "pts": [(jx, jy), (rx, ry)],
            "width_mm": branch_w,
            "label": f"{room['name']} {_duct_label(room_cmh)}",
            "room": room["name"],
        })

        # 出風口（在房間位置）
        routes.append({
            "type": "diffuser",
            "pts": [(rx, ry)],
            "width_mm": 600,
            "label": room["name"],
        })

    return routes


def _duct_width(cmh: float) -> float:
    """依風量估算風管寬度 mm（高度固定 300mm）"""
    if cmh <= 0:
        return 300
    # v = 5~8 m/s → 寬度 mm = CMH ÷ (v × 3600 × 0.3m高) × 1000
    v = 6.0
    w = (cmh / 3600 / v / 0.3) * 1000  # mm
    return max(300, min(round(w / 50) * 50, 2000))


def _duct_label(cmh: float) -> str:
    w = _duct_width(cmh)
    return f"{w:.0f}×300mm/{cmh:.0f}CMH"


# ── matplotlib 圖 ────────────────────────────────────────────────

def draw_duct_layout(ax, fp: dict, routes: list):
    from floor_plan import draw_floorplan
    import matplotlib.patches as mpatches

    draw_floorplan(ax, fp)

    for r in routes:
        if r["type"] == "main":
            xs = [p[0] for p in r["pts"]]
            ys = [p[1] for p in r["pts"]]
            ax.plot(xs, ys, color="#3ae374", lw=4, alpha=0.9, solid_capstyle="round")
            ax.text(xs[0], ys[0], r["label"], color="#3ae374", fontsize=7,
                    ha="center", va="top")

        elif r["type"] == "branch":
            xs = [p[0] for p in r["pts"]]
            ys = [p[1] for p in r["pts"]]
            ax.plot(xs, ys, color="#a8e6cf", lw=2, alpha=0.8)

        elif r["type"] == "diffuser":
            px, py = r["pts"][0]
            size = 400  # mm
            rect = mpatches.Rectangle(
                (px - size / 2, py - size / 2), size, size,
                linewidth=1.2, edgecolor="#e9c46a", facecolor="none",
            )
            ax.add_patch(rect)
            ax.plot([px - size / 2, px + size / 2],
                    [py - size / 2, py + size / 2], color="#e9c46a", lw=0.8)
            ax.plot([px + size / 2, px - size / 2],
                    [py - size / 2, py + size / 2], color="#e9c46a", lw=0.8)

    legend = [
        mpatches.Patch(color="#3ae374", label="主幹送風管"),
        mpatches.Patch(color="#a8e6cf", label="支管"),
        mpatches.Patch(facecolor="none", edgecolor="#e9c46a", label="出風口"),
    ]
    ax.legend(handles=legend, loc="upper right",
              facecolor="#2d2d44", edgecolor="#666", labelcolor="white",
              fontsize=7)
    ax.set_title("風管配置圖（示意）", color="white", fontsize=10)


# ── DXF 匯出 ────────────────────────────────────────────────────

def export_duct_dxf(fp: dict, routes: list, save_path: str):
    from dxf_writer import create_doc, add_walls, add_duct, add_diffuser, add_text

    doc, msp = create_doc("風管配置圖")
    add_walls(msp, fp.get("walls", []))

    for r in routes:
        if r["type"] == "main" and len(r["pts"]) >= 2:
            p1, p2 = r["pts"][0], r["pts"][-1]
            add_duct(msp, p1[0], p1[1], p2[0], p2[1], r["width_mm"], layer="AC-DUCT-SUP")
            add_text(msp, r["label"], (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2,
                     height=150, layer="AC-TEXT")

        elif r["type"] == "branch" and len(r["pts"]) >= 2:
            p1, p2 = r["pts"][0], r["pts"][-1]
            add_duct(msp, p1[0], p1[1], p2[0], p2[1], r["width_mm"], layer="AC-DUCT-SUP")

        elif r["type"] == "diffuser":
            px, py = r["pts"][0]
            add_diffuser(msp, px, py, size=400, layer="AC-DUCT-SUP")
            add_text(msp, r["label"], px + 250, py, height=120, layer="AC-TEXT")

    doc.saveas(save_path)
