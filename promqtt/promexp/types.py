"""Data types used by the prometheus exporter"""

from enum import Enum


class MetricTypeEnum(Enum):
    """Enumeration of metric types"""

    GAUGE = "gauge"
    COUNTER = "counter"
