# -*- coding: utf-8 -*-
"""
五部经典断语提取脚本
从滴天髓阐微、三命通会、子平真诠、穷通宝鉴、渊海子平中提取断语并分类
"""

import os
import re
import json
from collections import defaultdict

# ============================================================
# 配置
# ============================================================
BASE_DIR = r'D:\today\五部经典断语库'
OUTPUT_BY_CLASSIC = os.path.join(BASE_DIR, '01_按经典分')
OUTPUT_BY_CATEGORY = os.path.join(BASE_DIR, '02_按类别分')
OUTPUT_INDEX = os.path.join(BASE_DIR, '03_综合索引')

SOURCES = {
    '滴天髓阐微': r'D:\today\Canonical-Mining\完整原典补充\滴天髓阐微_garychowcmu.txt',
    '三命通会': r'D:\today\Canonical-Mining\完整原典补充\kanripo三命通会',
    '子平真诠': r'D:\today\Canonical-Mining\完整原典补充\子平真诠评注_bho1668_utf8.txt',
    '穷通宝鉴': r'D:\today\Canonical-Mining\完整原典补充\garychowcmu易藏\穷通宝鉴.txt',
    '渊海子平': r'D:\today\Canonical-Mining\五部经典完整数据\YHZP_渊海子平_完整全文.md',
}

# ============================================================
# 断语识别模式
# ============================================================
# 条件标记词
CONDITION_MARKERS = [
    '凡', '若', '如', '设', '假令', '假如', '若夫', '且如', '大凡', '凡属',
    '如逢', '若遇', '如见', '若有', '若无', '如无', '若逢', '若值', '如值',
    '倘', '脱', '或', '万一', '设使', '设若', '倘若', '倘使', '如其', '若其',
    '苟', '果', '第', '第恐', '第以', '第其',
    '正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月',
    '十一月', '十二月', '甲木', '乙木', '丙火', '丁火', '戊土', '己土', '庚金', '辛金', '壬水', '癸水',
    '生于', '生於', '日干', '日主', '柱中', '命中', '局中',
]

# 结论标记词
CONCLUSION_MARKERS = [
    '则', '必', '主', '为', '皆', '定', '决', '故', '是以', '大抵', '大概',
    '大约', '须', '宜', '忌', '喜', '当', '应', '其', '斯', '即', '乃', '则',
    '定然', '必定', '必然', '一定', '决主', '必主', '定主', '皆主', '则主',
    '主有', '主无', '主吉', '主凶', '主贵', '主贱', '主富', '主贫', '主寿', '主夭',
    '为吉', '为凶', '为贵', '为贱', '为富', '为贫', '为寿', '为夭', '为福', '为祸',
    '名', '号', '谓之', '所谓', '用', '取', '名曰', '号曰', '谓之',
    '不宜', '不可', '不能', '不利', '无益', '有损', '有伤', '有克',
    '富贵', '贫贱', '吉凶', '祸福', '寿夭', '生死', '成败', '得失',
]

# 结果标记词
RESULT_MARKERS = [
    '吉', '凶', '贵', '贱', '贫', '富', '寿', '夭', '死', '生', '福', '祸',
    '灾', '疾', '病', '喜', '忌', '成', '败', '得', '失', '荣', '辱', '显',
    '达', '困', '厄', '亨', '通', '塞', '滞', '顺', '逆', '安', '危', '乐',
    '忧', '苦', '甘', '辛', '劳', '逸', '勤', '惰', '智', '愚', '贤', '不肖',
    '平常人', '上命', '下命', '中命', '光棍', '残疾', '愚懦', '聪明', '雅秀',
    '英雄', '凶暴', '富贵双全', '财官双美', '功名富贵', '荣华富贵',
    '大富大贵', '大富', '大贵', '小富', '小贵', '暴富', '骤富',
    '克妻', '克子', '克夫', '刑妻', '刑子', '伤妻', '伤子',
    '一生', '终身', '平生', '一世', '半路', '中年', '晚年', '少年',
    '发福', '发贵', '发财', '发富', '发达', '成名', '登科', '及第',
    '僧道', '孤寡', '孤独', '鳏寡', '伶仃', '飘零', '漂泊',
    '聪明', '伶俐', '俊秀', '美丽', '丑陋', '凶恶', '善良',
]

