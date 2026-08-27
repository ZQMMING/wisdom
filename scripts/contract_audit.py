"""
Architecture Freeze V1.0 — Contract 符合性审计
验证所有6个冻结契约是否已正确实现
"""

import sys
import inspect
from pathlib import Path
from datetime import date, time

sys.path.insert(0, str(Path("src").absolute()))


# ============================================================================
# Contract 1: Profile Contract 验证
# ============================================================================
def validate_profile_contract():
    results = []
    
    # 1.1 检查 Gender 是否 REQUIRED 且禁止默认值
    try:
        from tongshu.engines.heluo.input import HeluoInput
        sig = inspect.signature(HeluoInput)
        gender_param = sig.parameters.get('gender')
        
        if gender_param is None:
            results.append(("C1.1", "FAIL", "HeluoInput 缺少 gender 字段"))
        elif gender_param.default is not inspect.Parameter.empty:
            results.append(("C1.1", "FAIL", f"gender 有默认值: {gender_param.default}（违反 forbidden_default）"))
        else:
            results.append(("C1.1", "PASS", "gender 为 REQUIRED，无默认值"))
    except Exception as e:
        results.append(("C1.1", "ERROR", str(e)))
    
    # 1.2 检查 Profile Gate 三态（路径: src/tongshu/api/profile.py）
    try:
        from tongshu.api.profile import ProfileStatus
        statuses = [s.value for s in ProfileStatus if s.value in ("NONE", "INSUFFICIENT", "VALID", "PROFILE_CALCULATION_READY")]
        required = {"NONE", "INSUFFICIENT", "VALID"}
        if required.issubset(set(statuses)):
            results.append(("C1.2", "PASS", f"Profile Gate 三态完整: {[s for s in statuses if s in required]}"))
        else:
            results.append(("C1.2", "FAIL", f"缺失状态: {required - set(statuses)}"))
    except Exception as e:
        results.append(("C1.2", "ERROR", str(e)))
    
    # 1.3 检查 CalculationContext → SubjectContext 包含 gender
    try:
        from tongshu.engines.time.calculation_context import CalculationContext, SubjectContext
        # 正确路径: CalculationContext.subject 是 SubjectContext 类型，SubjectContext.gender 存在
        if hasattr(SubjectContext, '__dataclass_fields__') and 'gender' in SubjectContext.__dataclass_fields__:
            results.append(("C1.3", "PASS", "CalculationContext.subject.gender 存在（通过 SubjectContext）"))
        else:
            results.append(("C1.3", "FAIL", f"SubjectContext 缺少 gender，实际字段: {list(SubjectContext.__dataclass_fields__.keys())}"))
    except Exception as e:
        results.append(("C1.3", "ERROR", str(e)))
    
    # 1.4 检查 signal_engine.build_signals 强制 gender
    try:
        from tongshu.reasoning.signal_engine import build_signals
        sig = inspect.signature(build_signals)
        gender_param = sig.parameters.get('gender')
        if gender_param is None or gender_param.default is not inspect.Parameter.empty:
            results.append(("C1.4", "FAIL", f"build_signals gender 参数异常: {gender_param}"))
        else:
            results.append(("C1.4", "PASS", "signal_engine.build_signals gender 为 REQUIRED"))
    except Exception as e:
        results.append(("C1.4", "ERROR", str(e)))
    
    return results


