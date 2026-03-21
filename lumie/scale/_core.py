# lumie/scale/_core.py
from __future__ import annotations

from enum import IntEnum


class UnsupportedScaleError(Exception):
    pass


class ComparisonResult(IntEnum):
    ORDERED_DESCENDING = 0
    ORDERED_SAME = 1
    ORDERED_ASCENDING = 2
    INCOMPARABLE = 3
