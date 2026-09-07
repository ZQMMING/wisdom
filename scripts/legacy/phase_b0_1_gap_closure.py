#!/usr/bin/env python3
"""
Phase B-0.1 Evidence Gap Closure - Complete Analysis

Analyzes 32 candidate rules against the evidence database,
produces gap closure report with prioritized recommendations.
"""

import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, field, asdict

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class EvidenceItem:
    evidence_id: str
    classic_id: str
    classic_name: str
    evidence_type: str
    observation_dimension: str
    original_text: str
    chapter: str
    passage_id: str
    extraction_quality: float
    authorization_level: str
    verification_status: str
    
@dataclass
class RuleGap:
    rule_id: str
    rule_name: str
    domain: str
    status: str
    evidence_count: int
    matched_evidence: List[dict]
    gaps: List[str]
    recommendation: str
    priority: int

@dataclass
class GapStats:
    total_rules: int
    high_count: int
    medium_count: int
    low_count: int
    pending_count: int
    coverage_rate: float
    by_domain: Dict[str, dict]

# ============================================================================
# RULE DEFINITIONS (32 Candidate Rules)
# ============================================================================

RULES = [
    # ===== 旺衰域 (11条) =====
    {"id": "WS-001", "name": "得令判定", "domain": "wangshuai", "priority": 1,
     "condition": "月支五行生助或同于日主",
     "expected_evidence": ["di_tian_sui", "yuan_hai_zi_ping"],
     "keywords": ["得令", "月令", "旺", "相"],
     "evidence_types": ["DAYMASTER_STRONG"]},
    
    {"id": "WS-002", "name": "失令判定", "domain": "wangshuai", "priority": 1,
     "condition": "月支五行克或被日主克",
     "expected_evidence": ["di_tian_sui", "yuan_hai_zi_ping"],
     "keywords": ["失令", "休囚死"],
     "evidence_types": ["DAYMASTER_WEAK"]},
    
    {"id": "WS-003", "name": "通根判定", "domain": "wangshuai", "priority": 2,
     "condition": "地支藏干含日主五行",
     "expected_evidence": ["yuan_hai_zi_ping"],
     "keywords": ["通根", "根气", "地支"],
     "evidence_types": ["ROOT_PRESENT"]},
    
    {"id": "WS-004", "name": "无根判定", "domain": "wangshuai", "priority": 2,
     "condition": "四柱地支无日主五行藏干",
     "expected_evidence": ["yuan_hai_zi_ping", "di_tian_sui"],
     "keywords": ["无根", "虚浮"],
     "evidence_types": []},
    
    {"id": "WS-005", "name": "比劫帮身", "domain": "wangshuai", "priority": 3,
     "condition": "天干比肩劫财数量>=2",
     "expected_evidence": ["yuan_hai_zi_ping"],
     "keywords": ["比肩", "劫财", "帮身"],
     "evidence_types": ["TEN_GODS_BALANCE"]},
    
    {"id": "WS-006", "name": "印星生身", "domain": "wangshuai", "priority": 3,
     "condition": "天干正印偏印数量>=1",
     "expected_evidence": ["yuan_hai_zi_ping", "ziping_zhenquan"],
     "keywords": ["印绶", "正印", "偏印", "生身"],
     "evidence_types": []},
    
    {"id": "WS-007", "name": "官杀攻身", "domain": "wangshuai", "priority": 3,
     "condition": "天干正官七杀数量>=2",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["官杀", "克身", "攻身"],
     "evidence_types": []},
    
    {"id": "WS-008", "name": "食伤泄身", "domain": "wangshuai", "priority": 3,
     "condition": "天干食神伤官数量>=2",
     "expected_evidence": ["di_tian_sui"],
     "keywords": ["食伤", "泄气", "泄身"],
     "evidence_types": []},
    
    {"id": "WS-009", "name": "综合强判定", "domain": "wangshuai", "priority": 4,
     "condition": "支持因素>=2 (得令+通根+生扶)",
     "expected_evidence": [],
     "keywords": ["综合", "强弱", "判断"],
     "evidence_types": []},
    
    {"id": "WS-010", "name": "综合弱判定", "domain": "wangshuai", "priority": 4,
     "condition": "制约因素>=2 (失令+无根+克泄)",
     "expected_evidence": [],
     "keywords": ["综合", "衰弱"],
     "evidence_types": []},
    
    {"id": "WS-011", "name": "综合中和", "domain": "wangshuai", "priority": 5,
     "condition": "以上条件均不满足",
     "expected_evidence": [],
     "keywords": ["中和", "平衡"],
     "evidence_types": []},
    
    # ===== 格局域 (10条) =====
    {"id": "PT-001", "name": "正官格", "domain": "pattern", "priority": 4,
     "condition": "月令正官透出天干",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["正官", "格局"],
     "evidence_types": ["GEJU_SUCCESS"]},
    
    {"id": "PT-002", "name": "七杀格", "domain": "pattern", "priority": 5,
     "condition": "月令七杀透出天干",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["七杀", "偏官", "格局"],
     "evidence_types": []},
    
    {"id": "PT-003", "name": "正财格", "domain": "pattern", "priority": 6,
     "condition": "月令正财透出天干",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["正财", "格局"],
     "evidence_types": []},
    
    {"id": "PT-004", "name": "偏财格", "domain": "pattern", "priority": 6,
     "condition": "月令偏财透出天干",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["偏财", "格局"],
     "evidence_types": []},
    
    {"id": "PT-005", "name": "正印格", "domain": "pattern", "priority": 6,
     "condition": "月令正印透出天干",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["正印", "格局"],
     "evidence_types": []},
    
    {"id": "PT-006", "name": "偏印格", "domain": "pattern", "priority": 6,
     "condition": "月令偏印透出天干",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["偏印", "枭神", "格局"],
     "evidence_types": []},
    
    {"id": "PT-007", "name": "食神格", "domain": "pattern", "priority": 7,
     "condition": "月令食神透出天干",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["食神", "格局"],
     "evidence_types": []},
    
    {"id": "PT-008", "name": "伤官格", "domain": "pattern", "priority": 7,
     "condition": "月令伤官透出天干",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["伤官", "格局"],
     "evidence_types": []},
    
    {"id": "PT-009", "name": "从格判定", "domain": "pattern", "priority": 0,
     "condition": "日主无根无帮扶",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["从格", "从旺", "从弱"],
     "evidence_types": ["PATTERN_RESCUE"]},
    
    {"id": "PT-010", "name": "化格判定", "domain": "pattern", "priority": 1,
     "condition": "天干五合化气成功",
     "expected_evidence": ["di_tian_sui"],
     "keywords": ["化格", "化气"],
     "evidence_types": []},
    
    # ===== 用神域 (4条) =====
    {"id": "YG-001", "name": "格局用神", "domain": "yongshen", "priority": 1,
     "condition": "格局已成，取相神为用",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["格局用神", "相神"],
     "evidence_types": ["YONGSHEN_VALID"]},
    
    {"id": "YG-002", "name": "调候用神", "domain": "yongshen", "priority": 2,
     "condition": "查穷通宝鉴表",
     "expected_evidence": ["qiong_tong_bao_jian"],
     "keywords": ["调候", "气候"],
     "evidence_types": ["ADJ"]},
    
    {"id": "YG-003", "name": "扶抑用神", "domain": "wangshuai", "priority": 2,
     "condition": "根据旺衰取用",
     "expected_evidence": ["di_tian_sui", "yuan_hai_zi_ping"],
     "keywords": ["扶抑", "抑强扶弱"],
     "evidence_types": []},
    
    {"id": "YG-004", "name": "制化用神", "domain": "yongshen", "priority": 3,
     "condition": "七杀有制化为用",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["制化", "化杀"],
     "evidence_types": []},
    
    # ===== 十神语义域 (3条) =====
    {"id": "TG-001", "name": "十神组合解释", "domain": "ten_god_semantics", "priority": 3,
     "condition": "多个十神组合",
     "expected_evidence": ["yuan_hai_zi_ping", "ziping_zhenquan"],
     "keywords": ["十神组合", "组合"],
     "evidence_types": []},
    
    {"id": "TG-002", "name": "十神位置分析", "domain": "ten_god_semantics", "priority": 3,
     "condition": "十神在四柱位置",
     "expected_evidence": ["yuan_hai_zi_ping"],
     "keywords": ["十神位置", "宫位"],
     "evidence_types": []},
    
    {"id": "TG-003", "name": "十神生克关系", "domain": "ten_god_semantics", "priority": 3,
     "condition": "十神之间的生克制化",
     "expected_evidence": ["di_tian_sui"],
     "keywords": ["十神生克", "制化"],
     "evidence_types": ["TEN_GODS_BALANCE"]},
    
    # ===== 事件判断域 (4条) =====
    {"id": "EV-001", "name": "财运判断", "domain": "event", "priority": 5,
     "condition": "财星旺衰及位置",
     "expected_evidence": ["yuan_hai_zi_ping"],
     "keywords": ["财运", "财富"],
     "evidence_types": []},
    
    {"id": "EV-002", "name": "婚姻判断", "domain": "event", "priority": 5,
     "condition": "夫妻宫及配偶星分析",
     "expected_evidence": ["yuan_hai_zi_ping"],
     "keywords": ["婚姻", "夫妻"],
     "evidence_types": []},
    
    {"id": "EV-003", "name": "事业判断", "domain": "event", "priority": 5,
     "condition": "官杀及格局分析",
     "expected_evidence": ["ziping_zhenquan"],
     "keywords": ["事业", "官运"],
     "evidence_types": []},
    
    {"id": "EV-004", "name": "健康判断", "domain": "event", "priority": 5,
     "condition": "五行失衡分析",
     "expected_evidence": ["yuan_hai_zi_ping"],
     "keywords": ["健康", "疾病"],
     "evidence_types": []},
]

