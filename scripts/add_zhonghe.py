# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

# 1. 在run_queries里加query_zhong_he
old='        query_yongshen_final(network),\n        \n    ]'
new='        query_yongshen_final(network),\n        query_zhong_he(network),\n        \n    ]'
content=content.replace(old,new)

# 2. 在文件末尾加query_zhong_he函数
zhong_he_func='''

def query_zhong_he(network: Dict[str, Any]) -> Dict:
    """原著结构(滴天髓/子平真诠): 中和纯粹 = 日主有根 + 印比透扶 + 非旺极/衰极/弱极.
    结构匹配: has_root AND (YIN_PARTY OR BIJIE_PARTY) AND NOT JIWANG AND NOT JISHUAI AND NOT JIRUO.
    只输出结构匹配; 不判格局高低, 不下吉凶结论."""
    has_root = network['dimensions']['ROOT'].get('has_root', False)
    yin_party = _has_yin_party(network['dimensions'])
    bijie_party = _has_bijie_party(network['dimensions'])
    # 非旺极/衰极/弱极
    root_class = network['dimensions']['ROOT'].get('root_weight_class', '')
    no_root = not has_root
    cai_party = _has_cai_party(network['dimensions'])
    sha_party = _has_guansha_party(network['dimensions'])
    shishang_party = _has_shishang_party(network['dimensions'])
    # 旺极: 得令+重根+印比成党
    seasonal = network['dimensions'].get('SEASONAL', {})
    in_season = seasonal.get('season_status') == 'IN_SEASON'
    jiwang = in_season and root_class == 'HEAVY' and (yin_party or bijie_party)
    # 衰极: 失令+无根+克泄成党
    out_season = seasonal.get('season_status') == 'OUT_OF_SEASON'
    jishuai = out_season and no_root and (sha_party or shishang_party or cai_party)
    # 弱极: 无根+无扶
    jiruo = no_root and not yin_party and not bijie_party
    
    match = has_root and (yin_party or bijie_party) and not jiwang and not jishuai and not jiruo
    return _result(
        query_id='ZP-160-QUERY-ZHONG-HE',
        name='中和纯粹结构',
        classic='滴天髓/子平真诠',
        state='SUPPORTED' if match else 'NOT_SUPPORTED',
        match_type='STRUCTURE_MATCH' if match else 'NO_MATCH',
        matched_nodes=['HAS_ROOT', 'YIN_OR_BIJIE_PARTY', 'NOT_EXTREME'] if match else [],
        matched_edges=['SUPPORT_RELATION', 'ROOT_PRESENT'] if match else [],
        evidence_refs=['DTS-001-001'],  # 滴天髓通神论: 中和纯粹
        boundary_note='只匹配有根+印比透扶+非极端; 不判格局高低, 不下吉凶结论',
    )
'''

# 加_has_bijie_party函数
bijie_func='''

def _has_bijie_party(dim: Dict) -> bool:
    b = dim.get('SUPPORT', {}).get('BIJIE', {})
    return bool(b.get('stem_present') and b.get('root_present'))
'''

# 在_has_yin_party后面加_has_bijie_party
old_yin='''def _has_yin_party(dim: Dict) -> bool:
    y = dim.get('SUPPORT', {}).get('YIN', {})
    return bool(y.get('stem_present') and y.get('root_present'))'''
new_yin=old_yin+bijie_func
content=content.replace(old_yin,new_yin)

content=content+zhong_he_func

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
