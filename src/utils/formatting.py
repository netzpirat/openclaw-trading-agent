"""Utility helpers for consistently formatting numeric values."""


def format_number(value, decimals=2):
    """Round ``value`` to ``decimals`` digits when possible, otherwise return raw."""
    try:
        return round(float(value), decimals)
    except Exception:
        return value


def format_size(value):
    """Format position sizes with 6 decimal place precision."""
    return format_number(value, 6)


