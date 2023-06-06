"""Prometheus exporter"""

import logging
from threading import Lock
from typing import Iterator

from .exceptions import PrometheusExporterException, UnknownMeasurementException
from .metric import Metric
from .types import MetricTypeEnum

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """Manage all measurements and provide the htp interface for interfacing with
    Prometheus."""

    def __init__(self, hide_empty_metrics: bool = False) -> None:
        self._prom: dict[str, Metric] = {}
        self._lock = Lock()
        self._hide_empty_metrics = hide_empty_metrics

    def register(
        self,
        name: str,
        datatype: MetricTypeEnum,
        helpstr: str,
        timeout: int = 0,
        with_update_counter: bool = False,
    ):  # pylint: disable=too-many-arguments
        """Register a name for exporting. This must be called before calling
        `set()`.

        :param str name: The name to register.
        :param str type: One of gauge or counter.
        :param str helpstr: The help information / comment to include in the
          output.
        :param int timeout: Timeout in seconds for any value. Before rendering,
          values which are updated longer ago than this value, are removed."""

        with self._lock:
            if name in self._prom:
                raise PrometheusExporterException(
                    f"The metric '{name}' is already registered"
                )

            metric = Metric(
                name=name,
                datatype=datatype,
                helpstr=helpstr,
                timeout=timeout,
                with_update_counter=with_update_counter,
            )

            self._prom[name] = metric

        if with_update_counter:
            self.register(
                name=f"{name}_updates",
                datatype=MetricTypeEnum.COUNTER,
                helpstr=f"Number of updates to {name}",
                timeout=0,
            )

    def set(self, name: str, labels: dict[str, str], value: float | None):
        """Set a value for exporting.

        :param str name: The name of the value to set. This name must have been
          registered already by calling `register()`.
        :param dict labels: The labels to attach to this name.
        :param value: The value to set. Automatically converted to string.
        :param fmt: The string format to use to convert value to a string.
          Default: '{0}'."""

        # We raise an exception if we do not know the metric name, i.e. if it
        # was not registered
        if name not in self._prom:
            raise UnknownMeasurementException(
                f"Cannot set not registered measurement '{name}'."
            )

        with self._lock:
            metric = self._prom[name]

            metric.set(labels, value)

            if metric.with_update_counter:
                counter = self._prom[f"{name}_updates"]
                counter.inc(labels)

    def check_timeout(self) -> None:
        """Remove all metric instances which have timed out"""

        with self._lock:
            for metric in self._prom.values():
                metric.check_timeout()

    def render_iter(self) -> Iterator[str]:
        """Return an iterator providing each line of Prometheus output."""

        for metric in self._prom.values():
            if not self._hide_empty_metrics or len(metric):
                yield from metric.render_iter()

    def render(self) -> str:
        """Render the current data to Prometheus format. See
        https://prometheus.io/docs/instrumenting/exposition_formats/ for details.

        :returns: String with output suitable for consumption by Prometheus over
          HTTP."""

        self.check_timeout()

        return "\n".join(self.render_iter())