# ============================================================
# 分类体系
# ============================================================
CATEGORIES = {
    '旺衰类': {
        'keywords': ['身强', '身弱', '得令', '失令', '得地', '失地', '得势', '失势',
                     '旺', '衰', '强', '弱', '盛', '太过', '不及', '有余', '不足',
                     '日主', '日干', '身旺', '身衰', '身弱', '身强', '比劫', '印绶',
                     '生扶', '克泄', '泄气', '帮身', '扶身', '身弱', '身旺'],
        'desc': '日主强弱、得令失令、旺衰判断相关断语',
    },
    '格局类': {
        'keywords': ['正官', '七杀', '偏官', '正财', '偏财', '正印', '偏印', '枭神',
                     '食神', '伤官', '比肩', '劫财', '建禄', '羊刃', '阳刃', '从格',
                     '化格', '杂气', '专旺', '曲直', '炎上', '稼穑', '从革', '润下',
                     '格局', '取格', '成格', '败格', '破格', '格', '局', '外格',
                     '内格', '正格', '杂格', '变格', '化气', '从杀', '从财', '从儿',
                     '从旺', '从强', '从弱', '从势'],
        'desc': '八字格局、取格、成格败格相关断语',
    },
    '用神喜忌类': {
        'keywords': ['用神', '喜神', '忌神', '相神', '仇神', '喜', '忌', '宜', '不宜',
                     '当用', '当忌', '当喜', '所喜', '所忌', '所用', '所恶', '所好',
                     '利', '不利', '益', '损', '助', '抑', '扶', '克', '生', '泄',
                     '制', '化', '合', '冲', '去', '留', '清', '浊'],
        'desc': '用神选取、喜忌判断、宜忌相关断语',
    },
    '六亲类': {
        'keywords': ['父', '母', '兄', '弟', '姐', '妹', '妻', '夫', '子', '女', '儿',
                     '六亲', '父母', '兄弟', '夫妻', '子女', '祖上', '祖父', '祖母',
                     '伯叔', '姑姨', '外甥', '侄', '孙', '亲族', '亲戚'],
        'desc': '六亲关系、父母兄弟夫妻子女相关断语',
    },
    '财运类': {
        'keywords': ['财', '富', '贫', '钱', '银', '金', '财产', '财富', '资财', '家财',
                     '发财', '破财', '聚财', '散财', '守财', '偏财', '正财', '财星',
                     '财帛', '财源', '财运', '富翁', '穷人', '大富', '小富', '暴富',
                     '渐富', '先富后贫', '先贫后富'],
        'desc': '财运、财富、贫富相关断语',
    },
    '官运类': {
        'keywords': ['官', '贵', '爵', '禄', '功名', '事业', '仕途', '官场', '官职',
                     '官星', '正官', '偏官', '官杀', '官贵', '官禄', '官爵', '官运',
                     '做官', '当官', '升官', '罢官', '丢官', '贵显', '显贵', '大贵',
                     '小贵', '贵格', '贱格', '公卿', '宰相', '尚书', '侍郎', '知府',
                     '知县', '举人', '进士', '状元', '秀才'],
        'desc': '官运、功名、事业、贵贱相关断语',
    },
    '婚姻类': {
        'keywords': ['婚', '姻', '妻', '妾', '夫', '嫁', '娶', '感情', '姻缘', '婚配',
                     '婚姻', '婚嫁', '婚事', '婚期', '晚婚', '早婚', '再婚', '离婚',
                     '休妻', '克妻', '克夫', '妻宫', '夫宫', '妻星', '夫星', '桃花',
                     '红艳', '咸池', '孤寡', '孤辰', '寡宿', '鳏寡', '孤独'],
        'desc': '婚姻、感情、夫妻关系相关断语',
    },
    '子息类': {
        'keywords': ['子', '女', '儿', '嗣', '息', '子女', '子嗣', '儿女', '子息',
                     '子星', '子宫', '子时', '生子', '生女', '多子', '少子', '无子',
                     '克子', '刑子', '损子', '送终', '养老', '传宗', '接代', '继嗣',
                     '螟蛉', '义子', '养子', '私生子'],
        'desc': '子女、子嗣、子息相关断语',
    },
    '疾病类': {
        'keywords': ['疾', '病', '灾', '厄', '患', '症', '健康', '医药', '医生',
                     '疾病', '病症', '病情', '病魔', '久病', '重病', '轻病', '急症',
                     '慢病', '旧病', '新病', '疾病缠身', '病灾', '病痛', '病弱',
                     '残疾', '废疾', '盲', '聋', '哑', '跛', '瘸', '瘫', '疯', '癫',
                     '狂', '痫', '痨', '蛊', '胀', '肿', '痛', '痒', '疮', '疥',
                     '癣', '癞', '痈', '疽', '疔', '疖', '瘤', '癌', '痔', '漏'],
        'desc': '疾病、健康、灾厄相关断语',
    },
    '寿夭类': {
        'keywords': ['寿', '夭', '死', '生', '命', '寿命', '生死', '夭亡', '夭折',
                     '短命', '长命', '高寿', '大寿', '寿元', '寿数', '寿夭', '死生',
                     '死亡', '去世', '过世', '谢世', '辞世', '逝世', '亡故', '身故',
                     '凶死', '横死', '善终', '令终', '正寝', '寿终', '天年', '享年',
                     '逢凶', '化吉', '大难', '不死', '后福'],
        'desc': '寿命、生死、寿夭相关断语',
    },
    '贫贱富贵类': {
        'keywords': ['富', '贵', '贫', '贱', '荣', '辱', '显', '达', '困', '厄',
                     '层次', '格局高低', '大富', '大贵', '中富', '中贵', '小富', '小贵',
                     '暴富', '骤富', '渐富', '先富后贫', '先贫后富', '富贵双全',
                     '财官双美', '功名富贵', '荣华富贵', '贫贱', '寒微', '卑微',
                     '低微', '下流', '庸俗', '鄙俗', '村俗', '粗俗'],
        'desc': '贫贱富贵、格局层次相关断语',
    },
    '流年大运类': {
        'keywords': ['大运', '流年', '岁运', '运', '岁', '限', '小运', '流月', '流日',
                     '行运', '走运', '交运', '脱运', '转运', '逆运', '顺运', '好运',
                     '坏运', '吉运', '凶运', '运限', '运途', '运势', '运气', '运程',
                     '岁君', '太岁', '流年太岁', '流年不利', '流年大吉', '岁运并临',
                     '天克地冲', '反吟', '伏吟', '限运', '大运流年'],
        'desc': '大运、流年、岁运相关断语',
    },
    '刑冲合害类': {
        'keywords': ['刑', '冲', '合', '害', '破', '会', '三合', '六合', '三会',
                     '相冲', '相刑', '相害', '相合', '相会', '相破', '三刑', '六冲',
                     '六害', '六破', '天干合', '地支合', '干合', '支合', '合化',
                     '合而不化', '化气', '冲克', '冲散', '冲动', '冲开', '刑伤',
                     '刑克', '刑害', '破耗', '破坏', '破败', '会局', '合局'],
        'desc': '刑冲合害、三会六合相关断语',
    },
    '神煞类': {
        'keywords': ['贵人', '文昌', '驿马', '桃花', '空亡', '华盖', '将星', '羊刃',
                     '劫煞', '灾煞', '天乙', '太极', '福星', '禄神', '天德', '月德',
                     '三奇', '天赦', '学堂', '词馆', '国印', '金舆', '金神', '魁罡',
                     '亡神', '元辰', '大耗', '小耗', '丧门', '吊客', '白虎', '朱雀',
                     '勾陈', '腾蛇', '青龙', '天后', '太阴', '太阳', '天官', '天厨',
                     '天喜', '红鸾', '天姚', '咸池', '沐浴', '冠带', '临官', '帝旺',
                     '衰', '病', '死', '墓', '绝', '胎', '养', '长生', '沐浴'],
        'desc': '神煞、贵人、桃花、空亡等相关断语',
    },
    '女命类': {
        'keywords': ['女', '妇', '妾', '妻', '夫人', '女命', '妇人', '女子', '女人',
                     '女性', '闺女', '处女', '寡妇', '孀妇', '妾命', '偏房', '侧室',
                     '填房', '继室', '正室', '嫡妻', '庶妻', '命妇', '诰命', '夫人',
                     '淑人', '恭人', '宜人', '安人', '孺人'],
        'desc': '女命、妇人、妻妾相关断语',
    },
    '小儿类': {
        'keywords': ['小儿', '孩童', '幼年', '童', '幼', '小儿关煞', '孩童', '儿童',
                     '童年', '幼童', '幼子', '幼女', '婴', '婴儿', '襁褓', '孩提',
                     '童限', '小限', '童限运', '关煞', '百日关', '千日关', '阎王关',
                     '鬼门关', '断桥关', '深水关', '汤火关', '四柱关', '将军箭',
                     '取命关', '铁蛇关', '鸡飞关', '落井关', '急脚关', '无情关',
                     '和尚关', '埋儿关', '天狗关', '天吊关', '浴盆关', '水火关',
                     '断肠关', '短命关', '夜啼关', '金木关', '五鬼关', '白虎关'],
        'desc': '小儿、孩童、幼年关煞相关断语',
    },
}

