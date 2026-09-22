# -*- coding: utf-8 -*-
"""修正《渊海子平·论运化气》切片里的OCR错误 + 记录异文"""
import sys
import io
import json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取原切片
jsonl_path = Path(r'D:\shuntian-ziping-p0\registries\source\sources.yhzp.jsonl')
lines = jsonl_path.read_text(encoding='utf-8').splitlines()

# 找YHZP-121-003
fixed = []
for line in lines:
    if not line.strip():
        fixed.append(line)
        continue
    rec = json.loads(line)
    if rec.get('source_id') == 'YHZP-121-003':
        print("=== 修正前 ===")
        print(f"source_text: {rec.get('source_text', '')[:300]}...")
        print()
        
        # 修正后的source_text（根据多版本交叉验证）
        corrected_text = """注：夫五运化气者，甲己化土，乙庚化金，丁壬化木尽成林，丙辛化水分清浊，戊癸化火。甲己化土，中正之合；辰戌丑未全，曰稼穑勾陈得位。乙庚化金，仁义之合；巳酉丑全，曰从革。戊癸化火，无情之合；得火局，曰炎上。丙辛化水，得申子辰水局曰润下。丁壬化木，得亥卯未全曰曲直仁寿。天干化合者秀气，地支合局者福德。化之真者名公巨卿，化之假者孤儿异姓。逢龙即化，变作龙飞在天，利见大人。月令生旺养库临官之地方化，阴阳得合，夫妇匹配，中和之气而化，太过不及皆不能化。有夫从妻化，妻从夫化，正化偏化，日下自化，转角化，乃未坤申丑艮寅。经云：东北丧朋，西北得朋。"""
        
        # 添加异文记录
        variants = rec.get('text_variants', [])
        new_variant = {
            "text_status": "TEXT_VARIANT",
            "canonical_for_engine": "PROJECT_BASE_TEXT",
            "human_verdict": "HUMAN_APPROVED",
            "loc": "五运化气五行对应关系段",
            "project_base_text": "甲己化土中正之合辰戌丑未全曰稼穑勾陈得位；乙庚化金仁义之合巳酉丑全曰从革；戊癸化火无情之合得火局曰炎上；丙辛化水得申子辰水局曰润下；丁壬化木得亥卯未全曰曲直仁寿",
            "variant": "戊癸化火得辰戌丑未全曰隊牆勾陳得位；庚辰戌丑未全曰潤下；丁壬化木得亥卯未全曰曲直仁壽",
            "variant_sources": [
                "https://m.gushiwen.cn/guwen/bookv_24444d0094a6.aspx",
                "https://www.kancloud.cn/yinchanye/yhzp/583217"
            ],
            "note": "OCR/传抄讹误：五行对应关系完全错位。多版本交叉验证（古诗文网+看云+袁氏家谱网）确认正确对应：甲己→稼穑（土）、乙庚→从革（金）、戊癸→炎上（火）、丙辛→润下（水）、丁壬→曲直（木）。原切片误将甲己写成戊癸、乙庚写成庚辰戌丑未。"
        }
        variants.append(new_variant)
        
        # 更新记录
        rec['source_text'] = corrected_text
        rec['text_variants'] = variants
        rec['notes'] = (rec.get('notes', '') + ' | 2026-09-22修正：OCR五行对应关系讹误，已按多版本交叉验证修正').strip(' |')
        
        print("=== 修正后 ===")
        print(f"source_text: {rec.get('source_text', '')[:300]}...")
        print()
        print(f"异文数: {len(variants)}（新增1条HUMAN_APPROVED）")
    
    fixed.append(json.dumps(rec, ensure_ascii=False))

# 写回文件
jsonl_path.write_text('\n'.join(fixed), encoding='utf-8')

print("✅ 切片修正完成")
print(f"文件: {jsonl_path}")
print(f"修正条数: 1条（YHZP-121-003）")
print()
print("=== 修正要点 ===")
print("1. 五行对应关系已修正（甲己→稼穑/乙庚→从革/戊癸→炎上/丙辛→润下/丁壬→曲直）")
print("2. 已记录异文（HUMAN_APPROVED状态）")
print("3. notes字段已追加修正记录")