# ============================================================================
# EVIDENCE LOADER
# ============================================================================

class EvidenceLoader:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.evidence_list: List[EvidenceItem] = []
        self.evidence_by_type: Dict[str, List[EvidenceItem]] = {}
        self.evidence_by_classic: Dict[str, List[EvidenceItem]] = {}
        
    def load_all(self):
        classics = ["yuan_hai_zi_ping", "ziping_zhenquan", "di_tian_sui", 
                   "qiong_tong_bao_jian", "san_ming_tong_hui"]
        
        for classic in classics:
            classic_path = self.base_path / classic
            if not classic_path.exists():
                continue
            
            json_files = sorted(classic_path.glob("E-*.json"))
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    item = EvidenceItem(
                        evidence_id=data.get("evidence_id", ""),
                        classic_id=data.get("classic_id", classic),
                        classic_name=data.get("classic_name", classic),
                        evidence_type=data.get("evidence_type", ""),
                        observation_dimension=data.get("observation_dimension", ""),
                        original_text=data.get("original_text", "")[:500],
                        chapter=data.get("source_locator", {}).get("chapter", ""),
                        passage_id=data.get("source_locator", {}).get("passage_id", ""),
                        extraction_quality=data.get("extraction_quality", 0.0),
                        authorization_level=data.get("authorization_level", ""),
                        verification_status=data.get("verification_status", "")
                    )
                    
                    self.evidence_list.append(item)
                    
                    # Build indexes
                    etype = item.evidence_type
                    if etype not in self.evidence_by_type:
                        self.evidence_by_type[etype] = []
                    self.evidence_by_type[etype].append(item)
                    
                    cid = item.classic_id
                    if cid not in self.evidence_by_classic:
                        self.evidence_by_classic[cid] = []
                    self.evidence_by_classic[cid].append(item)
                    
                except Exception as e:
                    print(f"  ⚠️ 加载失败 {json_file.name}: {e}")
        
        print(f"  ✅ 已加载 {len(self.evidence_list)} 条证据")
        for cid, items in self.evidence_by_classic.items():
            print(f"     {cid}: {len(items)} 条")

