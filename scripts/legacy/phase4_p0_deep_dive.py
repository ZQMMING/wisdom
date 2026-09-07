#!/usr/bin/env python3
"""
ZIPING Phase 4 P0 深挖阶段 - 禁止修改代码

依据 BOT-MASTER 裁决：
1. 暂时禁止修改任何代码
2. 仅追踪证据，生成 Gap Ledger
3. 优先 P0-1（ContextAssembler 重复排盘风险）
"""

from __future__ import annotations
import sys
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional
from dataclasses import dataclass, field


# ============================================================================
# GIT HISTORY UTILITIES
# ============================================================================

def git_log(filepath: Path, since: str = None, until: str = None) -> str:
    """获取文件 git log"""
    cmd = ["git", "-C", str(filepath.resolve().parents[3]), "log", "--oneline", "--all"]
    if since:
        cmd.extend(["--since", since])
    if until:
        cmd.extend(["--until", until])
    cmd.append(str(filepath))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout


def git_blame(filepath: Path, line_start: int = None, line_end: int = None) -> str:
    """获取文件 git blame"""
    cmd = ["git", "-C", str(filepath.resolve().parents[3]), "blame"]
    if line_start and line_end:
        cmd.extend(["-L", f"{line_start},{line_end}"])
    cmd.append(str(filepath))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout


