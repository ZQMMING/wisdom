"""Reasoning layer: Signal Engine, RuleMatcher, Cross Analysis, Theme Engine."""
from .signal_engine import SignalEngine, build_signals, Signal, build_rule_context
from .matcher import RuleMatcher, RuleContext, resolve_conflicts
from .rule_loader import RuleLoader, RuleLoadError
from .cross_analysis import CrossAnalyzer, CrossResult
from .theme_engine import ThemeEngine
from .rule_db import RuleDB  # deprecated (T203); kept for backward compat

__all__ = [
    "SignalEngine",
    "build_signals",
    "Signal",
    "build_rule_context",
    "RuleMatcher",
    "RuleContext",
    "resolve_conflicts",
    "RuleLoader",
    "RuleLoadError",
    "CrossAnalyzer",
    "CrossResult",
    "ThemeEngine",
    "RuleDB",
]
