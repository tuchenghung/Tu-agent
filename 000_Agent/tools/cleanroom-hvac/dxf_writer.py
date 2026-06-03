# DXF 輸出工具 — 標準圖層、符號繪製
# 座標單位：mm；比例 1:50 下文字高度 200mm

import ezdxf
from ezdxf.enums import TextEntityAlignment

LAYERS = {
    "AC-WALL":     (8,  "CONTINUOUS", "牆體底圖"),
    "AC-EQUIP":    (1,  "CONTINUOUS", "空調設備"),
    "AC-DUCT-SUP": (3,  "CONTINUOUS", "送風管"),
    "AC-DUCT-RET": (5,  "DASHED2",    "回風管"),
    "AC-PIPE-CHW": (4,  "CONTINUOUS", "冰水管"),
    "AC-PIPE-CW":  (6,  "CENTER2",    "冷卻水管"),
    "AC-PIPE-DRN": (30, "DASHED2",    "排水管"),
    "AC-ELEC":     (2,  "CONTINUOUS", "電力單線圖"),
    "AC-CTRL":     (7,  "CONTINUOUS", "控制架構"),
    "AC-TEXT":     (7,  "CONTINUOUS", "文字標注"),
    "AC-DIM":      (3,  "CONTINUOUS", "尺寸標注"),
    "AC-ZONE":     (9,  "CONTINUOUS", "空調分區"),
}


def create_doc(title: str = "") -> tuple:
    """建立新 DXF 文件，設定所有標準圖層，回傳 (doc, msp)。"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    for name, (color, ltype, _) in LAYERS.items():
        try:
            doc.layers.add(name, color=color, linetype=ltype)
        except Exception:
            doc.layers.add(name, color=color)
    if title:
        msp.add_text(
            title,
            dxfattribs={"layer": "AC-TEXT", "height": 500, "insert": (0, -1000)},
        )
    return doc, msp


def add_rect(msp, x, y, w, h, layer="AC-EQUIP"):
    msp.add_lwpolyline(
        [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
        close=True,
        dxfattribs={"layer": layer},
    )


def add_duct(msp, x1, y1, x2, y2, width_mm, layer="AC-DUCT-SUP"):
    """水平/垂直風管（雙線）"""
    import math
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1:
        return
    nx, ny = -dy / length * width_mm / 2, dx / length * width_mm / 2
    # 中心線
    msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})
    # 雙側邊線
    msp.add_line((x1 + nx, y1 + ny), (x2 + nx, y2 + ny), dxfattribs={"layer": layer})
    msp.add_line((x1 - nx, y1 - ny), (x2 - nx, y2 - ny), dxfattribs={"layer": layer})


def add_pipe(msp, pts: list, layer="AC-PIPE-CHW"):
    for i in range(len(pts) - 1):
        msp.add_line(pts[i], pts[i + 1], dxfattribs={"layer": layer})


def add_diffuser(msp, cx, cy, size=300, layer="AC-DUCT-SUP"):
    """出風口（正方形 + 對角線）"""
    h = size / 2
    add_rect(msp, cx - h, cy - h, size, size, layer=layer)
    msp.add_line((cx - h, cy - h), (cx + h, cy + h), dxfattribs={"layer": layer})
    msp.add_line((cx + h, cy - h), (cx - h, cy + h), dxfattribs={"layer": layer})


def add_text(msp, text, x, y, height=200, layer="AC-TEXT", halign="LEFT"):
    msp.add_text(
        text,
        dxfattribs={"layer": layer, "height": height, "insert": (x, y)},
    )


def add_circle(msp, cx, cy, r, layer="AC-EQUIP"):
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})


def add_walls(msp, walls: list):
    """把解析到的牆線多邊形寫入 AC-WALL 圖層"""
    for pts in walls:
        if len(pts) >= 2:
            msp.add_lwpolyline(
                pts,
                close=len(pts) >= 3,
                dxfattribs={"layer": "AC-WALL"},
            )
