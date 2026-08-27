"""Golden Test runner per architecture_decisions_v1.md DECISION-008."""
from .runner import GoldenRunner, run_golden_case

__all__ = ["GoldenRunner", "run_golden_case"]