# ============================================================
# 读取函数
# ============================================================
def read_classic(name, path):
    """读取一部经典，返回段落列表"""
    paragraphs = []
    
    if os.path.isdir(path):
        # 目录：读取所有txt文件
        files = sorted([f for f in os.listdir(path) if f.endswith('.txt')])
        for fn in files:
            fp = os.path.join(path, fn)
            text = read_file(fp)
            paragraphs.extend(split_paragraphs(text, name, fn))
    else:
        text = read_file(path)
        paragraphs.extend(split_paragraphs(text, name, os.path.basename(path)))
    
    return paragraphs

def read_file(path):
    """读取文件，自动检测编码"""
    for enc in ['utf-8', 'gbk', 'gb18030', 'big5', 'utf-16']:
        try:
            with open(path, encoding=enc, errors='strict') as f:
                return f.read()
        except:
            continue
    # 最后尝试忽略错误
    with open(path, encoding='utf-8', errors='ignore') as f:
        return f.read()

def split_paragraphs(text, classic_name, source_file):
    """将文本分割为段落"""
    paragraphs = []
    
    # 检测kanripo格式（每行末尾有¶符号）
    if '¶' in text and ('mandoku' in text or 'KR3g' in text or '欽定四庫' in text):
        return split_kanripo_paragraphs(text, classic_name, source_file)
    
    # 按换行分割，过滤空行和过短行
    raw_lines = text.split('\n')
    current_para = []
    
    for line in raw_lines:
        line = line.strip()
        # 过滤标题行、目录行、空行
        if not line:
            if current_para:
                para_text = ''.join(current_para)
                if len(para_text) >= 10:
                    paragraphs.append({
                        'text': para_text,
                        'classic': classic_name,
                        'source': source_file,
                    })
                current_para = []
            continue
        # 过滤明显的标题/目录行
        if re.match(r'^[#\-\*=\s]+$', line):
            continue
        if len(line) < 3 and not re.search(r'[吉凶恶喜忌贵贱富贫寿夭]', line):
            continue
        current_para.append(line)
    
    if current_para:
        para_text = ''.join(current_para)
        if len(para_text) >= 10:
            paragraphs.append({
                'text': para_text,
                'classic': classic_name,
                'source': source_file,
            })
    
    return paragraphs

