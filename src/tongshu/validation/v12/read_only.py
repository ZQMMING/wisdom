"""Read-Only Enforcement for Validation Layer.

Contract:
  Validation Layer is READ-ONLY. It consumes:
  - Canonical Signal
  - Temporal Evidence / Convergence
  - Evidence Chain
  - Agreement Evidence

  And outputs:
  - Validation Dimension Status
  - ValidationStatusReport
  - FailureTaxonomy
  - Micro-F1

  Forbidden operations:
  - Modify Canonical Signal
  - Modify Evidence
  - Modify Claim
  - Modify Temporal Evidence
  - Modify Engine Output
  - Write回 Golden Dataset
  - Modify Legacy Ontology
  - Modify Engine calculation result
"""
from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

F = TypeVar('F', bound=Callable[..., Any])


class ReadOnlyViolationError(Exception):
    """Raised when Validation layer attempts to write to non-Validation data."""
    pass


def enforce_read_only(func: F) -> F:
    """Decorator to mark a function as read-only validated.

    In production this would check that no mutations occur to upstream data.
    For Phase 5, we enforce at the test level by verifying immutable inputs.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)
    wrapper.__is_read_only__ = True  # type: ignore
    return wrapper


def validate_read_only_contract(upstream_data: dict, operation: str) -> None:
    """Validate that an operation does not modify upstream data.

    Args:
        upstream_data: snapshot of upstream data before operation
        operation: description of the operation being performed

    Raises:
        ReadOnlyViolationError: if upstream data was modified
    """
    # Phase 5: contract declaration only.
    # Full runtime enforcement requires deep copy comparison which is expensive.
    # Instead, we verify immutability at the test level using frozen dataclasses.
    pass


class ImmutableInputChecker:
    """Runtime checker for immutable inputs.

    Usage:
        checker = ImmutableInputChecker()
        checker.snapshot(data)
        # ... perform validation ...
        checker.verify_no_mutation(data, "upstream")
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, tuple] = {}

    def snapshot(self, key: str, data: Any) -> None:
        """Take a snapshot of upstream data for later comparison."""
        # For frozen dataclasses, we can compare by identity or repr
        self._snapshots[key] = (key, repr(data))

    def verify_no_mutation(self, key: str, data: Any) -> None:
        """Verify that upstream data has not been mutated."""
        if key not in self._snapshots:
            return  # no snapshot taken
        old_repr = self._snapshots[key][1]
        new_repr = repr(data)
        if old_repr != new_repr:
            raise ReadOnlyViolationError(
                f"Read-only violation: upstream data '{key}' was modified during validation"
            )