def git_log_all(filepath: Path) -> List[dict]:
    """获取文件完整 git 历史记录"""
    cmd = [
        "git", "-C", str(filepath.resolve().parents[3]),
        "log", "--all", "--pretty=format:%H|%an|%ad|%s",
        "--date=short", "--", str(filepath)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    entries = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('|', 3)
        if len(parts) == 4:
            entries.append({
                "hash": parts[0],
                "author": parts[1],
                "date": parts[2],
                "message": parts[3]
            })
    return entries


def git_show(filepath: Path, commit_hash: str = None, lines: Tuple[int, int] = None) -> str:
    """查看特定 commit 的文件内容"""
    cmd = ["git", "-C", str(filepath.resolve().parents[3]), "show"]
    if commit_hash:
        cmd.append(commit_hash)
    if lines:
        cmd.append(f":{filepath.name}")
    cmd.append("--")
    cmd.append(str(filepath))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CallChainEntry:
    """调用链节点"""
    module: str
    function: str
    filepath: str
    line_number: int
    call_type: str  # DIRECT_CALL / IMPORT / PASS_THROUGH
    notes: str = ""


@dataclass
class GapFinding:
    """Gap 发现"""
    finding_id: str
    category: str  # ARCHITECTURE_VIOLATION / LEGACY_REMNANT / MISSING_IMPLEMENTATION / PATH_DEPENDENCY
    severity: str  # P0 / P1 / P2
    description: str
    evidence: str
    git_history: str = ""
    impact: str = ""
    recommendation: str = ""
    belongs_to_legacy: bool = False
    has_unmerged_implementation: bool = False


# ============================================================================
# P0-1: ContextAssembler 重复排盘风险追踪
# ============================================================================

class P01_ContextAssemblerAnalyzer:
    """P0-1: 追踪 ContextAssembler → bazi_engine.compute() 调用链"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings: List[GapFinding] = []
        self.call_chains: List[CallChainEntry] = []
    
    def analyze(self) -> List[GapFinding]:
        """执行完整分析"""
        print("[P0-1] 分析 ContextAssembler 重复排盘风险...")
        
        # 1. 检查 ContextAssembler 的 compute() 调用
        self._trace_compute_call()
        
        # 2. 检查谁调用 ContextAssembler
        self._trace_assembler_callers()
        
        # 3. 检查是否有其他重复排盘入口
        self._find_other_recompute_entries()
        
        # 4. Git 历史追踪
        self._trace_git_history()
        
        return self.findings
    
    def _trace_compute_call(self):
        """追踪 compute() 调用"""
        assembler_path = self.repo_root / "src" / "tongshu" / "reasoning" / "context_assembler.py"
        if not assembler_path.exists():
            self.findings.append(GapFinding(
                finding_id="P0-1-A",
                category="MISSING_IMPLEMENTATION",
                severity="P0",
                description="ContextAssembler 不存在",
                evidence="文件未找到",
                recommendation="检查文件路径"
            ))
            return
        
        content = assembler_path.read_text(encoding='utf-8')
        
        # 定位 compute() 调用
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'bazi_engine.compute(' in line or 'engine.compute(' in line:
                self.findings.append(GapFinding(
                    finding_id="P0-1-A",
                    category="ARCHITECTURE_VIOLATION",
                    severity="P0",
                    description=f"ContextAssembler 第 {i} 行调用 bazi_engine.compute()",
                    evidence=line.strip(),
                    git_history=self._get_git_blame(assembler_path, i),
                    impact="可能重新计算四柱，违反 BAZI Frozen State 原则",
                    recommendation="删除或重构此调用，改为消费已计算的 chart"
                ))
    
    def _trace_assembler_callers(self):
        """追踪谁调用 ContextAssembler"""
        # 搜索所有调用 ContextAssembler 的地方
        results = subprocess.run(
            ['grep', '-rn', 'ContextAssembler', str(self.repo_root / 'src')],
            capture_output=True, text=True
        )
        
        callers = []
        for line in results.stdout.split('\n'):
            if not line or '__pycache__' in line:
                continue
            if 'class ContextAssembler' in line:
                continue
            callers.append(line)
        
        if callers:
            self.findings.append(GapFinding(
                finding_id="P0-1-B",
                category="ARCHITECTURE_VIOLATION",
                severity="P0",
                description=f"ContextAssembler 被 {len(callers)} 处引用",
                evidence='\n'.join(callers[:10]),
                impact="需要确认是否进入生产路径",
                recommendation="检查每个调用点是否必要"
            ))
        else:
            self.findings.append(GapFinding(
                finding_id="P0-1-B",
                category="LEGACY_REMNANT",
                severity="P1",
                description="ContextAssembler 未被任何代码引用",
                evidence="grep 返回空",
                impact="可能是遗留代码，但包含架构违规风险",
                recommendation="考虑删除整个文件"
            ))
    
    def _find_other_recompute_entries(self):
        """查找其他重复排盘入口"""
        recompute_patterns = [
            r'engine\.compute\(',
            r'bazi_engine\.compute\(',
            r'BaziEngine\(\)\.compute\(',
            r'resolver\.resolve\(',
            r'TimeResolver\(\)',
        ]
        
        for pattern in recompute_patterns:
            results = subprocess.run(
                ['grep', '-rn', '--include=*.py', pattern, str(self.repo_root / 'src')],
                capture_output=True, text=True
            )
            
            for line in results.stdout.split('\n'):
                if not line or '__pycache__' in line or 'test_' in line:
                    continue
                # 排除已知的正确调用点
                if 'context_assembler.py' in line:
                    continue
                if 'compute_stage.py' in line:
                    # ComputeStage 是正确调用点
                    continue
                
                self.findings.append(GapFinding(
                    finding_id=f"P0-1-C-{pattern[:10]}-{line[:30]}",
                    category="ARCHITECTURE_VIOLATION",
                    severity="P0",
                    description=f"发现可能的重复排盘调用: {pattern}",
                    evidence=line.strip(),
                    impact="需要人工核查是否为合法调用",
                    recommendation="检查调用点是否在 ZIPING 域内"
                ))
    
    def _trace_git_history(self):
        """Git 历史追踪"""
        assembler_path = self.repo_root / "src" / "tongshu" / "reasoning" / "context_assembler.py"
        if assembler_path.exists():
            history = git_log_all(assembler_path)
            if history:
                self.findings.append(GapFinding(
                    finding_id="P0-1-D",
                    category="GIT_HISTORY",
                    severity="INFO",
                    description="ContextAssembler git 历史记录",
                    evidence=f"共 {len(history)} 次提交",
                    git_history='\n'.join([f"{h['date']} {h['hash'][:8]} {h['message']}" for h in history[:5]]),
                    recommendation="检查是否有主动删除的 commit"
                ))
    
    def _get_git_blame(self, filepath: Path, line_num: int) -> str:
        """获取特定行的 git blame"""
        try:
            result = git_blame(filepath, line_num, line_num)
            return result.strip() if result else "无历史"
        except:
            return "无法获取"


# ============================================================================
# P0-2: 索引路径独立性审计
# ============================================================================

class P02_IndexPathAnalyzer:
    """P0-2: 审计所有 Evidence/Rule/Index 的路径依赖"""
    
    # 危险的路径模式
    DANGEROUS_PATTERNS = [
        r'/[A-Z]:/',           # Windows 盘符绝对路径
        r'/home/',             # Linux 用户目录
        r'C:\\',               # Windows 转义路径
        r'D:\\',
        r'C:/Users/',
        r'/c/Users/',
        r'/d/shuntian/',       # 硬编码项目路径
        r'D:/shuntian',
        r'D:/today',
        r'Path\(["\']/',       # 字面量路径
        r'"D:"',
        r"'D:'",
    ]
    
    # 安全检查的模式
    SAFE_PATTERNS = [
        r'__file__',           # 相对路径安全
        r'Path\(.*parents',    # 相对父目录
        r'Path\(.*resolve',    # 相对解析
        r'sys\.path\.insert',  # 路径注入
    ]
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings: List[GapFinding] = []
        self.vulnerable_files: List[str] = []
    
    def analyze(self) -> List[GapFinding]:
        """执行完整分析"""
        print("[P0-2] 审计路径依赖...")
        
        # 1. 扫描所有 Python 文件
        self._scan_python_files()
        
        # 2. 扫描 JSON 文件（规则/证据）
        self._scan_json_files()
        
        # 3. 检查绝对路径引用
        self._check_absolute_paths()
        
        # 4. 检查 cwd 依赖
        self._check_cwd_dependencies()
        
        # 5. Git 历史检查
        self._check_git_history()
        
        return self.findings
    
    def _scan_python_files(self):
        """扫描 Python 文件中的路径依赖"""
        for py_file in self.repo_root.rglob('*.py'):
            if '__pycache__' in str(py_file) or 'test_' in str(py_file):
                continue
            
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # 跳过注释
                if line.strip().startswith('#'):
                    continue
                
                # 检查危险模式
                for pattern in self.DANGEROUS_PATTERNS:
                    if re.search(pattern, line):
                        # 检查是否也是安全模式
                        is_safe = any(re.search(sp, line) for sp in self.SAFE_PATTERNS)
                        if not is_safe:
                            self.findings.append(GapFinding(
                                finding_id=f"P0-2-PY-{py_file.name}-{i}",
                                category="PATH_DEPENDENCY",
                                severity="P0",
                                description=f"可能的路径依赖: {py_file.name}:{i}",
                                evidence=line.strip()[:100],
                                impact="项目移动后索引可能失效",
                                recommendation="改为相对路径或 Path(__file__) 解析"
                            ))
                            self.vulnerable_files.append(str(py_file))
                            break
    
    def _scan_json_files(self):
        """扫描 JSON 文件中的路径依赖"""
        json_dirs = [
            self.repo_root / "backend" / "data" / "rules",
            self.repo_root / "data" / "rules",
            self.repo_root / "docs",
        ]
        
        for json_dir in json_dirs:
            if not json_dir.exists():
                continue
            
            for json_file in json_dir.rglob('*.json'):
                content = json_file.read_text(encoding='utf-8')
                
                # 检查是否包含绝对路径
                if re.search(r'[A-Z]:/|/home/|/c/Users/', content):
                    self.findings.append(GapFinding(
                        finding_id=f"P0-2-JSON-{json_file.name}",
                        category="PATH_DEPENDENCY",
                        severity="P1",
                        description=f"JSON 文件包含绝对路径: {json_file.name}",
                        evidence="文件内容包含绝对路径",
                        impact="规则/证据数据硬编码路径",
                        recommendation="移除数据中的路径信息，使用相对引用"
                    ))
    
    def _check_absolute_paths(self):
        """检查绝对路径引用"""
        results = subprocess.run(
            ['grep', '-rn', '--include=*.py', 
             '-E', r'/(home|usr|var|etc)/|"D:|"C:|\'D:|\'C:',
             str(self.repo_root / 'src')],
            capture_output=True, text=True
        )
        
        for line in results.stdout.split('\n'):
            if not line or '__pycache__' in line:
                continue
            self.findings.append(GapFinding(
                finding_id=f"P0-2-ABS-{line.split(':')[1] if ':' in line else 'unknown'}",
                category="PATH_DEPENDENCY",
                severity="P0",
                description="发现绝对路径引用",
                evidence=line.strip()[:100],
                impact="项目移动后必然失效",
                recommendation="必须改为相对路径"
            ))
    
    def _check_cwd_dependencies(self):
        """检查 cwd 依赖"""
        cwd_patterns = [
            r'os\.getcwd\(\)',
            r'pathlib\.Path\(\)',           # 无参数的 Path()
            r'open\([\'"][^/]',            # open 相对路径
        ]
        
        for pattern in cwd_patterns:
            results = subprocess.run(
                ['grep', '-rn', '--include=*.py', pattern, str(self.repo_root / 'src')],
                capture_output=True, text=True
            )
            
            for line in results.stdout.split('\n'):
                if not line or '__pycache__' in line:
                    continue
                self.findings.append(GapFinding(
                    finding_id=f"P0-2-CWD-{pattern[:10]}-{line[:30]}",
                    category="PATH_DEPENDENCY",
                    severity="P1",
                    description="发现 cwd 依赖",
                    evidence=line.strip()[:100],
                    impact="工作目录变化时行为不确定",
                    recommendation="使用 Path(__file__).resolve() 替代"
                ))
    
    def _check_git_history(self):
        """Git 历史检查"""
        # 检查是否有路径相关的 commit
        result = subprocess.run(
            ['git', '-C', str(self.repo_root), 'log', '--all', '--oneline',
             '--grep=路径', '-n', '20'],
            capture_output=True, text=True
        )
        
        if result.stdout.strip():
            self.findings.append(GapFinding(
                finding_id="P0-2-GIT",
                category="GIT_HISTORY",
                severity="INFO",
                description="Git 历史中有路径相关提交",
                evidence=result.stdout.strip()[:200],
                recommendation="检查是否有路径修复 commit"
            ))


# ============================================================================
# P0-3: Evidence → Rule 链路追踪
# ============================================================================

class P03_EvidenceRuleLinkAnalyzer:
    """P0-3: 逐条追踪 Evidence → Rule 链路"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings: List[GapFinding] = []
        self.rule_evidence_map: Dict[str, List[str]] = {}
    
    def analyze(self) -> List[GapFinding]:
        """执行完整分析"""
        print("[P0-3] 追踪 Evidence → Rule 链路...")
        
        # 1. 加载所有规则
        self._load_rules()
        
        # 2. 逐条验证证据引用
        self._verify_evidence_refs()
        
        # 3. 检查孤立 Registry
        self._check_orphan_registries()
        
        return self.findings
    
    def _load_rules(self):
        """加载所有规则"""
        rules_dirs = [
            self.repo_root / "backend" / "data" / "rules",
            self.repo_root / "data" / "rules",
        ]
        
        for rules_dir in rules_dirs:
            if not rules_dir.exists():
                continue
            
            for rule_file in rules_dir.glob('*.json'):
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        rule = __import__('json').load(f)
                    
                    rule_id = rule.get('rule_id', rule_file.stem)
                    evidence_refs = rule.get('evidence_refs', [])
                    
                    if evidence_refs:
                        self.rule_evidence_map[rule_id] = evidence_refs
                
                except Exception as e:
                    self.findings.append(GapFinding(
                        finding_id=f"P0-3-LOAD-{rule_file.name}",
                        category="DATA_INTEGRITY",
                        severity="P1",
                        description=f"规则加载失败: {rule_file.name}",
                        evidence=str(e),
                        recommendation="修复规则文件或数据格式"
                    ))
    
    def _verify_evidence_refs(self):
        """验证证据引用"""
        evidence_dirs = [
            self.repo_root / "data" / "evidence",
            self.repo_root / "backend" / "data" / "evidence",
            self.repo_root / "src" / "tongshu" / "classic_evidence",
        ]
        
        # 构建证据 ID 集合
        all_evidence_ids = set()
        for ev_dir in evidence_dirs:
            if ev_dir.exists():
                for ev_file in ev_dir.rglob('*.json'):
                    # 从文件名提取证据 ID
                    stem = ev_file.stem
                    if '-' in stem:
                        all_evidence_ids.add(stem.split('-')[0])
        
        # 验证每个规则的引用
        unverified_refs = []
        for rule_id, refs in self.rule_evidence_map.items():
            for ref in refs:
                # 检查引用是否对应真实证据
                found = False
                for ev_dir in evidence_dirs:
                    if ev_dir.exists():
                        for pattern in [f"*{ref}*.json", f"{ref}*.json"]:
                            if list(ev_dir.rglob(pattern)):
                                found = True
                                break
                    if found:
                        break
                
                if not found:
                    unverified_refs.append((rule_id, ref))
        
        if unverified_refs:
            self.findings.append(GapFinding(
                finding_id="P0-3-REF",
                category="DATA_INTEGRITY",
                severity="P0",
                description=f"发现 {len(unverified_refs)} 个未验证的证据引用",
                evidence=f"示例: {unverified_refs[:5]}",
                impact="Rule 引用了不存在的 Evidence，语义链条断裂",
                recommendation="建立证据索引验证机制，或补充缺失的证据文件"
            ))
        
        # 统计
        total_refs = sum(len(refs) for refs in self.rule_evidence_map.values())
        verified_ratio = (total_refs - len(unverified_refs)) / total_refs * 100 if total_refs > 0 else 100
        
        self.findings.append(GapFinding(
            finding_id="P0-3-STAT",
            category="DATA_INTEGRITY",
            severity="INFO",
            description="Evidence 引用统计",
            evidence=f"总引用数: {total_refs}, 已验证: {total_refs - len(unverified_refs)}, 未验证: {len(unverified_refs)}, 验证率: {verified_ratio:.1f}%",
            recommendation="目标是 100% 验证率"
        ))
    
    def _check_orphan_registries(self):
        """检查孤立 Registry"""
        # 检查 phase_b1_evidence_connection.py 中的 Registry
        registry_path = self.repo_root / "src" / "tongshu" / "phase_b1_evidence_connection.py"
        if registry_path.exists():
            content = registry_path.read_text(encoding='utf-8')
            
            # 检查是否有实际使用
            if 'class EvidenceRegistry' in content and 'class RuleRegistry' in content:
                # 检查是否被导入
                import_results = subprocess.run(
                    ['grep', '-rn', 'from.*phase_b1', str(self.repo_root / 'src')],
                    capture_output=True, text=True
                )
                
                if not import_results.stdout.strip():
                    self.findings.append(GapFinding(
                        finding_id="P0-3-ORPHAN",
                        category="MISSING_IMPLEMENTATION",
                        severity="P1",
                        description="EvidenceRegistry / RuleRegistry 未被导入使用",
                        evidence="phase_b1_evidence_connection.py 存在但无导入",
                        impact="Registry 仅是设计，未进入生产路径",
                        recommendation="建立 Registry → RuleEvaluator 的连接"
                    ))


# ============================================================================
# P0-4: RuleMatcher 内部机制检查
# ============================================================================

class P04_RuleMatcherAnalyzer:
    """P0-4: 检查 RuleMatcher/SignalEngine 内部机制"""
    
    # 禁止的聚合机制
    FORBIDDEN_PATTERNS = [
        r'\bscore\b',
        r'\bweight\b',
        r'\bvote\b',
        r'\bpercentage\b',
        r'\bprobability\b',
        r'\bconfidence\b',
        r'\baggregat',
        r'\bsum\(',
        r'\bmean\(',
        r'\bavg\(',
        r'\bratio\b',
        r'\brank\b',
        r'\bsort_by_score',
        r'top_k',
        r'max_score',
        r'score_threshold',
    ]
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings: List[GapFinding] = []
    
    def analyze(self) -> List[GapFinding]:
        """执行完整分析"""
        print("[P0-4] 检查 RuleMatcher/SignalEngine 内部机制...")
        
        # 1. 检查 matcher.py
        self._analyze_matcher()
        
        # 2. 检查 signal_engine.py
        self._analyze_signal_engine()
        
        # 3. 检查 resolver.py
        self._analyze_resolver()
        
        return self.findings
    
    def _analyze_matcher(self):
        """分析 RuleMatcher"""
        matcher_path = self.repo_root / "src" / "tongshu" / "reasoning" / "matcher.py"
        if not matcher_path.exists():
            self.findings.append(GapFinding(
                finding_id="P0-4-MATCHER",
                category="MISSING_IMPLEMENTATION",
                severity="P0",
                description="RuleMatcher 不存在",
                evidence="文件未找到",
                recommendation="检查文件路径或重建"
            ))
            return
        
        content = matcher_path.read_text(encoding='utf-8')
        
        # 检查禁止模式
        for pattern in self.FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # 过滤掉注释中的提及
                real_matches = []
                for line in content.split('\n'):
                    if line.strip().startswith('#'):
                        continue
                    if re.search(pattern, line, re.IGNORECASE):
                        real_matches.append(line.strip()[:80])
                
                if real_matches:
                    self.findings.append(GapFinding(
                        finding_id=f"P0-4-MATCHER-{pattern[:10]}",
                        category="ARCHITECTURE_VIOLATION",
                        severity="P0",
                        description=f"RuleMatcher 包含禁止的聚合机制: {pattern}",
                        evidence='\n'.join(real_matches[:3]),
                        impact="违反 BOT-MASTER 禁止 score/weight/vote 作为裁决机制的规定",
                        recommendation="必须移除或重构为确定性条件判断"
                    ))
    
    def _analyze_signal_engine(self):
        """分析 SignalEngine"""
        engine_path = self.repo_root / "src" / "tongshu" / "reasoning" / "signal_engine.py"
        if not engine_path.exists():
            return
        
        content = engine_path.read_text(encoding='utf-8')
        
        for pattern in self.FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                real_matches = []
                for line in content.split('\n'):
                    if line.strip().startswith('#'):
                        continue
                    if re.search(pattern, line, re.IGNORECASE):
                        real_matches.append(line.strip()[:80])
                
                if real_matches:
                    self.findings.append(GapFinding(
                        finding_id=f"P0-4-SIGNAL-{pattern[:10]}",
                        category="ARCHITECTURE_VIOLATION",
                        severity="P0",
                        description=f"SignalEngine 包含禁止的聚合机制: {pattern}",
                        evidence='\n'.join(real_matches[:3]),
                        impact="违反 BOT-MASTER 禁止 score/weight/vote 作为裁决机制的规定",
                        recommendation="必须移除或重构为确定性条件判断"
                    ))
    
    def _analyze_resolver(self):
        """分析 resolver（如果有）"""
        resolver_path = self.repo_root / "src" / "tongshu" / "reasoning" / "resolver.py"
        if resolver_path.exists():
            content = resolver_path.read_text(encoding='utf-8')
            
            # 检查是否有权重或分数计算
            if re.search(r'score.*=.*\*', content) or re.search(r'weight.*=.*\+', content):
                self.findings.append(GapFinding(
                    finding_id="P0-4-RESOLVER",
                    category="ARCHITECTURE_VIOLATION",
                    severity="P0",
                    description="Resolver 包含分数/权重计算",
                    evidence="检测到 score* 或 weight+ 模式",
                    impact="可能将非确定性机制引入裁决",
                    recommendation="检查是否为必要的工程计算，而非命理裁决"
                ))


# ============================================================================
# P0-5: Judgment Synthesis 边界检查
# ============================================================================

class P05_JudgmentBoundaryAnalyzer:
    """P0-5: 检查 Judgment 与 Signal 的边界"""
    
    # 五大辨证域
    DOMAINS = {
        "wangshuai": "旺衰",
        "pattern": "格局",
        "yongshen": "用神",
        "ten_god": "十神语义",
        "event": "事件判断"
    }
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings: List[GapFinding] = []
    
    def analyze(self) -> List[GapFinding]:
        """执行完整分析"""
        print("[P0-5] 检查 Judgment 与 Signal 边界...")
        
        # 1. 检查 Signal 类的字段定义
        self._check_signal_fields()
        
        # 2. 检查是否有 Domain Judgment 概念
        self._check_domain_judgment()
        
        # 3. 检查五大领域是否独立
        self._check_domain_independence()
        
        return self.findings
    
    def _check_signal_fields(self):
        """检查 Signal 类字段"""
        signal_path = self.repo_root / "src" / "tongshu" / "reasoning" / "signal_engine.py"
        if not signal_path.exists():
            return
        
        content = signal_path.read_text(encoding='utf-8')
        
        # 提取 Signal 类的定义
        signal_match = re.search(r'class Signal[^:]*:[\s\S]*?(?=\nclass |\n\ndef |\Z)', content)
        if signal_match:
            signal_def = signal_match.group(0)
            
            # 检查是否包含 domain 字段
            if 'domain' not in signal_def.lower():
                self.findings.append(GapFinding(
                    finding_id="P0-5-SIGNAL",
                    category="MISSING_IMPLEMENTATION",
                    severity="P1",
                    description="Signal 类缺少 domain 字段",
                    evidence="无法区分 Signal 属于哪个辨证域",
                    impact="无法进行 Domain-specific Judgment Synthesis",
                    recommendation="在 Signal 类中添加 domain 字段"
                ))
    
    def _check_domain_judgment(self):
        """检查 Domain Judgment 概念"""
        # 搜索所有文件中是否有 Domain Judgment 的实现
        results = subprocess.run(
            ['grep', '-rn', '--include=*.py', 
             '-E', 'DomainJudgment|domain_judgment|Judgment.*Synthesis',
             str(self.repo_root / 'src')],
            capture_output=True, text=True
        )
        
        if not results.stdout.strip():
            self.findings.append(GapFinding(
                finding_id="P0-5-JUDGMENT",
                category="MISSING_IMPLEMENTATION",
                severity="P0",
                description="未发现 Domain Judgment 实现",
                evidence="grep 返回空",
                impact="Signal 直接输出，没有经过 Domain Judgment 层",
                recommendation="建立 Domain Judgment 层，将 Signal 汇总为各域 Judgment"
            ))
        else:
            self.findings.append(GapFinding(
                finding_id="P0-5-JUDGMENT-FOUND",
                category="INFO",
                severity="INFO",
                description="发现 Domain Judgment 相关代码",
                evidence=results.stdout.strip()[:200],
                recommendation="验证其是否为真正的 Judgment Synthesis"
            ))
    
    def _check_domain_independence(self):
        """检查五大领域是否独立"""
        # 统计各领域的规则数
        rules_dir = self.repo_root / "backend" / "data" / "rules"
        if not rules_dir.exists():
            return
        
        domain_counts = {k: 0 for k in self.DOMAINS.keys()}
        
        for rule_file in rules_dir.glob('*.json'):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    import json
                    rule = json.load(f)
                
                rule_type = rule.get('rule_type', '').lower()
                
                # 根据规则类型归类
                if '旺衰' in rule_type or 'strength' in rule_type or rule_type.startswith('ws-'):
                    domain_counts['wangshuai'] += 1
                elif '格局' in rule_type or 'pattern' in rule_type or rule_type.startswith('pt-'):
                    domain_counts['pattern'] += 1
                elif '用神' in rule_type or 'yongshen' in rule_type or rule_type.startswith('yg-'):
                    domain_counts['yongshen'] += 1
                elif '十神' in rule_type or 'ten_god' in rule_type or rule_type.startswith('tg-'):
                    domain_counts['ten_god'] += 1
                elif 'event' in rule_type or rule_type.startswith('ev-'):
                    domain_counts['event'] += 1
            
            except:
                pass
        
        # 检查结果
        empty_domains = [k for k, v in domain_counts.items() if v == 0]
        
        if empty_domains:
            self.findings.append(GapFinding(
                finding_id="P0-5-DOMAIN",
                category="MISSING_IMPLEMENTATION",
                severity="P0",
                description=f"五大辨证域中以下领域无规则: {empty_domains}",
                evidence=f"领域分布: {domain_counts}",
                impact="这些领域的 Judgment 无法产生",
                recommendation="补充缺失领域的规则"
            ))
        
        if not empty_domains:
            self.findings.append(GapFinding(
                finding_id="P0-5-DOMAIN-OK",
                category="INFO",
                severity="INFO",
                description="五大领域均有规则覆盖",
                evidence=f"领域分布: {domain_counts}",
                recommendation="检查 Synthesis 机制是否存在"
            ))


# ============================================================================
# P0-6: 五大领域边界确认
# ============================================================================

class P06_DomainBoundaryAnalyzer:
    """P0-6: 确认五大领域边界"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings: List[GapFinding] = []
    
    def analyze(self) -> List[GapFinding]:
        """执行完整分析"""
        print("[P0-6] 确认五大领域边界...")
        
        # 1. 检查是否有独立的 Domain Engine
        self._check_domain_engines()
        
        # 2. 检查 CrossDomainOrchestrator
        self._check_cross_domain()
        
        # 3. 检查 Signal → Judgment 转换
        self._check_signal_to_judgment()
        
        return self.findings
    
    def _check_domain_engines(self):
        """检查独立 Domain Engine"""
        domain_engines = [
            ("旺衰", "strength_engine"),
            ("格局", "pattern_engine"),
            ("用神", "yongshen_engine"),
            ("十神语义", "ten_god_semantic_engine"),
            ("事件判断", "event_engine"),
        ]
        
        found = []
        for name, module in domain_engines:
            result = subprocess.run(
                ['grep', '-rl', f'class.*{module}', str(self.repo_root / 'src')],
                capture_output=True, text=True
            )
            if result.stdout.strip():
                found.append(name)
        
        missing = [name for name, _ in domain_engines if name not in found]
        
        if missing:
            self.findings.append(GapFinding(
                finding_id="P0-6-ENGINE",
                category="MISSING_IMPLEMENTATION",
                severity="P1",
                description=f"以下领域无独立 Engine: {missing}",
                evidence=f"已找到: {found}",
                impact="领域判断可能混入主引擎，违反单一职责",
                recommendation="为每个领域建立独立的 Judgment Engine"
            ))
    
    def _check_cross_domain(self):
        """检查跨域编排"""
        orchestrator_path = self.repo_root / "src" / "tongshu" / "cross_domain" / "orchestrator.py"
        if orchestrator_path.exists():
            content = orchestrator_path.read_text(encoding='utf-8')
            
            # 检查是否有 Synthesis 逻辑
            if 'synthesis' in content.lower() or 'merge' in content.lower():
                self.findings.append(GapFinding(
                    finding_id="P0-6-ORCHESTRATOR",
                    category="INFO",
                    severity="INFO",
                    description="CrossDomainOrchestrator 包含 Synthesis 逻辑",
                    evidence="发现 synthesis/merge 关键词",
                    recommendation="验证是否为真正的 Domain Judgment Synthesis"
                ))
            else:
                self.findings.append(GapFinding(
                    finding_id="P0-6-ORCHESTRATOR-MISSING",
                    category="MISSING_IMPLEMENTATION",
                    severity="P1",
                    description="CrossDomainOrchestrator 缺少 Synthesis 逻辑",
                    evidence="未发现 synthesis/merge 关键词",
                    impact="五大领域可能各自独立，没有 Synthesis",
                    recommendation="在 Orchestrator 中建立 Synthesis 机制"
                ))
        else:
            self.findings.append(GapFinding(
                finding_id="P0-6-ORCHESTRATOR-NOTFOUND",
                category="MISSING_IMPLEMENTATION",
                severity="P1",
                description="CrossDomainOrchestrator 不存在",
                evidence="文件未找到",
                impact="跨域编排无法实现",
                recommendation="建立 CrossDomainOrchestrator"
            ))
    
    def _check_signal_to_judgment(self):
        """检查 Signal → Judgment 转换"""
        # 搜索 Signal → Judgment 的转换逻辑
        results = subprocess.run(
            ['grep', '-rn', '--include=*.py',
             '-E', 'Signal.*Judgment|Judgment.*Signal|signal.*->.*judgment',
             str(self.repo_root / 'src')],
            capture_output=True, text=True
        )
        
        if not results.stdout.strip():
            self.findings.append(GapFinding(
                finding_id="P0-6-TRANSFORM",
                category="MISSING_IMPLEMENTATION",
                severity="P1",
                description="未发现 Signal → Judgment 转换逻辑",
                evidence="grep 返回空",
                impact="Signal 可能直接作为输出，没有经过 Judgment 转换",
                recommendation="建立 Signal → Judgment 转换层"
            ))


# ============================================================================
# P0-7: 端到端追踪
# ============================================================================

class P07_EndToEndAnalyzer:
    """P0-7: 端到端追踪真实 Canonical BAZI Case"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings: List[GapFinding] = []
    
    def analyze(self) -> List[GapFinding]:
        """执行完整分析"""
        print("[P0-7] 端到端追踪...")
        
        # 1. 追踪 Pipeline 入口
        self._trace_pipeline_entry()
        
        # 2. 检查 ComputeStage
        self._trace_compute_stage()
        
        # 3. 检查 SignalEngine 输出
        self._trace_signal_output()
        
        # 4. 检查 Composer 输入
        self._trace_composer_input()
        
        return self.findings
    
    def _trace_pipeline_entry(self):
        """追踪 Pipeline 入口"""
        pipeline_path = self.repo_root / "src" / "tongshu" / "pipeline.py"
        if not pipeline_path.exists():
            self.findings.append(GapFinding(
                finding_id="P0-7-PIPELINE",
                category="MISSING_IMPLEMENTATION",
                severity="P0",
                description="Pipeline 不存在",
                evidence="文件未找到",
                recommendation="检查 Pipeline 文件位置"
            ))
            return
        
        content = pipeline_path.read_text(encoding='utf-8')
        
        # 检查是否有 ContextAssembler 调用
        if 'ContextAssembler' in content or 'context_assembler' in content:
            self.findings.append(GapFinding(
                finding_id="P0-7-PIPELINE-ASSEMBLER",
                category="ARCHITECTURE_VIOLATION",
                severity="P0",
                description="Pipeline 可能调用 ContextAssembler",
                evidence="发现 ContextAssembler 引用",
                impact="可能导致重复排盘进入生产路径",
                recommendation="立即检查并删除"
            ))
        else:
            self.findings.append(GapFinding(
                finding_id="P0-7-PIPELINE-OK",
                category="INFO",
                severity="INFO",
                description="Pipeline 未直接调用 ContextAssembler",
                evidence="未发现 ContextAssembler 引用",
                recommendation="但仍需检查间接调用"
            ))
    
    def _trace_compute_stage(self):
        """追踪 ComputeStage"""
        compute_stage_path = self.repo_root / "src" / "tongshu" / "pipeline_stages" / "compute_stage.py"
        if not compute_stage_path.exists():
            return
        
        content = compute_stage_path.read_text(encoding='utf-8')
        
        # 检查是否有重复排盘
        if 'bazi_engine.compute(' in content:
            # 这是预期的，因为 ComputeStage 是合法的排盘入口
            self.findings.append(GapFinding(
                finding_id="P0-7-COMPUTE-STAGE",
                category="INFO",
                severity="INFO",
                description="ComputeStage 调用 bazi_engine.compute()（预期行为）",
                evidence="ComputeStage 是合法的 BAZI 计算入口",
                recommendation="确认此入口是唯一的排盘调用点"
            ))
        
        # 检查是否有 ContextAssembler
        if 'ContextAssembler' in content:
            self.findings.append(GapFinding(
                finding_id="P0-7-COMPUTE-ASSEMBLER",
                category="ARCHITECTURE_VIOLATION",
                severity="P0",
                description="ComputeStage 调用 ContextAssembler",
                evidence="发现 ContextAssembler 引用",
                impact="可能引入重复排盘风险",
                recommendation="删除此调用"
            ))
    
    def _trace_signal_output(self):
        """追踪 Signal 输出"""
        signal_path = self.repo_root / "src" / "tongshu" / "reasoning" / "signal_engine.py"
        if not signal_path.exists():
            return
        
        content = signal_path.read_text(encoding='utf-8')
        
        # 检查 Signal 产出逻辑
        if 'return Signal(' in content:
            self.findings.append(GapFinding(
                finding_id="P0-7-SIGNAL-PRODUCE",
                category="INFO",
                severity="INFO",
                description="SignalEngine 产出 Signal",
                evidence="发现 Signal 构造逻辑",
                recommendation="验证 Signal 包含必要的可追溯字段"
            ))
    
    def _trace_composer_input(self):
        """追踪 Composer 输入"""
        composer_path = self.repo_root / "src" / "tongshu" / "canonical" / "composer.py"
        if not composer_path.exists():
            return
        
        content = composer_path.read_text(encoding='utf-8')
        
        # 检查是否需要 Signal 输入
        if 'signals' in content:
            self.findings.append(GapFinding(
                finding_id="P0-7-COMPOSER-SIGNAL",
                category="INFO",
                severity="INFO",
                description="Composer 接收 Signal 输入",
                evidence="发现 signals 字段",
                recommendation="验证 Signal → Canonical Content 的转换是否正确"
            ))


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """主函数"""
    print("=" * 80)
    print("ZIPING Phase 4 P0 深挖阶段 - 证据追踪")
    print("=" * 80)
    print()
    
    # 确定仓库根目录
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    
    print(f"仓库根目录: {repo_root}")
    print()
    
    all_findings: List[GapFinding] = []
    
    # P0-1: ContextAssembler
    print("\n" + "=" * 80)
    print("一、P0-1: ContextAssembler 重复排盘风险追踪")
    print("=" * 80)
    p01 = P01_ContextAssemblerAnalyzer(repo_root)
    findings_p01 = p01.analyze()
    all_findings.extend(findings_p01)
    for f in findings_p01:
        icon = "❌" if f.severity == "P0" else "⚠️" if f.severity == "P1" else "ℹ️"
        print(f"  {icon} [{f.finding_id}] {f.description}")
        if f.evidence:
            print(f"     证据: {f.evidence[:100]}")
    
    # P0-2: 路径依赖
    print("\n" + "=" * 80)
    print("二、P0-2: 索引路径独立性审计")
    print("=" * 80)
    p02 = P02_IndexPathAnalyzer(repo_root)
    findings_p02 = p02.analyze()
    all_findings.extend(findings_p02)
    for f in findings_p02:
        icon = "❌" if f.severity == "P0" else "⚠️" if f.severity == "P1" else "ℹ️"
        print(f"  {icon} [{f.finding_id}] {f.description}")
        if f.evidence:
            print(f"     证据: {f.evidence[:100]}")
    
    # P0-3: Evidence → Rule
    print("\n" + "=" * 80)
    print("三、P0-3: Evidence → Rule 链路追踪")
    print("=" * 80)
    p03 = P03_EvidenceRuleLinkAnalyzer(repo_root)
    findings_p03 = p03.analyze()
    all_findings.extend(findings_p03)
    for f in findings_p03:
        icon = "❌" if f.severity == "P0" else "⚠️" if f.severity == "P1" else "ℹ️"
        print(f"  {icon} [{f.finding_id}] {f.description}")
        if f.evidence:
            print(f"     证据: {f.evidence[:100]}")
    
    # P0-4: RuleMatcher 内部机制
    print("\n" + "=" * 80)
    print("四、P0-4: RuleMatcher/SignalEngine 内部机制检查")
    print("=" * 80)
    p04 = P04_RuleMatcherAnalyzer(repo_root)
    findings_p04 = p04.analyze()
    all_findings.extend(findings_p04)
    for f in findings_p04:
        icon = "❌" if f.severity == "P0" else "⚠️" if f.severity == "P1" else "ℹ️"
        print(f"  {icon} [{f.finding_id}] {f.description}")
        if f.evidence:
            print(f"     证据: {f.evidence[:100]}")
    
    # P0-5: Judgment 边界
    print("\n" + "=" * 80)
    print("五、P0-5: Judgment 与 Signal 边界检查")
    print("=" * 80)
    p05 = P05_JudgmentBoundaryAnalyzer(repo_root)
    findings_p05 = p05.analyze()
    all_findings.extend(findings_p05)
    for f in findings_p05:
        icon = "❌" if f.severity == "P0" else "⚠️" if f.severity == "P1" else "ℹ️"
        print(f"  {icon} [{f.finding_id}] {f.description}")
        if f.evidence:
            print(f"     证据: {f.evidence[:100]}")
    
    # P0-6: 五大领域边界
    print("\n" + "=" * 80)
    print("六、P0-6: 五大领域边界确认")
    print("=" * 80)
    p06 = P06_DomainBoundaryAnalyzer(repo_root)
    findings_p06 = p06.analyze()
    all_findings.extend(findings_p06)
    for f in findings_p06:
        icon = "❌" if f.severity == "P0" else "⚠️" if f.severity == "P1" else "ℹ️"
        print(f"  {icon} [{f.finding_id}] {f.description}")
        if f.evidence:
            print(f"     证据: {f.evidence[:100]}")
    
    # P0-7: 端到端追踪
    print("\n" + "=" * 80)
    print("七、P0-7: 端到端追踪")
    print("=" * 80)
    p07 = P07_EndToEndAnalyzer(repo_root)
    findings_p07 = p07.analyze()
    all_findings.extend(findings_p07)
    for f in findings_p07:
        icon = "❌" if f.severity == "P0" else "⚠️" if f.severity == "P1" else "ℹ️"
        print(f"  {icon} [{f.finding_id}] {f.description}")
        if f.evidence:
            print(f"     证据: {f.evidence[:100]}")
    
    # 汇总
    print("\n" + "=" * 80)
    print("汇总")
    print("=" * 80)
    
    p0_count = sum(1 for f in all_findings if f.severity == "P0")
    p1_count = sum(1 for f in all_findings if f.severity == "P1")
    info_count = sum(1 for f in all_findings if f.severity == "INFO")
    
    print(f"P0 问题: {p0_count}")
    print(f"P1 问题: {p1_count}")
    print(f"INFO: {info_count}")
    print(f"总计: {len(all_findings)}")
    
    # 保存报告
    output_path = repo_root / "docs" / "bots" / "BOT-ZIPING" / "PHASE4_P0_DEEP_DIVE_REPORT.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    report_lines = [
        "# ZIPING Phase 4 P0 深挖阶段报告",
        "",
        "**任务 ID**: T-ENGINE-BAZI-002 Phase 4 P0 Deep Dive",
        "**执行者**: @bot-ziping",
        "**日期**: 2026-09-07",
        "**状态**: 证据追踪完成，禁止修改代码",
        "",
        "---",
        "",
        "## 汇总",
        "",
        f"| 级别 | 数量 |",
        f"|------|------|",
        f"| P0 | {p0_count} |",
        f"| P1 | {p1_count} |",
        f"| INFO | {info_count} |",
        "",
        "---",
        "",
        "## 详细发现",
        "",
    ]
    
    for f in all_findings:
        icon = "🔴" if f.severity == "P0" else "🟡" if f.severity == "P1" else "🔵"
        report_lines.extend([
            f"### {icon} [{f.finding_id}] {f.description}",
            "",
            f"- **类别**: {f.category}",
            f"- **严重级别**: {f.severity}",
            f"- **证据**: `{f.evidence[:200]}`",
        ])
        if f.git_history:
            report_lines.append(f"- **Git 历史**: {f.git_history[:200]}")
        if f.impact:
            report_lines.append(f"- **影响**: {f.impact}")
        if f.recommendation:
            report_lines.append(f"- **建议**: {f.recommendation}")
        report_lines.append("")
    
    output_path.write_text('\n'.join(report_lines), encoding='utf-8')
    print(f"\n✅ 报告已保存: {output_path}")
    
    return 0 if p0_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
