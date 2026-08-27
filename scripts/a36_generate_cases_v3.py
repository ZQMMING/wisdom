#!/usr/bin/env python3
"""重新生成 40 个带完整解释的 case 文件（用于 AI Expert Rating）。"""
import sys
import json
from pathlib import Path
from datetime import date
import random

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.pipeline import TONGSHUPipeline
from tongshu.canonical.composer import CanonicalComposer

REPO_ROOT = Path(__file__).parent.parent.parent  # D:/today

# Use pipeline's internal compose (no manual instantiation needed)
_pipeline = TONGSHUPipeline.for_demo(REPO_ROOT)
_stage = _pipeline.compute_stage
_stage.composer = CanonicalComposer(
    theme="WORK",
    engine_versions={"bazi": "1.0.0", "ziwei": "1.0.0", "rules": "1.0.0", "reasoning": "1.0.0"},
)


def run_case(year, month, day, hour, gender, analysis_date_str="2026-01-15"):
    """Run one case and return structured result."""
    hour_map = {
        "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
        "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11,
    }
    h = hour_map.get(hour, 0)
    # Map to 24-hour range for birth_date tuple
    # bazi uses hour index directly
    result = _stage.run(
        analysis_date=date(2026, 1, 15),
        birth_date=(year, month, day, h),
        gender=gender,
        theme="WORK",
        request_id=f"RR-RATING-{year}{month}{day}",
        trace_id=f"TRACE-RATING-{year}{month}{day}",
    )
    return result


def format_bazi(result):
    """Format bazi four pillars."""
    if not hasattr(result, 'bazi_chart') or result.bazi_chart is None:
        return "无八字结果"
    b = result.bazi_chart
    try:
        yp = getattr(b, 'year_pillar', None)
        mp = getattr(b, 'month_pillar', None)
        dp = getattr(b, 'day_pillar', None)
        hp = getattr(b, 'hour_pillar', None)
        pillars = [str(p) for p in (yp, mp, dp, hp) if p is not None]
        return f"- 年柱: {pillars[0] if len(pillars)>0 else '?'}\n- 月柱: {pillars[1] if len(pillars)>1 else '?'}\n- 日柱: {pillars[2] if len(pillars)>2 else '?'}\n- 时柱: {pillars[3] if len(pillars)>3 else '?'}"
    except Exception:
        return "无八字结果"


def format_heluo(result):
    """Format heluo result."""
    if not result.heluo_result:
        return "- 无河洛结果"
    h = result.heluo_result
    lines = []
    lines.append(f"- **先天卦**: {h.prenatal.hexagram_name or '?' }（上卦{h.prenatal.upper_gua}, 下卦{h.prenatal.lower_gua}）")
    lines.append(f"- **后天卦**: {h.postnatal.hexagram_name or '?' }（上卦{h.postnatal.upper_gua}, 下卦{h.postnatal.lower_gua}）")
    lines.append(f"- **元堂**: {h.yuantang.yuantang or '?' }")
    if hasattr(h, 'numbers') and h.numbers:
        lines.append(f"- 天数: {h.numbers.tian_shu}（化简: {h.numbers.tian_reduced}）")
        lines.append(f"- 地数: {h.numbers.di_shu}（化简: {h.numbers.di_reduced}）")
    return "\n".join(lines)


def format_yi(result):
    """Format yi interpretation."""
    if not result.yi_interpretation:
        return "- 无易经解释"
    yi = result.yi_interpretation
    lines = []
    lines.append("### 易经解释")
    lines.append(f"- **状态**: {yi.state or '无'}")
    if yi.opportunity:
        lines.append(f"- **机会**: {yi.opportunity}")
    if yi.risk:
        lines.append(f"- **风险**: {yi.risk}")
    if yi.remediation:
        lines.append(f"- **建议**: {yi.remediation}")
    if yi.action:
        lines.append(f"- **行动**: {yi.action}")
    lines.append(f"- **方向**: {yi.directional_label.value if hasattr(yi.directional_label, 'value') else str(yi.directional_label)}")
    lines.append(f"- **来源**: {', '.join(yi.source_refs) if yi.source_refs else '无'}")
    lines.append(f"- **置信度**: {yi.confidence}")
    return "\n".join(lines)