# ============================================================================
# Contract 2: Heluo Engine 8模块签名 验证
# ============================================================================
def validate_heluo_engine():
    results = []
    
    modules = {
        "input": ("prepare_heluo_input",),
        "numbers": ("compute_tian_di_shu", "normalize_tian_shu", "normalize_di_shu"),
        "prenatal": ("determine_prenatal_hexagram", "resolve_middle_palace"),
        "yuan_tang": ("find_yuantang",),
        "postnatal": ("compute_postnatal",),
        "temporal": ("compute_timeline", "compute_daily_hexagram"),
        "hexagram": ("analyze_hexagram", "compute_ti_yong", "compute_cheng_cheng_bi_ying"),
        "canonical": ("HeluoCanonical",),
    }
    
    for mod_name, expected_funcs in modules.items():
        try:
            mod = __import__(f"tongshu.engines.heluo.{mod_name}", fromlist=[""])
            results.append((f"C2.{mod_name}", "PASS", f"模块 {mod_name}.py 已加载"))
            
            for func_name in expected_funcs:
                if hasattr(mod, func_name):
                    results.append((f"C2.{mod_name}.{func_name}", "PASS", f"{func_name} 存在"))
                else:
                    results.append((f"C2.{mod_name}.{func_name}", "FAIL", f"{func_name} 缺失"))
        except Exception as e:
            results.append((f"C2.{mod_name}", "ERROR", str(e)))
    
    # 验证 golden case
    try:
        from tongshu.engines.heluo import HeluoCanonical
        canonical = HeluoCanonical()
        if canonical.verify_golden_case("jixiaolan"):
            results.append(("C2.golden", "PASS", "纪晓岚 Golden Case 通过"))
        else:
            results.append(("C2.golden", "FAIL", "纪晓岚 Golden Case 失败"))
    except Exception as e:
        results.append(("C2.golden", "ERROR", str(e)))
    
    return results


# ============================================================================
# Contract 3: Yi Engine 4层 验证
# ============================================================================
def validate_yi_engine():
    results = []
    
    layers = {
        "hexagram_symbol": ("get_hexagram_symbol", "get_ti_yong_relation"),
        "line_symbol": ("analyze_line_symbol", "check_dang_wei", "check_zhong", "compute_cheng_cheng_bi_ying"),
        "classical_text": ("get_classical_text", "get_yao_ci"),
        "image_expansion": ("expand_image", "validate_image_chain"),
        "relational_interpretation": ("relational_interpretation",),
    }
    
    for layer_name, expected_funcs in layers.items():
        try:
            mod = __import__(f"tongshu.engines.yi.{layer_name}", fromlist=[""])
            results.append((f"C3.{layer_name}", "PASS", f"层 {layer_name} 已加载"))
            
            for func_name in expected_funcs:
                if hasattr(mod, func_name):
                    results.append((f"C3.{layer_name}.{func_name}", "PASS", f"{func_name} 存在"))
                else:
                    results.append((f"C3.{layer_name}.{func_name}", "FAIL", f"{func_name} 缺失"))
        except Exception as e:
            results.append((f"C3.{layer_name}", "ERROR", str(e)))
    
    return results


# ============================================================================
# Contract 4: Calculation Snapshot 验证
# ============================================================================
def validate_snapshot():
    results = []
    
    try:
        from tongshu.engines.snapshot.models import CalculationSnapshot
        fields = CalculationSnapshot.__dataclass_fields__
        required = {"snapshot_id", "user_id", "calculation_timestamp", "heluo_result"}
        present = set(fields.keys())
        if required.issubset(present):
            results.append(("C4.snapshot", "PASS", f"CalculationSnapshot 字段完整: {sorted(required & present)}"))
        else:
            results.append(("C4.snapshot", "FAIL", f"缺失字段: {required - present}"))
    except Exception as e:
        results.append(("C4.snapshot", "ERROR", str(e)))
    
    try:
        from tongshu.engines.snapshot.manager import SnapshotManager
        results.append(("C4.writer", "PASS", "SnapshotManager 已加载"))
    except Exception as e:
        results.append(("C4.writer", "ERROR", str(e)))
    
    return results


