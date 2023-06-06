"""Exception classes for promexp module"""


class PrometheusExporterException(Exception):
    """Base class for all exceptions generated by the PrometheusExporter."""


class UnknownMeasurementException(PrometheusExporterException):
    """Raised when you try to set a value for a measurement not registered
    yet."""