def build_blind_md(case_id, year, month, day, hour, gender):
    """Build blind evaluation markdown for one case."""
    try:
        result = run_case(year, month, day, hour, gender)
    except Exception as e:
        # Fallback: create minimal result
        print(f"  WARNING: Case {case_id} failed: {e}", file=sys.stderr)
        result = None

    bazi_text = format_bazi(result) if result else "- 无八字结果"
    heluo_text = format_heluo(result) if result else "- 无河洛结果"
    yi_text = format_yi(result) if result else "- 无易经解释"

    content = f"""# {case_id} — Blind Evaluation (v3)

## 人物基本信息

- **人物ID**: PB-{int(year) % 100:02d}{int(month):02d}{int(day):02d}
- **性别**: {'男' if gender == 'male' else '女'}
- **出生年**: {year}
- **出生月**: {month}
- **出生日**: {day}
- **出生时**: {hour}

## 系统输入

```json
{{
  "birth_info": {{
    "year": {year},
    "month": {month},
    "day": {day},
    "hour": "{hour}",
    "gender": "{gender}"
  }}
}}
```

## 系统原始输出

### 八字四柱

{bazi_text}

### 河洛卦象

{heluo_text}

### 天地数

"""
    if result and result.heluo_result and result.heluo_result.numbers:
        n = result.heluo_result.numbers
        content += f"- 天数: {n.tian_shu}（化简: {n.tian_reduced}）\n- 地数: {n.di_shu}（化简: {n.di_reduced}）\n\n"
    else:
        content += "- 无数据\n\n"

    content += """### 计算细节

"""
    if result and result.heluo_result and result.heluo_result.numbers and result.heluo_result.numbers.details:
        for detail in result.heluo_result.numbers.details[:4]:
            content += f"{detail}\n"
    content += "\n---\n\n"
    content += yi_text
    content += """

---


## 评分任务

你是「顺天 V1.3 Accuracy Validation」项目的独立专家评价员。

你的唯一任务是：在严格的盲评条件下，根据预先冻结的评价标准，对「顺天系统生成的关系式解释」进行专家级质量评价。

### 最重要的原则

1. 评价系统，不重新计算系统 — 不得自行重新计算八字/河洛/紫微
2. 评价关系，不评价语言漂亮程度
3. 历史事实不能自动证明预测正确
4. 禁止事后合理化 — 宽泛语言适配大量事件不得视为高质量
5. 证据不足时必须使用 NOT_EVALUABLE

### 评分维度 (0-3 分)

| 维度 | 3 (STRONG) | 2 (ACCEPTABLE) | 1 (WEAK) | 0 (FAIL) |
|------|-----------|---------------|---------|---------|
| Temporal Alignment | 时间关系清晰，集中于目标窗口 | 基本对应，时间边界较宽 | 时间对应较弱，明显泛化 | 无法建立时间对应 |
| Event Correspondence | 对事件类型及性质有明确对应 | 存在合理对应，不够具体 | 只能通过宽泛解释勉强对应 | 无合理对应 |
| Relational Coherence | 关系结构高度一致 | 基本一致，轻微缺口 | 关系链存在明显断裂 | 自相矛盾或无法成立 |
| Evidence Support | 核心判断均有明确证据支持 | 大部分判断有证据支持 | 证据薄弱或存在明显跳跃 | 核心结论基本没有证据支持 |
| Directionality | 方向明确且证据充分 | 基本合理 | 方向模糊或存在明显冲突 | 方向与证据明显相反 |
| Specificity | 高度具体，具有明显约束力 | 有一定具体性 | 高度泛化 | 几乎完全属于通用套话 |
| Overall Interpretability | 整体解释成熟、连贯、可审计 | 基本成立，存在明显不足 | 解释零散或逻辑薄弱 | 无法形成有效解释 |

### 输出格式

必须严格输出 JSON，不得输出 Markdown 或额外解释：

```json
{
  "case_id": "...",
  "evaluable": true,
  "dimensions": {
    "temporal_alignment": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "event_correspondence": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "relational_coherence": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "evidence_support": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "directionality": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "specificity": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "overall_interpretability": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."}
  },
  "strengths": [...],
  "weaknesses": [...],
  "contradictions": [...],
  "unsupported_claims": [...],
  "overall_assessment": "...",
  "confidence": "HIGH|MEDIUM|LOW"
}
```

### 禁止行为

- 不得因为相信/不相信命理而评分
- 不得因为系统使用传统术语而加分
- 不得因为语言优美/冗长而加分
- 不得因为"看起来很准"而直接加分
- 不得使用事后已知信息反向修改评分标准
- 不得为系统寻找合理化解释或制造缺失证据
- 不得自己重新计算系统结果并将其作为 Ground Truth


---

**禁止信息**: 本文件不包含 Ground Truth、其他 Rater 评分、系统内部计算链、系统 confidence 值。
"""
    return content


