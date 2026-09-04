# Phase 5-B: Daily State Service
#
# ⚠️ WIP — 使用旧版 time_sequence/dayu 占位实现，已被 timeline_yun.py 替代。
#   生产路径请使用 canonical.HeluoCanonical → timeline_yun 计算链。
#   此文件暂无调用方，导入失败不影响主流程。

# 兼容：使用新 timeline_yun 替代已废弃的 time_sequence/dayu
try:
    from tongshu.engines.heluo.timeline_yun import (  # noqa: F401
        compute_liunian, compute_liuyue, compute_liuri,
    )
except ImportError:
    compute_liunian = compute_liuyue = compute_liuri = None

try:
    from tongshu.engines.heluo.timeline_yun import compute_dayun_liyao  # noqa: F401
except ImportError:
    compute_dayun_liyao = None

logger = logging.getLogger(__name__)


@dataclass
class EnergyState:
    """能量状态。"""
    level: str  # 旺盛/平和/衰退
    score: float  # 0-100
    description: str


@dataclass
class DailyState:
    """每日状态。"""
    date: date
    energy_state: EnergyState
    hexagram_state: dict
    element_balance: dict
    advice_context: str
    liu_nian: str
    liu_yue: str
    liu_ri: str


def compute_daily_state(
    user_id: str,
    birth_info: dict,
    target_date: Optional[date] = None
) -> DailyState:
    """计算用户指定日期的状态。"""
    if target_date is None:
        target_date = date.today()
    
    # 获取流年流月流日
    year_ganzhi = birth_info.get("year_ganzhi", "甲子")
    # 从干支提取年份（取后半部分）
    import re
    year_match = re.search(r'[子丑寅卯辰巳午未申酉戌亥]$', year_ganzhi)
    birth_year = 2024 if not year_match else 2024  # 简化：使用固定基准年
    gender = birth_info.get("gender", "male")
    
    liu_nian_result = compute_liu_nian(LiuNianInput(birth_year=birth_year, target_year=target_date.year, gender=gender))
    liu_nian = liu_nian_result.liu_nian_ganzhi
    
    liu_yue_result = compute_liu_yue(LiuYueInput(birth_year=birth_year, birth_month=1, target_year=target_date.year, target_month=target_date.month, gender=gender))
    liu_yue = liu_yue_result.liu_yue_ganzhi
    
    liu_ri_result = compute_liu_ri(LiuRiInput(
        birth_year=birth_year, birth_month=1, birth_day=1,
        target_date=datetime.combine(target_date, datetime.min.time()), gender=gender
    ))
    liu_ri = liu_ri_result.liu_ri_ganzhi
    
        # 计算个人模型
    from tongshu.engines.heluo.schemas import HeluoBirthInput
    calculator = HeluoCalculator()
    
    # 转换 birth_info dict 为 HeluoBirthInput
    birth_year_num = 1990
    birth_month_num = 1
    birth_day_num = 1
    
    heluo_input = HeluoBirthInput(
        birth_year=birth_year_num,
        birth_month=birth_month_num,
        birth_day=birth_day_num,
        birth_hour=12,  # 简化：使用正午
        gender=birth_info.get("gender", "male")
    )
    model = calculator.compute(heluo_input)
    
    # 将 HeluoResult 转换为 dict 方便访问
    model_dict = {
        'benming_hexagram': getattr(model, 'benming_hexagram', ''),
        'yuan_tang': getattr(model, 'yuan_tang', ''),
        'postnatal_hexagram': getattr(model, 'postnatal_hexagram', ''),
        'dominant_element': getattr(model, 'dominant_element', '火')
    }
    
    # 计算五行平衡
    element_balance = _calc_element_balance(model_dict)
    
    # 计算能量状态
    energy_state = _calc_energy_state(model_dict, element_balance, liu_nian, liu_yue, liu_ri)
    
    # 生成建议
    advice = _gen_advice(energy_state, element_balance, model_dict)
    
    return DailyState(
        date=target_date,
        energy_state=energy_state,
        hexagram_state={
            "benming": model_dict.get("benming_hexagram", ""),
            "postnatal": model_dict.get("postnatal_hexagram", ""),
            "liu_nian": liu_nian,
            "liu_yue": liu_yue,
            "liu_ri": liu_ri
        },
        element_balance=element_balance,
        advice_context=advice,
        liu_nian=liu_nian,
        liu_yue=liu_yue,
        liu_ri=liu_ri
    )


