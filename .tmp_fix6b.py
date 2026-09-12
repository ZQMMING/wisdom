# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_judgment.py"
src = io.open(p, encoding="utf-8").read()

# ── 修6b：官贵事件新增 DAMAGED / ROBBED 分支 ──
old = """        elif os_ == 'UNCONTROLLED':
            # OFF-001 官杀无制→官非候选（事实吉凶候选，非现代语言断语）
            # 状态机：无反局=仅 CANDIDATE（候选）；反局（FAN_JU）=官非落实 ESTABLISHED
            fan_ju = getattr(blind_result, 'zheng_fan_ju', None) == 'FAN_JU'
            evts.append(self._make_event(
                'OFFICIAL', 'OFFICIAL_OFFENSE_CANDIDATE', JDGDirection.IN_AUSPICIOUS,
                f"officer_present=True+controlled=False（官杀无制）+反局={fan_ju}",
                ['EVT-OFFICIAL-001', 'JDG-OFFICIAL-003', 'OFF-001'], ['BLIND-DJ-001'],
                'month', 'officer', 'EVT-OFFICIAL-001', None,
                status=JdgStatus.ESTABLISHED if fan_ju else JdgStatus.CANDIDATE))
            rules.append('JDG-OFFICIAL-003')
"""
new = """        elif os_ == 'DAMAGED':
            # V3.4.3：穿官=损官（官根受损，官场梦碎；非官非，非官贵）
            evts.append(self._make_event(
                'OFFICIAL', 'OFFICIAL_DAMAGED', JDGDirection.IN_AUSPICIOUS,
                f"official_state=DAMAGED（穿官损官，官根受损）",
                ['EVT-OFFICIAL-001', 'JDG-OFFICIAL-004'], ['BLIND-DJ-010'],
                'month', 'officer', 'EVT-OFFICIAL-001', None))
            rules.append('JDG-OFFICIAL-004')
        elif os_ == 'ROBBED':
            # V3.4.3：官被劫财合走（非我所有，做功无效）
            evts.append(self._make_event(
                'OFFICIAL', 'OFFICIAL_ROBBED', JDGDirection.NEUTRAL,
                f"official_state=ROBBED（官星被劫财合走，非我所有）",
                ['EVT-OFFICIAL-001', 'JDG-OFFICIAL-005'], ['BLIND-DJ-011'],
                'month', 'officer', 'EVT-OFFICIAL-001', None))
            rules.append('JDG-OFFICIAL-005')
        elif os_ == 'UNCONTROLLED':
            # OFF-001 官杀无制→官非候选（事实吉凶候选，非现代语言断语）
            # 状态机：无反局=仅 CANDIDATE（候选）；反局（FAN_JU）=官非落实 ESTABLISHED
            fan_ju = getattr(blind_result, 'zheng_fan_ju', None) == 'FAN_JU'
            evts.append(self._make_event(
                'OFFICIAL', 'OFFICIAL_OFFENSE_CANDIDATE', JDGDirection.IN_AUSPICIOUS,
                f"officer_present=True+controlled=False（官杀无制）+反局={fan_ju}",
                ['EVT-OFFICIAL-001', 'JDG-OFFICIAL-003', 'OFF-001'], ['BLIND-DJ-001'],
                'month', 'officer', 'EVT-OFFICIAL-001', None,
                status=JdgStatus.ESTABLISHED if fan_ju else JdgStatus.CANDIDATE))
            rules.append('JDG-OFFICIAL-003')
"""
assert old in src, "官非分支OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 官非DAMAGED/ROBBED分支 已加")