# ============================================================================
# Contract 5: API Contract 验证
# ============================================================================
def validate_api_contract():
    results = []
    
    try:
        from tongshu.api.app import app
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        required_paths = ["/today", "/profile", "/nfc"]
        for path in required_paths:
            if any(path in r for r in routes):
                results.append((f"C5.{path}", "PASS", f"路由 {path} 已注册"))
            else:
                results.append((f"C5.{path}", "FAIL", f"路由 {path} 未注册"))
    except Exception as e:
        results.append(("C5.api", "ERROR", str(e)))
    
    return results


# ============================================================================
# Contract 6: Gender Golden Test 验证
# ============================================================================
def validate_gender_golden_test():
    results = []
    
    try:
        from tongshu.engines.heluo import HeluoCanonical
        
        canonical = HeluoCanonical()
        
        # 测试路径分歧：同八字不同性别 → 卦象必须不同
        male_input = [("甲","辰"),("辛","未"),("丙","戌"),("甲","午")]
        female_input = [("甲","辰"),("辛","未"),("丙","戌"),("甲","午")]
        
        male_result = canonical.calculate(male_input, "male", "午", "xia")
        female_result = canonical.calculate(female_input, "female", "午", "xia")
        
        if male_result.prenatal.hexagram_name != female_result.prenatal.hexagram_name:
            results.append(("C6.sensitivity", "PASS", 
                f"路径分歧验证通过: 男→{male_result.prenatal.hexagram_name}, 女→{female_result.prenatal.hexagram_name}"))
        else:
            results.append(("C6.sensitivity", "FAIL", 
                f"路径分歧验证失败: 男女结果相同={male_result.prenatal.hexagram_name}"))
        
        # 纪晓岚 Golden
        if canonical.verify_golden_case("jixiaolan"):
            results.append(("C6.jixiaolan", "PASS", "纪晓岚 Golden Case 通过"))
        else:
            results.append(("C6.jixiaolan", "FAIL", "纪晓岚 Golden Case 失败"))
            
    except Exception as e:
        results.append(("C6.golden", "ERROR", str(e)))
    
    return results


# ============================================================================
# 主验证流程
# ============================================================================
def main():
    print("=" * 70)
    print("Architecture Freeze V1.0 — Contract 符合性审计")
    print("=" * 70)
    
    all_results = []
    
    validators = [
        ("Contract 1: Profile Contract", validate_profile_contract),
        ("Contract 2: Heluo Engine 8模块", validate_heluo_engine),
        ("Contract 3: Yi Engine 4层", validate_yi_engine),
        ("Contract 4: Calculation Snapshot", validate_snapshot),
        ("Contract 5: API Contract", validate_api_contract),
        ("Contract 6: Gender Golden Test", validate_gender_golden_test),
    ]
    
    for name, validator in validators:
        print(f"\n{'─' * 70}")
        print(f"【{name}】")
        print("─" * 70)
        
        results = validator()
        all_results.extend(results)
        
        for check_id, status, msg in results:
            icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"  {icon} [{check_id}] {status}: {msg}")
    
    # 汇总
    print(f"\n{'═' * 70}")
    print("审计汇总")
    print("═" * 70)
    
    pass_count = sum(1 for _, s, _ in all_results if s == "PASS")
    fail_count = sum(1 for _, s, _ in all_results if s == "FAIL")
    error_count = sum(1 for _, s, _ in all_results if s == "ERROR")
    
    print(f"  通过: {pass_count}")
    print(f"  失败: {fail_count}")
    print(f"  错误: {error_count}")
    print(f"  总计: {len(all_results)}")
    
    if fail_count > 0 or error_count > 0:
        print(f"\n⚠️ 发现 {fail_count + error_count} 项未通过，需修复")
        for cid, s, msg in all_results:
            if s in ("FAIL", "ERROR"):
                print(f"  - [{cid}] {s}: {msg}")
    else:
        print("\n✅ 全部通过！Architecture Freeze V1.0 已正确实施")
    
    return fail_count, error_count


if __name__ == "__main__":
    fail, error = main()
    sys.exit(1 if (fail + error) > 0 else 0)