# ============================================================================
# GAP ANALYZER
# ============================================================================

class GapAnalyzer:
    def __init__(self, loader: EvidenceLoader):
        self.loader = loader
        
    def analyze_rule(self, rule: dict) -> RuleGap:
        gaps = RuleGap(
            rule_id=rule["id"],
            rule_name=rule["name"],
            domain=rule["domain"],
            status="PENDING",
            evidence_count=0,
            matched_evidence=[],
            gaps=[],
            recommendation="",
            priority=rule.get("priority", 99)
        )
        
        # 1. 证据类型匹配
        type_matches = []
        for etype in rule.get("evidence_types", []):
            type_matches.extend(self.loader.evidence_by_type.get(etype, []))
        
        # 2. 关键词匹配
        keyword_matches = []
        for ev in self.loader.evidence_list:
            text = ev.original_text + ev.evidence_type + ev.observation_dimension
            score = sum(1 for kw in rule["keywords"] if kw in text)
            if score > 0:
                keyword_matches.append((score, ev))
        
        keyword_matches.sort(key=lambda x: -x[0])
        
        # 3. 合并去重
        seen_ids = set()
        all_matches = []
        
        for _, ev in keyword_matches[:5]:
            if ev.evidence_id not in seen_ids:
                all_matches.append(ev)
                seen_ids.add(ev.evidence_id)
        
        for ev in type_matches:
            if ev.evidence_id not in seen_ids:
                all_matches.append(ev)
                seen_ids.add(ev.evidence_id)
        
        # 4. 评估匹配质量
        for ev in all_matches:
            # 检查经典来源匹配
            classic_match = ev.classic_id in rule.get("expected_evidence", [])
            
            # 计算置信度
            base_confidence = ev.extraction_quality * 0.3
            type_bonus = 0.2 if ev.evidence_type in rule.get("evidence_types", []) else 0
            classic_bonus = 0.3 if classic_match else 0
            
            confidence = min(0.5 + base_confidence + type_bonus + classic_bonus, 0.95)
            
            gaps.matched_evidence.append({
                "evidence_id": ev.evidence_id,
                "classic": ev.classic_name,
                "type": ev.evidence_type,
                "confidence": round(confidence, 2),
                "classic_match": classic_match,
                "text_snippet": ev.original_text[:100] + "..." if len(ev.original_text) > 100 else ev.original_text
            })
            gaps.evidence_count += 1
        
        # 5. 确定状态
        if gaps.evidence_count == 0:
            gaps.status = "PENDING"
            gaps.gaps.append("无直接证据支持")
            if rule["expected_evidence"]:
                gaps.gaps.append(f"期望来自: {', '.join(rule['expected_evidence'])}")
        elif gaps.evidence_count == 1:
            avg_conf = gaps.matched_evidence[0]["confidence"]
            if avg_conf >= 0.85:
                gaps.status = "HIGH"
            elif avg_conf >= 0.7:
                gaps.status = "MEDIUM"
            else:
                gaps.status = "LOW"
            gaps.gaps.append("仅有一条证据，置信度不足")
        else:
            avg_conf = sum(e["confidence"] for e in gaps.matched_evidence) / gaps.evidence_count
            if avg_conf >= 0.85:
                gaps.status = "HIGH"
            elif avg_conf >= 0.7:
                gaps.status = "MEDIUM"
            else:
                gaps.status = "LOW"
        
        # 6. 生成补强建议
        gaps.recommendation = self._generate_recommendation(rule, gaps)
        
        return gaps
    
    def _generate_recommendation(self, rule: dict, gap: RuleGap) -> str:
        if gap.status == "HIGH":
            return "证据充分，可进入 EVIDENCE_VERIFIED 状态"
        elif gap.status == "MEDIUM":
            return "证据基本充分，建议补充更多同类证据"
        elif gap.status == "LOW":
            if rule["expected_evidence"]:
                return f"需从 {', '.join(rule['expected_evidence'])} 补充证据"
            return "需从原典提取证据"
        else:  # PENDING
            if rule.get("priority", 99) >= 5:
                return "低优先级规则，暂不处理"
            elif rule["domain"] == "event":
                return "事件判断规则，延后处理"
            elif rule["id"] in ["PT-009", "PT-010"]:
                return "特殊格局，需严格论证，暂保持 NOT IMPLEMENTED"
            else:
                return "需从原典提取直接证据"

