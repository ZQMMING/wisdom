"""Entry point for `python -m tongshu.golden`."""

from __future__ import annotations
import sys

from .main import main

if __name__ == "__main__":
    sys.exit(main())
