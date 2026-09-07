"""Phase 3: Update ContextAssembler to consume BAZI-provided fields"""

from pathlib import Path

p = Path('D:/shuntian/src/tongshu/reasoning/context_assembler.py')
content = p.read_text(encoding='utf-8')

# 1. Remove the compute_ten_god import
content = content.replace(
    'from tongshu.reasoning.bazi_ten_gods import ten_god as compute_ten_god\n',
    ''
)

# 2. Remove compute_year_pillar function
import re
content = re.sub(
    r'def compute_year_pillar\(year: int\) -> tuple\[str, str\]:\n    """计算流年干支 \(1984甲子年基准\)\."""\n    base_year = 1984\n    offset = year - base_year\n    stem_idx = offset % 10\n    branch_idx = offset % 12\n    return HEAVENLY_STEMS\[stem_idx\], EARTHLY_BRANCHES\[branch_idx\]\n\n\n',
    '',
    content
)

# 3. Update assemble_natal_context to consume chart fields
# Replace stem_ten_god computation with direct field access
content = content.replace(
    'stem_ten_god=compute_ten_god(chart.day_master, chart.year_pillar.heavenly_stem),',
    'stem_ten_god=chart.year_pillar.stem_ten_god,'
)
content = content.replace(
    'stem_ten_god=compute_ten_god(chart.day_master, chart.month_pillar.heavenly_stem),',
    'stem_ten_god=chart.month_pillar.stem_ten_god,'
)
content = content.replace(
    'stem_ten_god="DAY_MASTER",',
    'stem_ten_god=chart.day_pillar.stem_ten_god,'
)
content = content.replace(
    'stem_ten_god=compute_ten_god(chart.day_master, chart.hour_pillar.heavenly_stem),',
    'stem_ten_god=chart.hour_pillar.stem_ten_god,'
)

# 4. Replace branch relation calculation with direct field access
old_branch_calc = '''        # 地支关系
        branch_clashes = []
        branch_combinations = []
        branch_harms = []
        branch_punishments = []
        branch_three_combinations = []

        for i, b1 in enumerate(branches):
            for j, b2 in enumerate(branches):
                if i >= j:
                    continue
                pair = f"{b1}-{b2}"
                if BRANCH_CLASH.get(b1) == b2:
                    branch_clashes.append(pair)
                if BRANCH_COMBINATION.get(b1) == b2:
                    branch_combinations.append(pair)
                if BRANCH_HARM.get(b1) == b2:
                    branch_harms.append(pair)

        # 三合
        for combo in set(THREE_COMBINATION.values()):
            if all(b in branches for b in combo):
                branch_three_combinations.append("-".join(combo))'''

new_branch_calc = '''        # 地支关系：直接消费 BAZI 字段
        branch_clashes = list(chart.branch_clash_map.keys())
        branch_combinations = list(chart.branch_he_map.keys())
        branch_harms = list(chart.branch_harm_map.keys())
        branch_punishments = []  # TODO: add branch_sanxing_map to BAZI
        branch_three_combinations = list(chart.branch_sanhe_map.keys())'''

content = content.replace(old_branch_calc, new_branch_calc)

# 5. Update assemble_dayun_context to consume chart.luck_pillars
# First, remove the old implementation and replace with simplified version
old_dayun_impl = '''    def assemble_dayun_context(self, chart, natal: NatalContext, target_year: int) -> DaYunContext:
        """组装DaYunContext."""
        # 自己计算大运 (不依赖chart.luck_pillars数量)
        # 阳男阴女顺排, 阴男阳女逆排
        year_stem = natal.pillars[0].heavenly_stem  # 年干
        is_yang_year = STEM_NUMBER[year_stem] % 2 == 1  # 阳年
        is_male = natal.gender == "male"

        # 顺排: 阳男/阴女; 逆排: 阴男/阳女
        is_forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

        # 从月柱开始
        month_stem = natal.pillars[1].heavenly_stem
        month_branch = natal.pillars[1].earthly_branch
        month_stem_idx = HEAVENLY_STEMS.index(month_stem)
        month_branch_idx = EARTHLY_BRANCHES.index(month_branch)

        start_age = getattr(chart, 'start_age', 0.0)

        # 计算12个大运 (覆盖到120岁, 避免target_year超出范围)
        da_yun_pillars = []
        for i in range(12):
            if is_forward:
                stem_idx = (month_stem_idx + 1 + i) % 10
                branch_idx = (month_branch_idx + 1 + i) % 12
            else:
                stem_idx = (month_stem_idx - 1 - i) % 10
                branch_idx = (month_branch_idx - 1 - i) % 12

            stem = HEAVENLY_STEMS[stem_idx]
            branch = EARTHLY_BRANCHES[branch_idx]

            pillar_start_age = start_age + i * 10
            pillar_end_age = pillar_start_age + 10
            pillar_start_year = natal.birth_year + int(pillar_start_age)
            pillar_end_year = natal.birth_year + int(pillar_end_age)

            is_current = pillar_start_year <= target_year < pillar_end_year

            da_yun_pillars.append(DaYunPillar(
                index=i,
                heavenly_stem=stem,
                earthly_branch=branch,
                start_age=pillar_start_age,
                end_age=pillar_end_age,
                start_year=pillar_start_year,
                end_year=pillar_end_year,
                stem_ten_god=compute_ten_god(natal.day_master, stem),
                is_current=is_current,
            ))'''

