# 報價模組 — 空調工程報價（分項成本 + 售價 + Excel 匯出）
import io
import math
from reference_data import COST, PING_TO_M2

# 報價分類
CATEGORY = {
    "主機設備": "#e63946",
    "空調機組": "#2a9d8f",
    "風管工程": "#e9c46a",
    "水管工程": "#457b9d",
    "電氣工程": "#06d6a0",
    "自動控制": "#9b5de5",
    "施工費用": "#f4a261",
    "其他雜項": "#6c757d",
}

# 每 RT 造價（未稅，成本）
UNIT_COST = {
    # 主機設備
    "冰水主機 (Chiller)":         35_000,   # /RT
    "冷卻水塔":                   5_000,    # /RT
    "冰水泵 (CHWP)":              3_500,    # /RT
    "冷卻水泵 (CWP)":             3_000,    # /RT
    # 空調機組
    "MAU 外氣處理機":             275_000,  # /台 (10RT/5400CMH)
    "AHU 空調箱":                 150_000,  # /台 (估)
    "RCU 循環盤管":               80_000,   # /台
    "FCU 風機盤管":               15_000,   # /台
    "FFU 風機過濾單元 (設備)":    13_000,   # /台
    "FFU 安裝":                    1_200,   # /台
    "D/C 乾盤管":                 45_000,   # /台
    # 風管工程
    "風管製作安裝":                1_050,   # /m²
    "風管保溫":                      500,   # /m²
    "出風口/回風口":                2_500,   # /個
    # 水管工程
    "冰水管配管保溫":              15_000,   # /RT
    "冷卻水管配管":                 8_000,   # /RT
    "排水管":                       3_000,   # /RT
    # 電氣工程
    "配電盤及配線":                 6_000,   # /RT
    "接地工程":                     2_000,   # /RT
    # 自動控制（知識庫：台灣市場 3,000~8,000元/點含軟體，取中值5,500）
    "DDC 控制器及周邊":             8_000,   # /RT（DDC 硬體估算）
    "感測器安裝（含DDC）":          5_500,   # /點（含BMS軟體分攤）
    "BMS 監控軟體（基礎授權）":   120_000,   # /套（固定費）
    # 施工
    "施工綜合費用":                 8_000,   # /RT
    "試運轉及調試":                 5_000,   # /RT
}


def calc_quote(area_m2: float, rt_result: dict,
               airflow_result: dict, system_type: str,
               equipment: dict, io_sum: dict,
               duct_m2: float = 0.0,
               markup: float = 1.30) -> dict:
    """
    計算完整報價分項。
    回傳: {items: [{category, item, unit, qty, unit_price, amount}], ...}
    """
    rt = rt_result["total_rt"]
    ffu_n = airflow_result.get("ffu_count", 0)
    mau_n = equipment.get("mau_count", 0)
    ahu_n = equipment.get("ahu_count", 0)
    rcu_n = equipment.get("rcu_count", 0)
    fcu_n = equipment.get("fcu_count", 0)
    dc_n = equipment.get("dc_count", 0)
    io_pts = io_sum.get("total", 0)
    diffuser_n = math.ceil(area_m2 / 20)  # 約每20m²一個出風口

    items = []

    def add(category, item, unit, qty, unit_price):
        if qty > 0:
            items.append({
                "category": category,
                "item": item,
                "unit": unit,
                "qty": round(qty, 2),
                "unit_price": int(unit_price),
                "amount": int(qty * unit_price),
            })

    # 主機設備
    add("主機設備", "冰水主機 (Chiller)", "RT", rt, UNIT_COST["冰水主機 (Chiller)"])
    add("主機設備", "冷卻水塔", "RT", rt, UNIT_COST["冷卻水塔"])
    add("主機設備", "冰水泵 (CHWP)", "RT", rt, UNIT_COST["冰水泵 (CHWP)"])
    add("主機設備", "冷卻水泵 (CWP)", "RT", rt, UNIT_COST["冷卻水泵 (CWP)"])

    # 空調機組
    if mau_n:
        add("空調機組", "MAU 外氣處理機", "台", mau_n, UNIT_COST["MAU 外氣處理機"])
    if ahu_n:
        add("空調機組", "AHU 空調箱", "台", ahu_n, UNIT_COST["AHU 空調箱"])
    if rcu_n:
        add("空調機組", "RCU 循環盤管", "台", rcu_n, UNIT_COST["RCU 循環盤管"])
    if fcu_n:
        add("空調機組", "FCU 風機盤管", "台", fcu_n, UNIT_COST["FCU 風機盤管"])
    if ffu_n:
        add("空調機組", "FFU 風機過濾單元", "台", ffu_n, UNIT_COST["FFU 風機過濾單元 (設備)"])
        add("空調機組", "FFU 安裝費", "台", ffu_n, UNIT_COST["FFU 安裝"])
    if dc_n:
        add("空調機組", "D/C 乾盤管", "台", dc_n, UNIT_COST["D/C 乾盤管"])

    # 風管工程
    duct = duct_m2 or area_m2 * 0.5
    add("風管工程", "風管製作安裝", "m²", duct, UNIT_COST["風管製作安裝"])
    add("風管工程", "風管保溫", "m²", duct, UNIT_COST["風管保溫"])
    add("風管工程", "出風口/回風口", "個", diffuser_n, UNIT_COST["出風口/回風口"])

    # 水管工程
    add("水管工程", "冰水管配管保溫", "RT", rt, UNIT_COST["冰水管配管保溫"])
    add("水管工程", "冷卻水管配管", "RT", rt, UNIT_COST["冷卻水管配管"])
    add("水管工程", "排水管", "RT", rt, UNIT_COST["排水管"])

    # 電氣工程
    add("電氣工程", "配電盤及配線", "RT", rt, UNIT_COST["配電盤及配線"])
    add("電氣工程", "接地工程", "RT", rt, UNIT_COST["接地工程"])

    # 自動控制
    add("自動控制", "DDC 控制器及周邊", "RT", rt, UNIT_COST["DDC 控制器及周邊"])
    add("自動控制", "感測器安裝（含DDC）", "點", io_pts, UNIT_COST["感測器安裝（含DDC）"])
    add("自動控制", "BMS 監控軟體（基礎授權）", "套", 1, UNIT_COST["BMS 監控軟體（基礎授權）"])

    # 施工費
    add("施工費用", "施工綜合費用", "RT", rt, UNIT_COST["施工綜合費用"])
    add("施工費用", "試運轉及調試", "RT", rt, UNIT_COST["試運轉及調試"])

    subtotal = sum(i["amount"] for i in items)
    tax = int(subtotal * 0.05)
    total_cost = subtotal
    selling = int(subtotal * markup)
    selling_with_tax = int(selling * 1.05)

    ping = area_m2 / PING_TO_M2

    return {
        "items": items,
        "subtotal": subtotal,
        "tax_5pct": tax,
        "total_cost": total_cost,
        "selling": selling,
        "selling_with_tax": selling_with_tax,
        "markup": markup,
        "rt": rt,
        "area_m2": area_m2,
        "ping": round(ping, 1),
        "unit_price_per_ping": round(selling / ping, 0) if ping > 0 else 0,
        "system_type": system_type,
    }


