"""Implementation of the metric instance"""

import logging
from typing import TYPE_CHECKING

from .utils import _get_label_string, get_current_time

if TYPE_CHECKING:
    from .metric import Metric

logger = logging.getLogger(__name__)


class MetricInstance:
    """Represents a single metric instance. Instances are identified by a unique
    combination of labels and a value."""

    def __init__(self, metric: "Metric", labels: dict[str, str], value: float):
        self._metric = metric
        self._labels = labels
        self._label_str = _get_label_string(labels)

        self.value = value

    @property
    def value(self) -> float:
        """Return the value"""

        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """Set the value"""

        self._value = value
        self._timestamp = get_current_time()

        logger.debug(f"Set metric instance {self}")

    @property
    def age(self) -> float:
        """Return the age of the metric value, i.e. when it was last set."""

        return (get_current_time() - self._timestamp).total_seconds()

    @property
    def is_timed_out(self) -> bool:
        """Return True if the metric timeout is expired"""

        if not self._metric.has_timeout:
            return False

        return self.age >= self._metric.timeout

    @property
    def label_string(self) -> str:
        """Return the label string of this instance"""
        return self._label_str

    def __str__(self) -> str:
        return f"{self._metric.name}{{{self.label_string}}} {self.value}"
