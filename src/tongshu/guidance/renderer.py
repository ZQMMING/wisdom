"""P5-C Renderer - 指引渲染器.

将ComposedGuidance渲染为用户可读的自然语言.

硬契约(4条红线):
  1. Renderer不得重新计算 - 只渲染已有的ComposedGuidance
  2. 不得改变direction - 只用"有利条件"/"需要注意"/"无明显偏移"
  3. 不得新增输入中不存在的断言 - 所有内容来自ComposedGuidance
  4. 不引入AI自由推理 - 第一版deterministic/template-first

渲染规则:
  - 必须保留opportunity/caution/action/avoid的区别
  - 不得增加"必然""一定""注定"等确定性预测
  - 不得引用未经提供的命理规则
  - 输出格式: 结构化文本(Markdown), 包含总体概述/各维度详情/优先级行动
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from .composer import ComposedGuidance, DomainGuidance
from .guidance_atom import GuidanceAtom, FORBIDDEN_TERMS

log = logging.getLogger(__name__)


class GuidanceRenderer:
    """指引渲染器 - 将ComposedGuidance渲染为用户可读的自然语言.

    硬契约:
      - 不重新计算, 只渲染已有数据
      - 不改变direction
      - 不新增断言
      - 不引入AI自由推理(deterministic/template-first)
    """

    def __init__(self):
        self._forbidden_terms = FORBIDDEN_TERMS

    def render_markdown(self, composed: ComposedGuidance) -> str:
        """渲染为Markdown格式.

        Args:
            composed: ComposedGuidance

        Returns:
            Markdown文本
        """
        sections = []

        # 1. 标题
        sections.append(self._render_title(composed))

        # 2. 总体概述
        sections.append(self._render_overall_summary(composed))

        # 3. 关键主题
        sections.append(self._render_key_themes(composed))

        # 4. 各维度详情
        sections.append(self._render_domains(composed))

        # 5. 优先级行动建议
        sections.append(self._render_priorities(composed))

        # 6. 说明(可追溯)
        sections.append(self._render_disclaimer(composed))

        return "\n\n".join(sections)

    def render_text(self, composed: ComposedGuidance) -> str:
        """渲染为纯文本格式."""
        # 简单去除Markdown标记
        md = self.render_markdown(composed)
        text = md.replace("### ", "").replace("## ", "").replace("# ", "")
        text = text.replace("**", "").replace("*", "")
        text = text.replace("- ", "• ")
        return text

    def render_structured(self, composed: ComposedGuidance) -> dict:
        """渲染为结构化JSON(供API使用)."""
        return {
            "title": f"个人结构分析与行动指引",
            "overall_summary": composed.overall_summary,
            "key_themes": composed.key_themes,
            "domains": [
                {
                    "domain": dg.domain,
                    "domain_label": dg.domain_label,
                    "top_theme": dg.top_theme,
                    "direction_summary": dg.direction_summary,
                    "guidance_items": [
                        {
                            "theme": atom.theme,
                            "direction": atom.direction_label,
                            "intensity": atom.intensity,
                            "opportunities": atom.opportunities,
                            "cautions": atom.cautions,
                            "actions": atom.actions,
                            "avoid": atom.avoid,
                        }
                        for atom in dg.atoms
                    ],
                }
                for dg in composed.domains
            ],
            "priorities": composed.priorities,
            "meta": {
                "case_id": composed.case_id,
                "direction_distribution": composed.direction_distribution,
                "source_engines": composed.source_engines,
                "guidance_atom_count": len(composed.source_guidance_ids),
                "assertion_count": len(composed.source_assertion_ids),
                "status": composed.status,
            },
        }

    def _render_title(self, composed: ComposedGuidance) -> str:
        """渲染标题."""
        return "# 个人结构分析与行动指引"

    def _render_overall_summary(self, composed: ComposedGuidance) -> str:
        """渲染总体概述."""
        lines = ["## 总体概述", ""]
        lines.append(composed.overall_summary)
        return "\n".join(lines)

    def _render_key_themes(self, composed: ComposedGuidance) -> str:
        """渲染关键主题."""
        if not composed.key_themes:
            return ""
        lines = ["## 关键主题", ""]
        for i, theme in enumerate(composed.key_themes, 1):
            lines.append(f"{i}. {theme}")
        return "\n".join(lines)

    def _render_domains(self, composed: ComposedGuidance) -> str:
        """渲染各维度详情."""
        sections = ["## 各维度详情"]

        for dg in composed.domains:
            sections.append("")
            sections.append(f"### {dg.domain_label}")
            sections.append("")

            # direction摘要
            if dg.direction_summary:
                dir_parts = [f"{k} {v}项" for k, v in dg.direction_summary.items()]
                sections.append(f"**方向分布**：{'，'.join(dir_parts)}")
                sections.append("")

            # 每个guidance atom
            for atom in dg.atoms:
                sections.append(f"#### {atom.theme}")
                sections.append("")
                sections.append(f"**方向**：{atom.direction_label}（强度 {atom.intensity}/100）")
                sections.append("")

                if atom.opportunities:
                    sections.append("**可利用的机会**：")
                    for opp in atom.opportunities:
                        sections.append(f"- {opp}")
                    sections.append("")

                if atom.cautions:
                    sections.append("**需要注意**：")
                    for cau in atom.cautions:
                        sections.append(f"- {cau}")
                    sections.append("")

                if atom.actions:
                    sections.append("**建议行动**：")
                    for act in atom.actions:
                        sections.append(f"- {act}")
                    sections.append("")

                if atom.avoid:
                    sections.append("**建议避免**：")
                    for avd in atom.avoid:
                        sections.append(f"- {avd}")
                    sections.append("")

        return "\n".join(sections)

    def _render_priorities(self, composed: ComposedGuidance) -> str:
        """渲染优先级行动建议."""
        if not composed.priorities:
            return ""

        sections = ["## 优先级行动建议", ""]

        # 按type分组
        actions = [p for p in composed.priorities if p["type"] == "action"]
        avoids = [p for p in composed.priorities if p["type"] == "avoid"]

        if actions:
            sections.append("### 建议优先执行")
            sections.append("")
            for i, p in enumerate(actions[:10], 1):  # 最多显示10条
                sections.append(f"{i}. **{p['domain']}**（{p['theme']}，{p['direction']}）：{p['content']}")
            sections.append("")

        if avoids:
            sections.append("### 建议优先避免")
            sections.append("")
            for i, p in enumerate(avoids[:10], 1):  # 最多显示10条
                sections.append(f"{i}. **{p['domain']}**（{p['theme']}，{p['direction']}）：{p['content']}")
            sections.append("")

        return "\n".join(sections)

    def _render_disclaimer(self, composed: ComposedGuidance) -> str:
        """渲染说明(可追溯)."""
        lines = ["---", ""]
        lines.append("**说明**：")
        lines.append("- 以上为基于传统命理体系的结构性分析，非科学预测。")
        lines.append("- 健康维度仅为生活节奏提醒，不构成医疗诊断或建议。")
        lines.append("- 所有判断均可追溯至计算引擎的原始证据，不包含AI自由推理。")
        lines.append(f"- 分析涵盖 {len(composed.source_engines)} 个计算引擎的互补证据。")
        return "\n".join(lines)

    def validate_render(self, text: str) -> list[str]:
        """验证渲染结果不包含禁止术语."""
        violations = []
        for term in self._forbidden_terms:
            if term in text:
                violations.append(f"渲染结果包含禁止术语: {term}")
        return violations