def to_excel(quote: dict) -> bytes:
    """匯出報價 Excel（含封面摘要 + 明細）。"""
    import pandas as pd
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 摘要頁
        summary_rows = [
            ("系統型式", quote["system_type"]),
            ("空間面積", f"{quote['area_m2']:.0f} m² / {quote['ping']:.0f} 坪"),
            ("冷凍噸", f"{quote['rt']:.1f} RT"),
            ("成本合計（未稅）", f"NT$ {quote['subtotal']:,}"),
            (f"建議售價（成本 × {quote['markup']}）", f"NT$ {quote['selling']:,}"),
            ("含稅售價（+5% 稅）", f"NT$ {quote['selling_with_tax']:,}"),
            ("每坪單價", f"NT$ {quote['unit_price_per_ping']:,.0f}"),
        ]
        pd.DataFrame(summary_rows, columns=["項目", "數值"]).to_excel(
            writer, sheet_name="報價摘要", index=False)

        # 明細頁
        import pandas as pd
        df = pd.DataFrame(quote["items"])
        df["amount"] = df["amount"].apply(lambda x: f"NT$ {x:,}")
        df["unit_price"] = df["unit_price"].apply(lambda x: f"NT$ {x:,}")
        df = df.rename(columns={
            "category": "類別", "item": "品項",
            "unit": "單位", "qty": "數量",
            "unit_price": "單價", "amount": "金額",
        })
        df.to_excel(writer, sheet_name="報價明細", index=False)

        # 分類小計
        cat_rows = []
        cats = {}
        for row in quote["items"]:
            cats.setdefault(row["category"], 0)
            cats[row["category"]] += row["amount"]
        for cat, amt in cats.items():
            cat_rows.append({"類別": cat, "小計": f"NT$ {amt:,}",
                             "佔比": f"{amt / quote['subtotal'] * 100:.1f}%"})
        pd.DataFrame(cat_rows).to_excel(writer, sheet_name="分類小計", index=False)

    return output.getvalue()


def draw_quote_chart(ax, quote: dict):
    """圓餅圖 — 各類別造價佔比。"""
    import matplotlib.pyplot as plt

    cats = {}
    for row in quote["items"]:
        cats.setdefault(row["category"], 0)
        cats[row["category"]] += row["amount"]

    labels = list(cats.keys())
    sizes = list(cats.values())
    colors = [CATEGORY.get(l, "#888") for l in labels]

    ax.set_facecolor("#12121f")
    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, colors=colors,
        autopct="%1.1f%%", startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(width=0.5, edgecolor="#12121f"),
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(7)

    ax.legend(
        wedges, [f"{l}  NT${v/10000:.0f}萬" for l, v in zip(labels, sizes)],
        loc="lower center", bbox_to_anchor=(0.5, -0.15),
        ncol=2, facecolor="#2d2d44", edgecolor="#666",
        labelcolor="white", fontsize=7,
    )
    ax.set_title(
        f"造價分析 — 成本合計 NT${quote['subtotal']/10000:.0f}萬\n"
        f"建議售價 NT${quote['selling']/10000:.0f}萬（每坪 NT${quote['unit_price_per_ping']:,.0f}）",
        color="white", fontsize=9, pad=8,
    )
