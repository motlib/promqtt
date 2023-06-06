"""Unit tests of the metric module"""

from ..metric import Metric
from ..types import MetricTypeEnum


def test_promexp_metric_len() -> None:
    """Test that the length of a metric is the number of instances in the metric."""

    metric1 = Metric(name="metric1", datatype=MetricTypeEnum.GAUGE, helpstr="")

    assert len(metric1) == 0

    # After setting a label, there is one instance
    metric1.set(labels={"foo": "bar"}, value=17)
    assert len(metric1) == 1

    # Re-setting the label still leads to one instance
    metric1.set(labels={"foo": "bar"}, value=18)
    assert len(metric1) == 1

    # Setting to None removes the instance
    metric1.set(labels={"foo": "bar"}, value=None)
    assert len(metric1) == 0
