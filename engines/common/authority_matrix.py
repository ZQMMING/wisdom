# -*- coding: utf-8 -*-
"""六经典 Authority Matrix v0.1.
定义每个命理元的 Primary/Secondary/Alternate 轨道归属.
Authority Matrix 只做轨道归属, 不做综合裁决.
3条铁律:
1. Authority Matrix 只做轨道归属, 不做综合裁决
2. 旺衰/强弱保持结构事实+证据+规则, 不擅自形成综合裁决
3. wangshuai_multidim 标记为 Legacy/Reference, 不立即删除
"""
from typing import Dict, List, Any, Optional


# 六经典标识
CLASSIC_BOOKS = {
    'PZZQ': '子平真诠',
    'YHZP': '渊海子平',
    'DTS': '滴天髓',
    'QTBJ': '穷通宝鉴',
    'SFTK': '神峰通考',
    'SMTH': '三命通会',
}


# 命理元定义
META_DEFINITIONS = {
    'WANG_SHUAI': {
        'meta_id': 'WANG_SHUAI',
        'meta_name': '旺衰',
        'definition': '日主是否得时/失时, 即月令维度的五行之气状态. '
                      '《子平真诠》: "得时为旺, 失时为衰". '
                      '旺衰 ≠ 强弱, 可以"虽旺而弱", 也可以"虽衰而强".',
        'primary_track': 'PZZQ',  # 子平真诠: 得时不旺失时不弱专章
        'secondary_tracks': ['YHZP'],  # 渊海子平: 得令即旺的朴素体系
        'alternate_tracks': ['DTS'],  # 滴天髓: 旺衰篇, 五行流通配合
        'activation_condition': 'always',  # 旺衰是基础维度, 始终激活
        'boundary_note': '旺衰只回答得令/失令, 不回答身强/身弱. '
                         '不得旺→自动强, 衰→自动弱. '
                         '最终强弱裁决 NOT_AUTHORIZED.',
        'evidence_refs': [
            'PZZQ-论十干得时不旺失时不弱',
            'YHZP-论旺衰',
            'DTS-旺衰篇',
        ],
    },
    'QIANG_RUO': {
        'meta_id': 'QIANG_RUO',
        'meta_name': '强弱',
        'definition': '日主的力量结构, 即党众/助寡维度. '
                      '《子平真诠》: "党众为强, 助寡为弱". '
                      '强弱 = 得地(根气) + 得势(帮扶) + 泄耗 + 克制 的多维结构. '
                      '强弱 ≠ 旺衰, 可以"虽旺而弱", 也可以"虽衰而强".',
        'primary_track': 'PZZQ',  # 子平真诠: 党众为强助寡为弱
        'secondary_tracks': ['YHZP'],  # 渊海子平: 身强身弱的朴素判断
        'alternate_tracks': ['DTS'],  # 滴天髓: 体用扶抑, 气势流通
        'activation_condition': 'always',  # 强弱是基础维度, 始终激活
        'boundary_note': '强弱输出多维结构事实(得地/得势/泄耗/克制), '
                         '不输出单一的身强/身弱综合裁决. '
                         'Strength Resolver (160-B) NOT_AUTHORIZED. '
                         'wangshuai_multidim 标记为 Legacy/Reference, 待 Authority Matrix 验证.',
        'evidence_refs': [
            'PZZQ-论旺衰强弱分别',
            'YHZP-论身强身弱',
            'DTS-体用篇',
        ],
    },
    'GE_JU': {
        'meta_id': 'GE_JU',
        'meta_name': '格局',
        'definition': '月令定格, 以月令之财官印食杀伤六神分六格. '
                      '《子平真诠》: "八字用神, 专求月令". '
                      '格局是结构识别, 不等于格局成立, 不等于格局高低.',
        'primary_track': 'PZZQ',  # 子平真诠: 八格体系, 格局成败救应
        'secondary_tracks': ['YHZP'],  # 渊海子平: 格局基础分类
        'alternate_tracks': ['SMTH'],  # 三命通会: 月令取格, 六格大纲
        'activation_condition': '月令有可用之神(月令藏干透干或成格)',
        'boundary_note': '格局只输出格神候选和结构识别, '
                         '不输出格局成立/格局高低/富贵贫贱. '
                         '格清/配合保持 PLACEHOLDER. '
                         '相神暂不实现, 保留为后续独立刀.',
        'evidence_refs': [
            'PZZQ-论八格',
            'YHZP-论格局',
            'SMTH-六格大纲',
        ],
    },
    'DIAO_HOU': {
        'meta_id': 'DIAO_HOU',
        'meta_name': '调候',
        'definition': '月令气候寒暖燥湿与日干所需调候. '
                      '《穷通宝鉴》: 通篇以月令气候定取用先后. '
                      '调候是气候所需, 不等于用神最终裁决.',
        'primary_track': 'QTBJ',  # 穷通宝鉴: 四时调候, 气候用神
        'secondary_tracks': ['SMTH'],  # 三命通会: 调候基础
        'alternate_tracks': [],
        'activation_condition': '生于亥子丑或巳午未, 且原局气候极端(调候所需五行极弱或无)',
        'boundary_note': '调候只输出调候候选和气候修正, '
                         '不输出用神最终裁决. '
                         'D5/T16 月令效力修正已接入, 修正月令效力未做.',
        'evidence_refs': [
            'QTBJ-四时调候',
            'SMTH-论调候',
        ],
    },
    'BING_YAO': {
        'meta_id': 'BING_YAO',
        'meta_name': '病药',
        'definition': '命局中存在的破坏平衡的有害之神(病), '
                      '以及能够克制去除病神的字(药). '
                      '《神峰通考》: "有病方为贵, 无伤不是奇". '
                      '病药是病机诊断, 不等于用神最终裁决.',
        'primary_track': 'SFTK',  # 神峰通考: 病药体系, 张楠核心思想
        'secondary_tracks': ['DTS'],  # 滴天髓: 病药相关论述
        'alternate_tracks': [],
        'activation_condition': '存在明显病(伤官见官/七杀攻身/枭神夺食/财多身弱/比劫夺财), 且病无制无化',
        'boundary_note': '病药只输出病机和药神候选, '
                         '不输出用神最终裁决. '
                         'bingyao_layer 已实现(命局病机药神枚举+应期去病添病).',
        'evidence_refs': [
            'SFTK-病药说',
            'DTS-病药相关',
        ],
    },
    'YONG_SHEN': {
        'meta_id': 'YONG_SHEN',
        'meta_name': '用神',
        'definition': '用神有多种, 不能混为一谈: '
                      '格局用神(子平真诠月令定格)、调候用神(穷通宝鉴气候所需)、'
                      '病药用神(神峰通考去病之药)、扶抑用神(滴天髓体用扶抑). '
                      '用神是多轨并行, 不是单一答案.',
        'primary_track': 'PZZQ',  # 子平真诠: 格局用神, 月令用神
        'secondary_tracks': ['QTBJ'],  # 穷通宝鉴: 调候用神
        'alternate_tracks': ['SFTK', 'DTS'],  # 神峰通考: 病药用神; 滴天髓: 扶抑用神
        'activation_condition': '格局轨/调候轨/病药轨/体用轨任一激活',
        'boundary_note': '用神四轨并行, 冲突保留不裁决. '
                         '不输出单一的最终用神. '
                         'yongshen_multi_track 已实现, 命中率@K 100%. '
                         '渊海子平/三命通会降级为基础事实校验层, 不作为独立用神轨道.',
        'evidence_refs': [
            'PZZQ-论用神',
            'QTBJ-调候用神',
            'SFTK-病药用神',
            'DTS-扶抑用神',
        ],
    },
}