def _calc_element_balance(model) -> dict:
    """计算五行平衡。"""
    # 简化版：基于本命卦和元堂
    # model 是 HeluoResult，转换为 dict 访问
    try:
        dominant = getattr(model, 'dominant_element', '火') or '火'
    except:
        dominant = '火'
    
    # 五行总和为1.0
    balance = {"金": 0.2, "木": 0.2, "水": 0.2, "火": 0.2, "土": 0.2}
    
    # 增强主导元素至0.35，其他等分剩余0.65
    balance[dominant] = 0.35
    remaining = 0.65
    others = [e for e in balance if e != dominant]
    for e in others:
        balance[e] = remaining / len(others)
    
    return balance


def _get_enemy_element(element: str) -> str:
    """获取相克元素。"""
    enemies = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
    return enemies.get(element, "土")


def _calc_energy_state(
    model: dict,
    element_balance: dict,
    liu_nian: str,
    liu_yue: str,
    liu_ri: str
) -> EnergyState:
    """计算能量状态。"""
    # 基于五行平衡和流年流月流日计算
    dominant = element_balance.get(max(element_balance.items(), key=lambda x: x[1])[0], 0.2)
    
    # 基础分数
    base_score = dominant * 100
    
    # 流年修正
    year_modifier = _get_year_modifier(liu_nian)
    base_score += year_modifier * 10
    
    # 流月修正
    month_modifier = _get_month_modifier(liu_yue)
    base_score += month_modifier * 5
    
    # 流日修正
    day_modifier = _get_day_modifier(liu_ri)
    base_score += day_modifier * 2
    
    # 归一化
    score = max(0, min(100, base_score))
    
    # 确定等级
    if score >= 75:
        level = "旺盛"
        desc = "能量充沛，宜主动进取"
    elif score >= 50:
        level = "平和"
        desc = "能量平稳，宜稳中求进"
    else:
        level = "衰退"
        desc = "能量不足，宜保守防守"
    
    return EnergyState(level=level, score=round(score, 2), description=desc)


def _get_year_modifier(liu_nian: str) -> float:
    """获取流年修正系数。"""
    # 简化版：根据干支计算
    return 0.0  # 占位，后续细化


def _get_month_modifier(liu_yue: str) -> float:
    """获取流月修正系数。"""
    return 0.0  # 占位，后续细化


def _get_day_modifier(liu_ri: str) -> float:
    """获取流日修正系数。"""
    return 0.0  # 占位，后续细化


def _gen_advice(energy_state, element_balance, model) -> str:
    """生成建议。"""
    dominant = max(element_balance.items(), key=lambda x: x[1])[0]
    advice_map = {
        "旺盛": f"今日{energy_state.description}，主导五行{dominant}，宜发挥优势。",
        "平和": f"今日{energy_state.description}，五行相对均衡，宜稳步前行。",
        "衰退": f"今日{energy_state.description}，主导五行{dominant}偏弱，宜注意养护。"
    }
    return advice_map.get(energy_state.level, "今日状态正常。")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试
    test_birth = {
        "year_ganzhi": "庚午",
        "month_ganzhi": "辛巳",
        "day_ganzhi": "戊子",
        "hour_ganzhi": "未时",
        "gender": "male"
    }
    
    state = compute_daily_state("test-user", test_birth, date(2026, 8, 21))
    print(f"日期: {state.date}")
    print(f"能量: {state.energy_state.level} ({state.energy_state.score})")
    print(f"流年: {state.liu_nian}, 流月: {state.liu_yue}, 流日: {state.liu_ri}")
    print(f"建议: {state.advice_context}")
