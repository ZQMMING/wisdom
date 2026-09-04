"""
K2G Registry 数据加载器
从YAML文件加载所有Registry数据到内存
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import os


# 默认Registry路径（本地项目路径）
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_PATHS = [
    str(_PROJECT_ROOT / 'src' / 'tongshu' / 'k2g'),
]
DEFAULT_REGISTRY_PATH = os.environ.get('K2G_REGISTRY_PATH', _DEFAULT_PATHS[0])


@dataclass
class RegistryLoader:
    """Registry数据加载器"""
    
    registry_path: Path
    
    def __post_init__(self):
        # 确保路径存在（支持Windows和POSIX路径）
        path_str = str(self.registry_path).replace('\\', '/')
        if not Path(path_str).exists():
            # 尝试原始路径
            if not self.registry_path.exists():
                raise FileNotFoundError(f"Registry path not found: {self.registry_path}")
    
    def load_semantics(self) -> List[Dict]:
        """加载语义注册表"""
        entries = []
        for theme_file in self.registry_path.glob('semantics/theme_*.yaml'):
            theme_name = theme_file.stem.replace('theme_', '').replace('_semantics', '')
            theme_data = yaml.safe_load(theme_file.read_text(encoding='utf-8'))
            if isinstance(theme_data, dict):
                for item in theme_data.get('entries', []):
                    if isinstance(item, dict):
                        item['_theme'] = theme_name
                        entries.append(item)
        
        return entries
    
    def load_relations(self) -> List[Dict]:
        """加载关系注册表"""
        path = self.registry_path / 'relations' / 'relation_registry.yaml'
        if not path.exists():
            return []
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        return data.get('relations', [])
    
    def load_states(self) -> List[Dict]:
        """加载状态模板"""
        # 项目中没有 state 目录
        return []
    
    def load_safety(self) -> List[Dict]:
        """加载安全规则"""
        # 项目中没有 safety 目录
        return []
    
    def load_core(self) -> Dict:
        """加载核心注册表"""
        # 使用 concept_registry.yaml 作为核心注册表
        path = self.registry_path / 'concepts' / 'concept_registry.yaml'
        if not path.exists():
            return {}
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        return data
    
    def load_golden(self) -> Dict:
        """加载黄金数据集 - 从 baziqa 竞赛数据"""
        import json
        golden_path = Path(__file__).resolve().parents[4] / '.tmp_cases' / 'baziqa'
        total_count = 0
        contests = []
        
        for f in sorted(golden_path.glob('contest*_*.json')):
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                if isinstance(data, list):
                    total_count += len(data)
                    contests.append({'file': f.name, 'count': len(data)})
        
        return {
            'total_count': total_count,
            'contests': contests
        }
    
    def get_all_counts(self) -> Dict[str, int]:
        """获取所有Registry条目数"""
        return {
            'semantics': len(self.load_semantics()),
            'relations': len(self.load_relations()),
            'states': len(self.load_states()),
            'safety': len(self.load_safety()),
            'mappings': len(self.load_core().get('mappings', [])),
            'daily_guidance': len(self.load_core().get('daily_guidance', [])),
            'expressions': len(self.load_core().get('expressions', [])),
            'golden': self.load_golden().get('total_count', 0),
        }


def load_k2g_registry(path: Optional[str] = None) -> RegistryLoader:
    """工厂函数：创建Registry加载器"""
    if path is None:
        path = DEFAULT_REGISTRY_PATH
    # 规范化路径
    path = path.replace('\\', '/').replace('//', '/')
    return RegistryLoader(Path(path))