def get_meta_definition(meta_id: str) -> Optional[Dict[str, Any]]:
    """获取命理元定义."""
    return META_DEFINITIONS.get(meta_id)


def get_all_meta_ids() -> List[str]:
    """获取所有命理元ID."""
    return list(META_DEFINITIONS.keys())


def get_tracks_for_meta(meta_id: str) -> Dict[str, Any]:
    """获取命理元的轨道归属."""
    meta = META_DEFINITIONS.get(meta_id)
    if not meta:
        return {}
    return {
        'primary': meta['primary_track'],
        'secondary': meta['secondary_tracks'],
        'alternate': meta['alternate_tracks'],
    }


def is_track_activated(meta_id: str, facts: Dict[str, Any]) -> bool:
    """检查轨道是否激活(简化版, 后续细化)."""
    meta = META_DEFINITIONS.get(meta_id)
    if not meta:
        return False
    if meta['activation_condition'] == 'always':
        return True
    # 其他激活条件后续细化
    return True


def get_authority_matrix_summary() -> Dict[str, Any]:
    """获取 Authority Matrix 摘要."""
    summary = {}
    for meta_id, meta in META_DEFINITIONS.items():
        summary[meta_id] = {
            'name': meta['meta_name'],
            'primary': CLASSIC_BOOKS.get(meta['primary_track'], meta['primary_track']),
            'secondary': [CLASSIC_BOOKS.get(t, t) for t in meta['secondary_tracks']],
            'alternate': [CLASSIC_BOOKS.get(t, t) for t in meta['alternate_tracks']],
            'activation': meta['activation_condition'],
        }
    return summary


# Authority Matrix 版本
AUTHORITY_MATRIX_VERSION = 'v0.1'
AUTHORITY_MATRIX_BOUNDARY_NOTE = (
    'Authority Matrix 只做轨道归属, 不做综合裁决. '
    '旺衰/强弱保持结构事实+证据+规则, 不擅自形成综合裁决. '
    'wangshuai_multidim 标记为 Legacy/Reference, 待 Authority Matrix 验证.'
)