def main():
    out_dir = Path(__file__).parent.parent / "dataset" / "accuracy" / "expert_pilot" / "cases_v3"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 40 cases with diverse birth data
    cases = [
        (1960, 5, 29, "亥", "male"),
        (1975, 3, 15, "子", "female"),
        (1982, 8, 22, "午", "male"),
        (1990, 1, 8, "辰", "female"),
        (1988, 11, 3, "卯", "male"),
        (1978, 6, 17, "巳", "female"),
        (1995, 9, 25, "申", "male"),
        (1965, 4, 12, "酉", "female"),
        (1983, 7, 30, "寅", "male"),
        (1972, 12, 5, "戌", "female"),
        (1991, 2, 18, "亥", "male"),
        (1986, 10, 9, "子", "female"),
        (1979, 5, 23, "午", "male"),
        (1994, 8, 7, "辰", "female"),
        (1968, 3, 31, "巳", "male"),
        (1985, 11, 14, "卯", "female"),
        (1973, 6, 28, "申", "male"),
        (1992, 1, 20, "酉", "female"),
        (1980, 9, 3, "寅", "male"),
        (1987, 4, 16, "戌", "female"),
        (1963, 7, 8, "亥", "male"),
        (1996, 12, 22, "子", "female"),
        (1976, 2, 11, "午", "male"),
        (1984, 10, 5, "辰", "female"),
        (1969, 5, 19, "巳", "male"),
        (1993, 8, 1, "卯", "female"),
        (1977, 3, 24, "申", "male"),
        (1981, 11, 12, "酉", "female"),
        (1966, 6, 6, "寅", "male"),
        (1997, 1, 30, "戌", "female"),
        (1974, 9, 18, "亥", "male"),
        (1989, 4, 2, "子", "female"),
        (1962, 7, 25, "午", "male"),
        (1998, 12, 10, "辰", "female"),
        (1971, 2, 28, "巳", "male"),
        (1988, 10, 15, "卯", "female"),
        (1964, 5, 8, "申", "male"),
        (1995, 8, 21, "酉", "female"),
        (1970, 3, 14, "寅", "male"),
        (1987, 11, 27, "戌", "female"),
    ]

    print(f"Generating {len(cases)} cases to: {out_dir}")
    for i, (y, m, d, h, g) in enumerate(cases, 1):
        case_id = f"SAMPLE_{i:03d}"
        print(f"  [{i:2d}/{len(cases)}] {case_id}...", end=" ")
        md = build_blind_md(case_id, y, m, d, h, g)
        path = out_dir / f"{case_id}_BLIND.md"
        path.write_text(md, encoding="utf-8")
        print(f"OK ({len(md)} chars)")

    print(f"\nDone! {len(cases)} cases saved to {out_dir}")


if __name__ == "__main__":
    main()