def split_kanripo_paragraphs(text, classic_name, source_file):
    """处理kanripo格式的文本（四库全书版）"""
    paragraphs = []
    
    # 移除元数据行
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # 跳过元数据行
        if line.startswith('#') or line.startswith('#+'):
            continue
        # 移除页码标记
        line = re.sub(r'<pb:[^>]+>', '', line)
        # 移除¶符号
        line = line.replace('¶', '')
        # 移除全角空格
        line = line.replace('\u3000', '')
        line = line.strip()
        if line and len(line) >= 2:
            lines.append(line)
    
    # 将所有行连接成一个大文本
    full_text = ''.join(lines)
    
    # 按句子分割（中文句号、问号、感叹号、分号）
    sentences = re.split(r'[。！？；]', full_text)
    
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        
        # 如果句子太长（繁体文本可能没有句号），按固定长度分割
        if len(sent) > 500:
            # 按150字左右分割，尽量在标点处断开
            chunks = split_long_text(sent, 150)
            for chunk in chunks:
                if len(chunk) >= 10 and len(chunk) <= 500:
                    paragraphs.append({
                        'text': chunk,
                        'classic': classic_name,
                        'source': source_file,
                    })
        elif len(sent) >= 10:
            paragraphs.append({
                'text': sent,
                'classic': classic_name,
                'source': source_file,
            })
    
    return paragraphs