new_dayun_impl = '''    def assemble_dayun_context(self, chart, natal: NatalContext, target_year: int) -> DaYunContext:
        """组装DaYunContext - 消费 BAZI 已有大运列表."""
        start_age = getattr(chart, 'start_age', 0.0)

        # 消费 BAZI 已有大运列表 (不重新计算)
        da_yun_pillars = []
        for luck in chart.luck_pillars:
            pillar_start_age = luck.start_age if hasattr(luck, 'start_age') else start_age + da_yun_pillars.__len__() * 10
            pillar_end_age = luck.end_age if hasattr(luck, 'end_age') else pillar_start_age + 10
            pillar_start_year = natal.birth_year + int(pillar_start_age)
            pillar_end_year = natal.birth_year + int(pillar_end_age)
            is_current = pillar_start_year <= target_year < pillar_end_year

            da_yun_pillars.append(DaYunPillar(
                index=len(da_yun_pillars),
                heavenly_stem=luck.heavenly_stem,
                earthly_branch=luck.earthly_branch,
                start_age=pillar_start_age,
                end_age=pillar_end_age,
                start_year=pillar_start_year,
                end_year=pillar_end_year,
                stem_ten_god=getattr(luck, 'stem_ten_god', ''),  # 消费 BAZI 字段
                is_current=is_current,
            ))'''

content = content.replace(old_dayun_impl, new_dayun_impl)

# 6. Update assemble_year_context to not use compute_year_pillar
old_year_start = '''    def assemble_year_context(self, natal: NatalContext, dayun: DaYunContext,
                               target_year: int) -> YearContext:
        """组装YearContext."""
        year_stem, year_branch = compute_year_pillar(target_year)
        year_stem_ten_god = compute_ten_god(natal.day_master, year_stem)'''

new_year_start = '''    def assemble_year_context(self, natal: NatalContext, dayun: DaYunContext,
                               target_year: int) -> YearContext:
        """组装YearContext - 流年干支由 TimeEngine 提供，此处仅消费."""
        # TODO: 从 TemporalContext 获取流年干支
        # 当前使用简化计算作为临时方案，等待 Phase 2 (Temporal Engine)
        year_stem, year_branch = self._compute_year_pillar_temp(target_year)
        year_stem_ten_god = self._compute_ten_god_temp(natal.day_master, year_stem)'''

content = content.replace(old_year_start, new_year_start)

# 7. Add temporary helper functions for year pillar and ten god calculation
# These will be replaced when TemporalEngine is ready
temp_helpers = '''
    def _compute_year_pillar_temp(self, year: int) -> tuple[str, str]:
        """临时：计算流年干支。等待 TemporalEngine 集成后删除."""
        from tongshu.reasoning.bazi_ten_gods import HEAVENLY_STEMS, EARTHLY_BRANCHES
        base_year = 1984
        offset = year - base_year
        stem_idx = offset % 10
        branch_idx = offset % 12
        return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

    def _compute_ten_god_temp(self, day_master: str, stem: str) -> str:
        """临时：计算十神。等待 BAZI Chart 提供后删除."""
        from tongshu.reasoning.bazi_ten_gods import ten_god
        return ten_god(day_master, stem)

'''

# Insert after class definition
class_start = content.find('class ContextAssembler:')
if class_start > 0:
    # Find the __init__ method
    init_end = content.find('def assemble_natal_context', class_start)
    if init_end > 0:
        content = content[:init_end] + temp_helpers + content[init_end:]

# Write back
p.write_text(content, encoding='utf-8')
print("Phase 3: ContextAssembler updated to consume BAZI fields")
