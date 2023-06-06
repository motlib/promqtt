"""Utility functions"""

from datetime import datetime


def get_current_time() -> datetime:
    """Return the current time as a datetime object.

    Wrapped in a function, so it can be stubbed for testing."""

    return datetime.now()


def _get_label_string(labels: dict[str, str]) -> str:
    """Convert a dictionary of labels to a unique label string"""

    labelstr = ",".join([f'{k}="{labels[k]}"' for k in sorted(labels.keys())])

    return labelstr