def split_long_text(text, max_len=150):
    """将长文本分割成较短的片段，尽量在标点处断开"""
    chunks = []
    # 尝试在常见标点处断开
    break_points = [',', '，', '、', '：', ':', '；', ';', '。', '！', '？', ' ', '\t']
    
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        
        # 如果不是最后一段，尝试在标点处提前断开
        if end < len(text):
            # 从end往前找最近的标点
            for i in range(end, start + max_len // 2, -1):
                if text[i-1] in break_points:
                    end = i
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    
    return chunks

# ============================================================
# 断语识别
# ============================================================
def is_duanyu(text):
    """判断一段文字是否包含断语"""
    # 长度过滤
    if len(text) < 8 or len(text) > 500:
        return False
    
    # 检查是否包含条件标记
    has_condition = any(marker in text for marker in CONDITION_MARKERS)
    # 检查是否包含结论标记
    has_conclusion = any(marker in text for marker in CONCLUSION_MARKERS)
    # 检查是否包含结果标记
    has_result = any(marker in text for marker in RESULT_MARKERS)
    
    # 断语判定：放宽条件
    # 1. 条件+结论，或条件+结果，或结论+结果
    if (has_condition and has_conclusion) or \
       (has_condition and has_result) or \
       (has_conclusion and has_result):
        return True
    
    # 2. 单独有明确的判断词组合（喜/忌/宜/不宜 + 结果）
    if re.search(r'[喜忌宜][^。！？；]{0,20}[吉凶恶贵贱富贫寿夭福祸成败]', text):
        return True
    
    # 3. 得XX，XX模式（如"得丙癸逢，富贵双全"）
    if re.search(r'得[甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]{1,4}[，,。][^。]{0,30}[吉凶恶贵贱富贫寿夭福祸]', text):
        return True
    
    # 4. 用XX者，XX模式（如"用庚者，土为妻，金为子"）
    if re.search(r'用[甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥金木水火土]{1,4}者', text):
        return True
    
    # 5. 名XX/号XX/谓之XX模式
    if re.search(r'[名号謂之][^。]{2,20}[格局命人]', text):
        return True
    
    # 6. 额外模式：明确的判断句
    judgment_patterns = [
        r'主[吉凶恶喜忌贵贱富贫寿夭福祸成败]',
        r'为[吉凶恶喜忌贵贱富贫寿夭福祸成败]',
        r'必[主为有吉凶恶喜忌贵贱富贫寿夭]',
        r'则[主为有吉凶恶喜忌贵贱富贫寿夭]',
        r'皆[主为有吉凶恶喜忌贵贱富贫寿夭]',
        r'定[主为有吉凶恶喜忌贵贱富贫寿夭]',
        r'决[主为有吉凶恶喜忌贵贱富贫寿夭]',
        r'[喜忌宜][^。]{0,15}[则必主为皆定决]',
        r'[正偏][官杀财印][^。]{0,15}[格局]',
        r'[从化][格杀财儿旺强势]',
    ]
    for pattern in judgment_patterns:
        if re.search(pattern, text):
            return True
    
    return False

def extract_duanyu_from_paragraph(para):
    """从段落中提取断语句子"""
    text = para['text']
    duanyu_list = []
    
    # 如果段落已经是句子级别（kanripo格式），直接判断
    if len(text) <= 300 and '。' not in text[:50]:
        if is_duanyu(text):
            duanyu_list.append({
                'text': text,
                'classic': para['classic'],
                'source': para['source'],
            })
        return duanyu_list
    
    # 按句子分割（中文句号、问号、感叹号、分号）
    sentences = re.split(r'[。！？；\n]', text)
    
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 8 or len(sent) > 300:
            continue
        if is_duanyu(sent):
            duanyu_list.append({
                'text': sent,
                'classic': para['classic'],
                'source': para['source'],
            })
    
    return duanyu_list

# ============================================================
# 分类
# ============================================================
def classify_duanyu(duanyu_text):
    """对断语进行分类，返回匹配的类别列表"""
    matched_categories = []
    
    for cat_name, cat_info in CATEGORIES.items():
        score = 0
        matched_keywords = []
        for kw in cat_info['keywords']:
            if kw in duanyu_text:
                score += 1
                matched_keywords.append(kw)
        
        if score >= 1:
            matched_categories.append({
                'category': cat_name,
                'score': score,
                'keywords': matched_keywords,
            })
    
    # 按匹配分数排序
    matched_categories.sort(key=lambda x: x['score'], reverse=True)
    return matched_categories

# ============================================================
# 主流程
# ============================================================
def main():
    print('='*70)
    print('五部经典断语提取')
    print('='*70)
    
    # 1. 读取所有经典
    print('\n【1】读取五部经典...')
    all_paragraphs = []
    for name, path in SOURCES.items():
        paras = read_classic(name, path)
        all_paragraphs.extend(paras)
        print(f'  {name}: {len(paras)} 段')
    
    print(f'  总计: {len(all_paragraphs)} 段')
    
    # 2. 提取断语
    print('\n【2】提取断语...')
    all_duanyu = []
    for para in all_paragraphs:
        duanyus = extract_duanyu_from_paragraph(para)
        all_duanyu.extend(duanyus)
    
    print(f'  提取到断语: {len(all_duanyu)} 条')
    
    # 按经典统计
    classic_stats = defaultdict(int)
    for d in all_duanyu:
        classic_stats[d['classic']] += 1
    for name, count in classic_stats.items():
        print(f'    {name}: {count} 条')
    
    # 3. 分类
    print('\n【3】分类断语...')
    categorized = defaultdict(list)  # category -> list of duanyu
    uncategorized = []
    
    for d in all_duanyu:
        cats = classify_duanyu(d['text'])
        if cats:
            # 取最高分的类别（主类别）
            primary_cat = cats[0]['category']
            d['categories'] = cats
            d['primary_category'] = primary_cat
            categorized[primary_cat].append(d)
            # 同时加入其他匹配类别
            for c in cats[1:]:
                if c['score'] >= 2:  # 只有分数>=2才加入副类别
                    categorized[c['category']].append(d)
        else:
            uncategorized.append(d)
    
    print(f'  已分类: {sum(len(v) for v in categorized.values())} 条次')
    print(f'  未分类: {len(uncategorized)} 条')
    
    # 各类别统计
    print('\n  各类别统计:')
    for cat_name in CATEGORIES.keys():
        count = len(categorized.get(cat_name, []))
        print(f'    {cat_name}: {count} 条')
    
    # 4. 保存按经典分的文件
    print('\n【4】保存按经典分的文件...')
    for classic_name in SOURCES.keys():
        classic_duanyu = [d for d in all_duanyu if d['classic'] == classic_name]
        if not classic_duanyu:
            continue
        
        filepath = os.path.join(OUTPUT_BY_CLASSIC, f'{classic_name}_断语.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'# {classic_name} 断语集\n\n')
            f.write(f'> 来源：{classic_name}\n')
            f.write(f'> 提取断语：{len(classic_duanyu)} 条\n\n')
            f.write('---\n\n')
            
            # 按主类别分组
            by_cat = defaultdict(list)
            for d in classic_duanyu:
                cat = d.get('primary_category', '未分类')
                by_cat[cat].append(d)
            
            for cat_name in CATEGORIES.keys():
                cat_duanyu = by_cat.get(cat_name, [])
                if not cat_duanyu:
                    continue
                f.write(f'## {cat_name}\n\n')
                f.write(f'> {CATEGORIES[cat_name]["desc"]}\n\n')
                for i, d in enumerate(cat_duanyu, 1):
                    f.write(f'**{i}.** {d["text"]}\n\n')
                f.write('---\n\n')
            
            # 未分类
            uncat = by_cat.get('未分类', [])
            if uncat:
                f.write(f'## 未分类\n\n')
                for i, d in enumerate(uncat, 1):
                    f.write(f'**{i}.** {d["text"]}\n\n')
        
        print(f'  已保存: {filepath} ({len(classic_duanyu)} 条)')
    
    # 5. 保存按类别分的文件
    print('\n【5】保存按类别分的文件...')
    for cat_name, cat_info in CATEGORIES.items():
        cat_duanyu = categorized.get(cat_name, [])
        if not cat_duanyu:
            continue
        
        filepath = os.path.join(OUTPUT_BY_CATEGORY, f'{cat_name}_断语.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'# {cat_name} 断语集\n\n')
            f.write(f'> {cat_info["desc"]}\n')
            f.write(f'> 五部经典合计：{len(cat_duanyu)} 条\n\n')
            f.write('---\n\n')
            
            # 按经典分组
            by_classic = defaultdict(list)
            for d in cat_duanyu:
                by_classic[d['classic']].append(d)
            
            for classic_name in SOURCES.keys():
                classic_duanyu = by_classic.get(classic_name, [])
                if not classic_duanyu:
                    continue
                f.write(f'## 《{classic_name}》\n\n')
                for i, d in enumerate(classic_duanyu, 1):
                    f.write(f'**{i}.** {d["text"]}\n\n')
                f.write('---\n\n')
        
        print(f'  已保存: {filepath} ({len(cat_duanyu)} 条)')
    
    # 6. 保存综合索引
    print('\n【6】保存综合索引...')
    index_path = os.path.join(OUTPUT_INDEX, '断语总索引.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('# 五部经典断语总索引\n\n')
        f.write('> 从滴天髓阐微、三命通会、子平真诠、穷通宝鉴、渊海子平五部经典中提取的断语\n')
        f.write(f'> 总计提取：{len(all_duanyu)} 条断语\n\n')
        f.write('---\n\n')
        
        f.write('## 一、按经典统计\n\n')
        f.write('| 经典 | 断语数 | 文件 |\n')
        f.write('|------|--------|------|\n')
        for name in SOURCES.keys():
            count = classic_stats.get(name, 0)
            f.write(f'| {name} | {count} | [查看](../01_按经典分/{name}_断语.md) |\n')
        
        f.write('\n## 二、按类别统计\n\n')
        f.write('| 类别 | 断语数 | 说明 | 文件 |\n')
        f.write('|------|--------|------|------|\n')
        for cat_name, cat_info in CATEGORIES.items():
            count = len(categorized.get(cat_name, []))
            if count > 0:
                f.write(f'| {cat_name} | {count} | {cat_info["desc"]} | [查看](../02_按类别分/{cat_name}_断语.md) |\n')
        
        f.write(f'\n## 三、未分类断语\n\n')
        f.write(f'共 {len(uncategorized)} 条未分类断语\n\n')
        if uncategorized:
            for i, d in enumerate(uncategorized[:50], 1):
                f.write(f'**{i}.** [{d["classic"]}] {d["text"]}\n\n')
            if len(uncategorized) > 50:
                f.write(f'... 还有 {len(uncategorized) - 50} 条\n')
    
    print(f'  已保存: {index_path}')
    
    # 7. 保存JSON数据
    print('\n【7】保存JSON数据...')
    json_path = os.path.join(OUTPUT_INDEX, 'all_duanyu.json')
    json_data = []
    for d in all_duanyu:
        json_data.append({
            'text': d['text'],
            'classic': d['classic'],
            'source': d['source'],
            'primary_category': d.get('primary_category', '未分类'),
            'categories': [c['category'] for c in d.get('categories', [])],
        })
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f'  已保存: {json_path} ({len(json_data)} 条)')
    
    print('\n' + '='*70)
    print('提取完成！')
    print(f'  总断语数: {len(all_duanyu)}')
    print(f'  已分类: {sum(len(v) for v in categorized.values())} 条次')
    print(f'  未分类: {len(uncategorized)}')
    print(f'  输出目录: {BASE_DIR}')
    print('='*70)

if __name__ == '__main__':
    main()
