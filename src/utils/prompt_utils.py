"""Prompt serialization helpers shared across agent entry points."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Any


def json_default(obj: Any) -> Any:
    """Serialize datetime and set objects for JSON dumps."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    return str(obj)


def safe_float(value: Any) -> float | None:
    """Cast ``value`` to float when possible, otherwise return ``None``."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def round_or_none(value: Any, decimals: int = 2) -> float | None:
    """Round numeric values to ``decimals`` places, preserving ``None``."""
    numeric = safe_float(value)
    if numeric is None:
        return None
    return round(numeric, decimals)


def round_series(series: Iterable[Any] | None, decimals: int = 2) -> list[float | None]:
    """Round each entry in ``series`` to ``decimals`` places when numeric."""
    if not series:
        return []
    rounded: list[float | None] = []
    for val in series:
        numeric = safe_float(val)
        rounded.append(round(numeric, decimals) if numeric is not None else None)
    return rounded