# ============================================================================
# REPORT GENERATOR
# ============================================================================

def generate_report(stats: GapStats, gaps: List[RuleGap]) -> str:
    report = []
    report.append("# Phase B-0.1 Evidence Gap Closure Report")
    report.append("")
    report.append("**任务 ID**: T-ENGINE-BAZI-002 Phase B-0.1")
    report.append("**执行者**: @bot-ziping")
    report.append("**日期**: 2026-09-06")
    report.append("**状态**: ✅ COMPLETED")
    report.append("")
    
    # 执行摘要
    report.append("---")
    report.append("## 执行摘要")
    report.append("")
    report.append("| 指标 | 数值 | 目标 | 差距 |")
    report.append("|------|------|------|------|")
    report.append(f"| 证据覆盖率 | {stats.coverage_rate:.1f}% | ≥90% | {stats.coverage_rate-90:.1f}% |")
    report.append(f"| 高置信规则 | {stats.high_count}/32 | ≥80% | -{(80-stats.high_count/32*100):.1f}% |")
    report.append(f"| 无证据规则 | {stats.pending_count}/32 | ≤10% | +{(stats.pending_count/32*100-10):.1f}% |")
    report.append("")
    
    # 按域统计
    report.append("---")
    report.append("## 按域统计")
    report.append("")
    report.append("| 域 | 总数 | HIGH | MEDIUM | LOW | PENDING |")
    report.append("|-----|------|------|--------|-----|---------|")
    for domain, dstats in stats.by_domain.items():
        report.append(f"| {domain} | {dstats['total']} | {dstats['high']} | {dstats['medium']} | {dstats['low']} | {dstats['pending']} |")
    report.append("")
    
    # 详细规则分析
    report.append("---")
    report.append("## 规则详细分析")
    report.append("")
    
    # 按优先级排序
    sorted_gaps = sorted(gaps, key=lambda g: g.priority)
    
    for gap in sorted_gaps:
        status_emoji = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "PENDING": "🔴"}.get(gap.status, "⚪")
        report.append(f"### {status_emoji} {gap.rule_id}: {gap.rule_name}")
        report.append("")
        report.append(f"- **域**: {gap.domain}")
        report.append(f"- **优先级**: {gap.priority}")
        report.append(f"- **状态**: {gap.status}")
        report.append(f"- **证据数量**: {gap.evidence_count}")
        report.append("")
        
        if gap.matched_evidence:
            report.append("**匹配证据**:")
            report.append("")
            for ev in gap.matched_evidence[:3]:
                report.append(f"- `{ev['evidence_id']}` ({ev['classic']}, 置信度: {ev['confidence']})")
            report.append("")
        
        if gap.gaps:
            report.append("**缺口**:")
            report.append("")
            for g in gap.gaps:
                report.append(f"- {g}")
            report.append("")
        
        report.append(f"**建议**: {gap.recommendation}")
        report.append("")
    
    # 优先级分组
    report.append("---")
    report.append("## 优先级分组处理建议")
    report.append("")
    
    # 第一批：高优先级核心规则
    first_batch = [g for g in gaps if g.priority <= 2 and g.domain in ["wangshuai", "pattern", "yongshen"]]
    report.append("### 第一批：核心规则（优先处理）")
    report.append("")
    for g in first_batch:
        status_icon = "🟢" if g.status in ["HIGH", "MEDIUM"] else "❌"
        report.append(f"{status_icon} {g.rule_id} {g.rule_name} ({g.status})")
    report.append("")
    
    # 第二批：特殊格局
    second_batch = [g for g in gaps if g.rule_id in ["PT-009", "PT-010"]]
    report.append("### 第二批：特殊格局（需谨慎处理）")
    report.append("")
    for g in second_batch:
        report.append(f"- {g.rule_id} {g.rule_name} → 建议保持 NOT IMPLEMENTED")
    report.append("")
    
    # 第三批：十神语义和事件判断
    third_batch = [g for g in gaps if g.domain in ["ten_god_semantics", "event"]]
    report.append("### 第三批：十神语义和事件判断（延后处理）")
    report.append("")
    for g in third_batch:
        report.append(f"- {g.rule_id} {g.rule_name}")
    report.append("")
    
    return "\n".join(report)

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("Phase B-0.1 Evidence Gap Closure")
    print("=" * 80)
    
    # 加载证据
    print("\n[1/3] 加载证据数据库...")
    loader = EvidenceLoader(Path("D:/shuntian/data/evidence"))
    loader.load_all()
    
    if len(loader.evidence_list) == 0:
        print("  ⚠️ 警告: 未加载到任何证据!")
        print("  请检查路径是否正确")
        return
    
    # 分析缺口
    print("\n[2/3] 分析规则缺口...")
    analyzer = GapAnalyzer(loader)
    gaps = []
    
    for rule in RULES:
        gap = analyzer.analyze_rule(rule)
        gaps.append(gap)
        status_emoji = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "PENDING": "🔴"}.get(gap.status, "⚪")
        print(f"  {status_emoji} {gap.rule_id} {gap.rule_name}: {gap.status} ({gap.evidence_count}条证据)")
    
    # 统计
    print("\n[3/3] 生成报告...")
    
    stats = GapStats(
        total_rules=len(gaps),
        high_count=sum(1 for g in gaps if g.status == "HIGH"),
        medium_count=sum(1 for g in gaps if g.status == "MEDIUM"),
        low_count=sum(1 for g in gaps if g.status == "LOW"),
        pending_count=sum(1 for g in gaps if g.status == "PENDING"),
        coverage_rate=(sum(1 for g in gaps if g.status in ["HIGH", "MEDIUM"]) / len(gaps) * 100),
        by_domain={}
    )
    
    # 按域统计
    domain_groups = {}
    for g in gaps:
        if g.domain not in domain_groups:
            domain_groups[g.domain] = {"total": 0, "high": 0, "medium": 0, "low": 0, "pending": 0}
        domain_groups[g.domain]["total"] += 1
        domain_groups[g.domain][g.status.lower()] += 1
    
    stats.by_domain = domain_groups
    
    # 生成报告
    report = generate_report(stats, gaps)
    
    # 保存报告
    output_dir = Path("D:/shuntian/docs/bots/BOT-ZIPING")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / "PHASE_B0_1_EVIDENCE_GAP_CLOSURE_REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    
    # 保存JSON
    json_data = {
        "stats": asdict(stats),
        "gaps": [
            {
                "rule_id": g.rule_id,
                "rule_name": g.rule_name,
                "domain": g.domain,
                "status": g.status,
                "evidence_count": g.evidence_count,
                "matched_evidence": g.matched_evidence,
                "gaps": g.gaps,
                "recommendation": g.recommendation,
                "priority": g.priority
            }
            for g in gaps
        ]
    }
    
    json_path = output_dir / "phase_b0_1_analysis.json"
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"\n  ✅ 报告已保存: {report_path}")
    print(f"  ✅ JSON数据已保存: {json_path}")
    
    return stats, gaps

if __name__ == "__main__":
    stats, gaps = main()
