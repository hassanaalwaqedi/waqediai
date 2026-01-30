"""
Common utility functions for WaqediAI services.
"""

import uuid
from datetime import datetime, timezone


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique identifier.

    Args:
        prefix: Optional prefix for the ID (e.g., "doc", "chunk").

    Returns:
        A unique identifier string.

    Example:
        >>> generate_id("doc")
        'doc_a1b2c3d4e5f6...'
    """
    uid = uuid.uuid4().hex
    if prefix:
        return f"{prefix}_{uid}"
    return uid


def utc_now() -> datetime:
    """
    Get current UTC timestamp.

    Returns:
        Timezone-aware datetime in UTC.
    """
    return datetime.now(timezone.utc)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate.
        max_length: Maximum length before truncation.
        suffix: Suffix to append when truncated.

    Returns:
        Truncated text with suffix if applicable.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def chunk_list(items: list, chunk_size: int) -> list[list]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to split.
        chunk_size: Maximum items per chunk.

    Returns:
        List of chunks.
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_get(data: dict, *keys, default=None):
    """
    Safely get a nested value from a dictionary.

    Args:
        data: Dictionary to search.
        *keys: Sequence of keys to traverse.
        default: Default value if key not found.

    Returns:
        Value at nested key path or default.

    Example:
        >>> safe_get({"a": {"b": 1}}, "a", "b")
        1
        >>> safe_get({"a": {"b": 1}}, "a", "c", default=0)
        0
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data
