# tongshu-bazi 八字引擎
# 复用 bazi-tool MIT 代码，添加喜用神 v1

from . import lib

from .lib.pillars import calculate_pillars
from .lib.true_solar_time import correct_to_true_solar_time, get_correction_info
from .lib.ten_gods import get_all_ten_gods, get_ten_god
from .lib.five_elements import analyze_five_elements, judge_day_master_strength
from .lib.major_luck import calculate_major_luck
from .lib.relationships import analyze_relationships
from .lib.hidden_stems import get_hidden_stems
from .lib.cities import get_city_coords, list_cities
from .lib.constants import (
    TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING,
    GAN_YINYANG, ZHI_YINYANG, WUXING_SHENG, WUXING_KE,
    HIDDEN_STEMS, HIDDEN_STEM_WEIGHTS,
)