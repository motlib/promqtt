"""Unittests for promexp module"""

from datetime import datetime, timedelta

import pytest

from ..promexp import (
    MetricTypeEnum,
    PrometheusExporter,
    PrometheusExporterException,
    UnknownMeasurementException,
)


def _has_line(promexp: PrometheusExporter, line: str):
    """Utility function to check if rendered output contains a specific line."""

    out = promexp.render().split("\n")

    return any(map(lambda l: l == line, out))


@pytest.fixture(name="promexp")
def promexp_fixture() -> PrometheusExporter:
    """Create a new prometheus exporter instance."""

    return PrometheusExporter()


def test_promqtt_register(promexp: PrometheusExporter) -> None:
    """Register measurement and check that it's not yet in the output."""

    promexp.register(
        name="test_meas_1", datatype=MetricTypeEnum.GAUGE, helpstr="yeah", timeout=12
    )

    out = promexp.render().split("\n")

    # we did not set a value, so no measurement shall be visible
    hasline = any(map(lambda l: l.startswith("test_meas_1"), out))

    assert not hasline


def test_promqtt_register_twice(promexp: PrometheusExporter) -> None:
    """Double registration of a measurement raises an exception."""

    promexp.register(
        name="test_meas_1", datatype=MetricTypeEnum.GAUGE, helpstr="yeah", timeout=12
    )

    with pytest.raises(PrometheusExporterException):
        promexp.register(
            name="test_meas_1",
            datatype=MetricTypeEnum.GAUGE,
            helpstr="yeah",
            timeout=12,
        )


def test_promqtt_set(promexp: PrometheusExporter) -> None:
    """Setting a value to a registered measurement works fine."""

    promexp.register(
        name="test_meas_1", datatype=MetricTypeEnum.GAUGE, helpstr="yeah", timeout=12
    )

    promexp.set(name="test_meas_1", value=12.3, labels={"foo": "bar"})

    print("*** Render Output  ***")
    print(promexp.render())

    assert _has_line(promexp, "# HELP test_meas_1 yeah")
    assert _has_line(promexp, "# TYPE test_meas_1 gauge")
    assert _has_line(promexp, 'test_meas_1{foo="bar"} 12.3')


def test_promqtt_unset(promexp: PrometheusExporter) -> None:
    """Setting a value of a registered metric to None removes it."""

    promexp.register(
        name="test_meas_1", datatype=MetricTypeEnum.GAUGE, helpstr="yeah", timeout=12
    )

    # Set to metric values with different labels
    promexp.set(name="test_meas_1", value=12.3, labels={"foo": "bar"})

    promexp.set(name="test_meas_1", value=12.3, labels={"foo": "foo"})

    promexp.set(name="test_meas_1", value=None, labels={"foo": "bar"})

    assert not _has_line(promexp, 'test_meas_1{foo="bar"}')


def test_promqtt_unset_new(promexp: PrometheusExporter) -> None:
    """Setting a value of a registered metric that was never set has no effect."""

    promexp.register(
        name="test_meas_1", datatype=MetricTypeEnum.GAUGE, helpstr="yeah", timeout=12
    )

    promexp.set(name="test_meas_1", value=None, labels={"foo": "bar"})

    assert not _has_line(promexp, 'test_meas_1{foo="bar"}')


def test_promqtt_not_registered(promexp: PrometheusExporter) -> None:
    """Setting a value to a not registered measurement raises an exception."""

    with pytest.raises(UnknownMeasurementException):
        promexp.set(name="test_meas_2", value=12.3, labels={})


def test_promqtt_timeout(monkeypatch, promexp: PrometheusExporter) -> None:
    """Check if timed out items are correctly removed."""

    promexp.register(
        name="test_meas_1", datatype=MetricTypeEnum.GAUGE, helpstr="yeah1", timeout=12
    )

    promexp.register(
        name="test_meas_2", datatype=MetricTypeEnum.GAUGE, helpstr="yeah2", timeout=0
    )

    # create dummy functions returning the current time or time 13s in the
    # future to fake timeout.
    def tm_now():
        return datetime(year=2023, month=8, day=7, hour=12, minute=30, second=0)

    def tm_13s():
        return tm_now() + timedelta(seconds=13)

    monkeypatch.setattr("promqtt.promexp.metric_inst.get_current_time", tm_now)

    promexp.set(name="test_meas_1", value=12.3, labels={"foo": "bar"})

    # make sure it is rendered to the output
    assert _has_line(promexp, 'test_meas_1{foo="bar"} 12.3')

    monkeypatch.setattr("promqtt.promexp.metric_inst.get_current_time", tm_13s)

    # make sure it is not rendered to the output anymore
    assert not _has_line(promexp, 'test_meas_1{foo="bar"} 12.3')

    # as there was only one item, also make sure that the header is removed
    # assert not _has_line(promexp, "# HELP yeah1")


def test_promexp_hide_empty_metrics():
    """Ensure that if hide_empty_metrics is set, that the headers of an empty metric
    are not present in the output."""

    promexp = PrometheusExporter(hide_empty_metrics=True)

    promexp.register(name="test1", datatype=MetricTypeEnum.GAUGE, helpstr="helpstr1")
    promexp.register(name="test2", datatype=MetricTypeEnum.GAUGE, helpstr="helpstr2")

    promexp.set(name="test1", labels={"foo": "bar"}, value=42)

    # has metric instance, so header should be in output
    assert _has_line(promexp, "# HELP test1 helpstr1")
    assert _has_line(promexp, "# TYPE test1 gauge")
    # no metric instance, so should not appear in output
    assert not _has_line(promexp, "# HELP test2 helpstr2")
    assert not _has_line(promexp, "# TYPE test2 gause")


def test_promexp_show_empty_metrics():
    """Ensure that if hide_empty_metrics is not set, that the headers of an empty metric
    are still present in the output."""

    promexp = PrometheusExporter(hide_empty_metrics=False)

    promexp.register(name="test1", datatype=MetricTypeEnum.GAUGE, helpstr="helpstr1")
    promexp.register(name="test2", datatype=MetricTypeEnum.GAUGE, helpstr="helpstr2")

    promexp.set(name="test1", labels={"foo": "bar"}, value=42)

    # has metric instance, so header should be in output
    assert _has_line(promexp, "# HELP test1 helpstr1")
    assert _has_line(promexp, "# TYPE test1 gauge")
    # no metric instance, but header shall still appear in output
    assert _has_line(promexp, "# HELP test2 helpstr2")
    assert _has_line(promexp, "# TYPE test2 gauge")
