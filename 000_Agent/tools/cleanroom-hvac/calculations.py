# 無塵室空調計算系統 — 空調計算核心模組
# 來源公式：空調規劃基礎Data.xlsx 設計規劃 + 計畫書確認值

import math
from typing import Optional
from reference_data import (
    ACH_TABLE, POSITIVE_PRESSURE_ACH, FFU_AIRFLOW_PER_UNIT,
    RCU_ACH, COST, RT_PER_PING, CHW_PIPE, PING_TO_M2
)


def ping_to_m2(ping: float) -> float:
    return ping * PING_TO_M2


def calc_volume(area_m2: float, height_m: float) -> float:
    return area_m2 * height_m


def get_ach(class_name: str, custom_ach: Optional[float] = None) -> dict:
    if custom_ach:
        return {"ach": custom_ach, "source": "自訂"}
    data = ACH_TABLE[class_name]
    return {"ach": data["ach_default"], "source": f"{data['ach_min']}~{data['ach_max']} 次/hr"}


def calc_airflow(volume_m3: float, class_name: str,
                 system_type: str, custom_ach: Optional[float] = None,
                 exhaust_cmh: float = 0) -> dict:
    """
    計算循環風量、正壓風量、MAU 需求風量。
    volume_m3    : 空間體積 m³
    system_type  : 'MAU+RCU' | 'AHU' | 'FFU' | 'FCU' | 'D/C'
    exhaust_cmh  : 排氣量 CMH（有機排氣、廁排等）
    """
    ach_data = get_ach(class_name, custom_ach)
    ach = ach_data["ach"]

    circulation_cmh = volume_m3 * ach          # CMH

    # 正壓風量（維持室壓微正壓）
    pp_ach = POSITIVE_PRESSURE_ACH["default"]
    positive_pressure_cmh = volume_m3 * pp_ach  # CMH

    ffu_count = 0
    rcu_cmh = 0
    mau_cmh = 0
    ahu_cmh = 0

    if system_type == "FFU循環":
        ffu_count = math.ceil(circulation_cmh / FFU_AIRFLOW_PER_UNIT)
        mau_cmh = exhaust_cmh + positive_pressure_cmh

    elif system_type == "MAU+RCU":
        rcu_ach = RCU_ACH["default"]
        rcu_cmh = volume_m3 * rcu_ach           # RCU 循環風量
        mau_cmh = exhaust_cmh + positive_pressure_cmh

    elif system_type == "AHU全頂送":
        ahu_cmh = circulation_cmh
        mau_cmh = exhaust_cmh + positive_pressure_cmh

    elif system_type in ("FCU", "D/C"):
        ahu_cmh = circulation_cmh               # FCU/D/C 處理循環
        mau_cmh = exhaust_cmh + positive_pressure_cmh

    return {
        "ach": ach,
        "ach_source": ach_data["source"],
        "circulation_cmh": round(circulation_cmh, 0),
        "positive_pressure_cmh": round(positive_pressure_cmh, 0),
        "mau_cmh": round(mau_cmh, 0),
        "rcu_cmh": round(rcu_cmh, 0),
        "ahu_cmh": round(ahu_cmh, 0),
        "ffu_count": ffu_count,
    }


def calc_rt(area_m2: float, class_name: str, system_type: str,
            equipment_heat_kw: float = 0) -> dict:
    """
    計算冷凍噸需求。
    equipment_heat_kw : 設備發熱量 kW（選填，預設 0）
    """
    ping = area_m2 / PING_TO_M2

    if "一般空調" in class_name or "ISO 9" in class_name or system_type == "FCU":
        base_rt = ping / RT_PER_PING
        diversity = 1.0
        note = f"{ping:.1f}坪 ÷ {RT_PER_PING}坪/RT"
    else:
        # 無塵室：以坪數估算後加參差因數
        base_rt = ping / RT_PER_PING
        diversity = COST["mep_diversity_factor"]
        note = f"{ping:.1f}坪 ÷ {RT_PER_PING}坪/RT × 參差因數{diversity}"

    equipment_rt = equipment_heat_kw / 3.517 if equipment_heat_kw else 0
    total_rt = base_rt + equipment_rt

    return {
        "base_rt": round(base_rt, 1),
        "equipment_rt": round(equipment_rt, 1),
        "total_rt": round(total_rt, 1),
        "diversity_rt": round(total_rt * diversity, 1),
        "diversity_factor": diversity,
        "note": note,
    }


def select_chw_pipe(rt: float) -> str:
    for max_rt, size in CHW_PIPE:
        if rt <= max_rt:
            return size
    return "> 8\""


def calc_duct_area(area_m2: float, system_type: str) -> float:
    """風管面積估算 m²（依系統型式與空間面積）"""
    factors = {
        "MAU+RCU":  0.5,
        "AHU全頂送": 0.8,
        "FFU循環":   0.3,   # FFU 風管量少
        "FCU":       0.6,
        "D/C":       0.4,
    }
    return area_m2 * factors.get(system_type, 0.5)


def calc_mau_count(mau_cmh: float,
                   mau_unit_cmh: float = 5400) -> int:
    """MAU 台數（預設單台 5400 CMH = 10RT）"""
    if mau_cmh <= 0:
        return 0
    return math.ceil(mau_cmh / mau_unit_cmh)


def calc_cost(area_m2: float, rt_result: dict,
              airflow_result: dict, system_type: str) -> dict:
    """
    依系統型式計算造價分項。
    回傳：設備費、安裝費、風管費、水管費、成本合計、建議售價。
    """
    total_rt = rt_result["total_rt"]
    diversity_rt = rt_result["diversity_rt"]
    ffu_count = airflow_result["ffu_count"]
    mau_cmh = airflow_result["mau_cmh"]
    duct_m2 = calc_duct_area(area_m2, system_type)
    mau_count = calc_mau_count(mau_cmh)

    costs = {}

    if system_type in ("MAU+RCU", "AHU全頂送", "FFU循環"):
        # C/R 系統
        costs["C/R空調設備 (RCU/AHU)"] = total_rt * COST["cr10k_per_rt"]
        costs["MEP主機配管"] = diversity_rt * COST["mep_per_rt"]
        if ffu_count:
            costs[f"FFU x{ffu_count}台"] = ffu_count * COST["ffu_unit"]
            costs["FFU安裝"] = ffu_count * COST["ffu_install"]
        if mau_count:
            costs[f"MAU x{mau_count}台"] = mau_count * COST["mau_10rt"]

    else:
        # 一般空調
        costs["一般空調設備+配管"] = area_m2 * COST["general_ac_per_m2"]
        costs["MEP主機配管"] = diversity_rt * COST["mep_per_rt"]

    costs["風管製作安裝"] = duct_m2 * COST["duct_per_m2"]
    costs["風管保溫"] = duct_m2 * COST["duct_insulation_m2"]

    subtotal = sum(costs.values())
    selling = subtotal * COST["markup"]

    return {
        "items": costs,
        "subtotal": round(subtotal, 0),
        "selling": round(selling, 0),
        "duct_m2": round(duct_m2, 1),
        "mau_count": mau_count,
    }
