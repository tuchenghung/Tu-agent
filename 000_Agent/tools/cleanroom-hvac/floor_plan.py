# 平面圖解析模組 — 支援 DXF 自動解析 + JPG/PNG 手動輸入
# ezdxf 座標單位：mm（1:50 圖面）

import re
import math
from pathlib import Path

try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False

# 常見台灣建築 CAD 圖層名（可在 UI 自訂）
DEFAULT_WALL_LAYERS = [
    "C2-RC牆", "C3-輕質隔間", "WALL", "牆", "A-WALL",
    "牆體", "隔間", "PARTITION", "RC", "A-WALL-FULL",
]
DEFAULT_TEXT_LAYERS = [
    "TEXT", "文字", "A-TEXT", "空間名稱", "ROOM", "ANNO",
]


def parse_dxf(filepath: str,
              wall_layers: list = None,
              text_layers: list = None) -> dict:
    """
    解析 DXF 平面圖。
    回傳 {walls, rooms, scale, raw_doc, bbox}
    - walls: list of [(x,y),...] 多邊形點列
    - rooms: list of {name, x, y, area_m2, class, is_cleanroom}
    - scale: mm/unit
    - bbox: (xmin, ymin, xmax, ymax)
    """
    if not HAS_EZDXF:
        raise RuntimeError("請先安裝 ezdxf: pip install ezdxf")

    wl = wall_layers or DEFAULT_WALL_LAYERS
    tl = text_layers or DEFAULT_TEXT_LAYERS

    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    walls = _extract_walls(msp, wl)
    rooms = _extract_rooms(msp)  # 從所有文字萃取
    rooms = _estimate_areas(rooms, walls)
    bbox = _calc_bbox(walls, rooms)

    return {
        "walls": walls,
        "rooms": rooms,
        "scale": 1.0,
        "raw_doc": doc,
        "bbox": bbox,
        "source": "dxf",
        "filepath": str(filepath),
    }


def _extract_walls(msp, wall_layers: list) -> list:
    walls = []
    for e in msp:
        if e.dxf.layer not in wall_layers:
            continue
        if e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
            if len(pts) >= 2:
                walls.append(pts)
        elif e.dxftype() == "LINE":
            s, end = e.dxf.start, e.dxf.end
            walls.append([(s.x, s.y), (end.x, end.y)])
    return walls


_MTEXT_RE = re.compile(r"\\[fFcCWAHIPQSTL][^;]*;|[{}]|\\[Pp]|\\~")


def _clean_mtext(raw: str) -> str:
    return _MTEXT_RE.sub("", raw).replace("\\\\", "\\").strip()


def _extract_rooms(msp) -> list:
    seen = set()
    rooms = []
    for e in msp:
        text = ""
        pos = None
        if e.dxftype() == "TEXT":
            text = (e.dxf.text or "").strip()
            ins = e.dxf.insert
            pos = (ins.x, ins.y)
        elif e.dxftype() == "MTEXT":
            text = _clean_mtext(e.text or "")
            ins = e.dxf.insert
            pos = (ins.x, ins.y)

        if not text or not pos:
            continue
        # 過濾：只留中文、長度 2–12 字的空間名
        ch = sum(1 for c in text if "一" <= c <= "鿿")
        if ch < 1 or len(text) > 20:
            continue
        key = (round(pos[0], 0), round(pos[1], 0))
        if key in seen:
            continue
        seen.add(key)
        rooms.append({
            "name": text,
            "x": pos[0],
            "y": pos[1],
            "area_m2": 0.0,
            "class": "一般空調 (ISO 9)",
            "is_cleanroom": False,
        })
    return rooms


def _estimate_areas(rooms: list, walls: list) -> list:
    """對封閉多邊形 (≥4頂點) 用 point-in-polygon + 面積計算。"""
    closed_walls = [w for w in walls if len(w) >= 4]
    for room in rooms:
        rx, ry = room["x"], room["y"]
        best = 0.0
        for wall_pts in closed_walls:
            if _point_in_polygon(rx, ry, wall_pts):
                a = _polygon_area(wall_pts) / 1_000_000  # mm² → m²
                if a > best:
                    best = a
        room["area_m2"] = round(best, 1)
    return rooms


def _point_in_polygon(px, py, polygon):
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _polygon_area(pts):
    n = len(pts)
    a = 0.0
    for i in range(n):
        j = (i + 1) % n
        a += pts[i][0] * pts[j][1]
        a -= pts[j][0] * pts[i][1]
    return abs(a) / 2


def _calc_bbox(walls, rooms):
    xs, ys = [], []
    for w in walls:
        for x, y in w:
            xs.append(x)
            ys.append(y)
    for r in rooms:
        xs.append(r["x"])
        ys.append(r["y"])
    if not xs:
        return (0, 0, 10000, 10000)
    return (min(xs), min(ys), max(xs), max(ys))


def make_empty_fp(area_m2: float = 0.0, name: str = "全區") -> dict:
    """無平面圖時的預設空白結構（手動輸入用）。"""
    return {
        "walls": [],
        "rooms": [{"name": name, "x": 0, "y": 0,
                   "area_m2": area_m2,
                   "class": "一般空調 (ISO 9)",
                   "is_cleanroom": False}],
        "scale": 1.0,
        "raw_doc": None,
        "bbox": (0, 0, 10000, 10000),
        "source": "manual",
        "filepath": "",
    }


def draw_floorplan(ax, fp: dict, room_colors: dict = None):
    """在 matplotlib axis 上繪製平面圖底圖 + 房間色塊。"""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection
    import numpy as np

    walls = fp.get("walls", [])
    rooms = fp.get("rooms", [])
    bbox = fp.get("bbox", (0, 0, 10000, 10000))

    ax.set_facecolor("#1e1e2e")

    # 畫牆體
    wall_patches = []
    for pts in walls:
        if len(pts) >= 3:
            wall_patches.append(Polygon(pts, closed=True))
        elif len(pts) == 2:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            ax.plot(xs, ys, color="#6c6c8a", lw=0.8)

    if wall_patches:
        pc = PatchCollection(wall_patches, facecolor="#3a3a5c",
                             edgecolor="#8888aa", linewidth=0.6, alpha=0.85)
        ax.add_collection(pc)

    # 標記房間
    palette = ["#e63946", "#2a9d8f", "#e9c46a", "#457b9d",
               "#f4a261", "#a8dadc", "#06d6a0", "#ef476f"]
    for i, room in enumerate(rooms):
        c = (room_colors or {}).get(room["name"], palette[i % len(palette)])
        ax.plot(room["x"], room["y"], "o", color=c, markersize=8)
        ax.annotate(
            f"{room['name']}\n{room['area_m2']:.0f}㎡",
            (room["x"], room["y"]),
            color="white", fontsize=7,
            ha="left", va="bottom",
            xytext=(200, 200), textcoords="offset points",
            arrowprops=dict(arrowstyle="-", color="#aaaacc", lw=0.5),
        )

    x0, y0, x1, y1 = bbox
    pad = max((x1 - x0), (y1 - y0)) * 0.1 or 1000
    ax.set_xlim(x0 - pad, x1 + pad)
    ax.set_ylim(y0 - pad, y1 + pad)
    ax.set_aspect("equal")
    ax.tick_params(colors="#666")
    for sp in ax.spines.values():
        sp.set_edgecolor("#444")
