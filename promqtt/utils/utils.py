"""Collection of misc utilities"""


def str_to_bool(val: str) -> bool:
    """Convert a "booly" string to a boolean"""

    return val.strip().lower() in ("y", "yes", "t", "true", "on", "1")
