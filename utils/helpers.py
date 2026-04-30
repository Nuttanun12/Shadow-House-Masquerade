"""
utils/helpers.py
----------------
Shared utility functions for Shadow House: Masquerade.
"""
from __future__ import annotations

import os
import sys
import datetime


def get_project_root() -> str:
    """Return the absolute path to the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(relative: str) -> str:
    """
    Resolve a resource path relative to the project root.
    Works both in development and when running from a packaged binary.
    """
    root = get_project_root()
    return os.path.join(root, relative)


def format_timestamp(ts: str) -> str:
    """
    Convert a raw SQLite CURRENT_TIMESTAMP string (e.g. '2025-05-01 14:23:00')
    to a nicer format like '01 May 2025, 14:23'.
    """
    try:
        dt = datetime.datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %H:%M")
    except (ValueError, TypeError):
        return str(ts)


def pluralise(count: int, singular: str, plural: str | None = None) -> str:
    """Return '{count} singular' or '{count} plural' correctly."""
    if plural is None:
        plural = singular + "s"
    return f"{count} {singular if count == 1 else plural}"


def clamp(value: int | float, lo: int | float, hi: int | float):
    """Clamp `value` between `lo` and `hi`."""
    return max(lo, min(value, hi))


def validate_player_name(name: str) -> str:
    """
    Sanitise a player name string.
    - Strips surrounding whitespace.
    - Falls back to 'Player' if empty.
    - Caps at 24 characters.
    """
    name = name.strip()[:24]
    return name if name else "Player"
