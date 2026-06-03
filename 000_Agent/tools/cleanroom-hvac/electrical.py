# 無塵室空調計算系統 — 電力規劃模組
# 來源：電力系統.pdf（表6、馬達配電對照表、配電設計表）

import math
from reference_data import (
    MOTOR_FLC_380V, WIRE_SIZE_380V, NFB_AT_SERIES, NFB_AF_SERIES,
    EMT_CONDUIT_4C, GROUND_WIRE, STAR_DELTA_THRESHOLD_KW_380V
)


def get_motor_flc_380v(kw: float) -> float:
    """查380V馬達全載電流。若表中無精確值，用 KW÷658 公式計算。"""
    if kw in MOTOR_FLC_380V:
        return MOTOR_FLC_380V[kw]
    # 最近值查表
    candidates = sorted(MOTOR_FLC_380V.keys())
    for k in candidates:
        if k >= kw:
            return MOTOR_FLC_380V[k]
    # 超出表格範圍：用公式 KW÷658=A
    return round(kw / 0.658, 1)


def select_nfb_at(flc: float, factor: float = 1.5) -> int:
    """
    選 NFB 跳脫容量 AT。
    規則：AT = FLC × factor，向上取標準AT序列。
    來源：電力系統.pdf 配電設計表備註1：NFB以滿載電流×1.5倍。
    """
    required = flc * factor
    for at in NFB_AT_SERIES:
        if at >= required:
            return at
    return NFB_AT_SERIES[-1]


def select_nfb_af(at: int) -> str:
    """依 AT 值選 NFB 框架容量 AF。"""
    for max_at, af in NFB_AF_SERIES:
        if at <= max_at:
            return af
    return "3P-1200"


def select_wire_size(flc: float) -> float:
    """
    選最小線徑 mm²（380V PVC管）。
    規則：線徑安培容量 > NFB AT，確保短路時 NFB 跳脫。
    來源：電力系統.pdf P.4 手寫備註 + 表6。
    """
    for max_current, wire_mm2 in WIRE_SIZE_380V:
        if flc <= max_current:
            return wire_mm2
    return 400.0


def select_emt_conduit(wire_mm2: float) -> int:
    """依線徑選 EMT 管徑 φ（4導線）。來源：電力系統.pdf P.5 表。"""
    for max_wire, phi in EMT_CONDUIT_4C:
        if wire_mm2 <= max_wire:
            return phi
    return 75


def select_ground_wire(nfb_at: int) -> float:
    """依 NFB AT 選接地線 mm²。來源：電力系統.pdf P.9 接地導線選用表。"""
    for max_at, gw in GROUND_WIRE:
        if nfb_at <= max_at:
            return gw
    return 100.0


def get_start_method(kw: float, voltage: int = 380) -> str:
    """
    判斷啟動方式。380V > 37kW（≈50HP）用 Y-△。
    來源：電力系統.pdf P.7 手寫備註。
    """
    if voltage == 380 and kw > STAR_DELTA_THRESHOLD_KW_380V:
        return "Y-△"
    return "MS"


def calc_circuit(name: str, kw: float, voltage: int = 380,
                 phase: str = "3φ") -> dict:
    """
    計算單一迴路完整選型。
    回傳：全載電流、NFB AT/AF、線徑、EMT管徑、接地線、啟動方式。
    """
    if voltage == 380 and phase == "3φ":
        flc = get_motor_flc_380v(kw)
    elif voltage == 220 and phase == "1φ":
        # 單相 220V：A = W ÷ (V × PF) ≈ kW*1000 ÷ (220 × 0.85)
        flc = round(kw * 1000 / (220 * 0.85), 1)
    else:
        # 三相 220V
        flc = round(kw / 0.381, 1)

    nfb_at = select_nfb_at(flc)
    nfb_af = select_nfb_af(nfb_at)
    wire_mm2 = select_wire_size(flc)
    emt_phi = select_emt_conduit(wire_mm2)
    gnd_mm2 = select_ground_wire(nfb_at)
    start = get_start_method(kw, voltage) if phase == "3φ" else "MS"

    return {
        "name": name,
        "kw": kw,
        "voltage": voltage,
        "phase": phase,
        "flc_a": flc,
        "nfb_at": nfb_at,
        "nfb_af": nfb_af,
        "wire_mm2": wire_mm2,
        "emt_phi": emt_phi,
        "gnd_mm2": gnd_mm2,
        "start_method": start,
    }


def calc_panel_nfb(circuits: list[dict]) -> dict:
    """
    計算配電盤總 NFB。
    規則：最大馬達電流 × 1.5 + Σ其餘電流。
    來源：電力系統.pdf ACP-401 單線圖手寫備註。
    """
    if not circuits:
        return {}

    flc_list = [c["flc_a"] for c in circuits]
    max_flc = max(flc_list)
    sum_others = sum(flc_list) - max_flc

    total_required = max_flc * 1.5 + sum_others
    total_kw = sum(c["kw"] for c in circuits)
    total_kva = round(total_kw / 0.85, 1)   # PF=0.85

    panel_at = select_nfb_at(total_required, factor=1.0)
    panel_af = select_nfb_af(panel_at)

    return {
        "max_flc": round(max_flc, 1),
        "sum_others": round(sum_others, 1),
        "total_required_a": round(total_required, 1),
        "panel_nfb_at": panel_at,
        "panel_nfb_af": panel_af,
        "total_kw": round(total_kw, 1),
        "total_kva": total_kva,
        "calc_note": f"{max_flc:.1f}A × 1.5 + {sum_others:.1f}A = {total_required:.1f}A",
    }


def build_hvac_circuits(mau_kw: float, mau_count: int,
                        ahu_kw: float, ahu_count: int,
                        ffu_kw: float, ffu_count: int,
                        pump_kw: float = 0, pump_count: int = 0,
                        humidifier_kw: float = 0.1,
                        humidifier_count: int = 0) -> list[dict]:
    """依設備清單建立迴路清單。"""
    circuits = []

    for i in range(1, mau_count + 1):
        circuits.append(calc_circuit(f"MAU-{i:02d} 風車", mau_kw, 380, "3φ"))
        if humidifier_count > 0:
            circuits.append(calc_circuit(f"MAU-{i:02d} 加濕器", humidifier_kw, 220, "1φ"))

    for i in range(1, ahu_count + 1):
        circuits.append(calc_circuit(f"AHU-{i:02d}", ahu_kw, 380, "3φ"))

    if ffu_count > 0 and ffu_kw > 0:
        # FFU 通常多台並聯在分電盤，以群組計
        ffu_total_kw = ffu_kw * ffu_count
        circuits.append(calc_circuit(f"FFU×{ffu_count}台", ffu_total_kw, 220, "1φ"))

    for i in range(1, pump_count + 1):
        circuits.append(calc_circuit(f"冰水泵-{i:02d}", pump_kw, 380, "3φ"))

    return circuits
