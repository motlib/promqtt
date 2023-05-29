"""Configuration file datamodel"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Extra, Field, root_validator

from .httpsrv.config import HttpServerConfig

# pylint: disable=too-few-public-methods


class MqttModel(BaseModel):
    """MQTT broker settings"""

    broker: str = Field(description="The hostname of the MQTT broker")
    port: int = Field(1883, description="The MQTT port to connect to.")
    topic: str = Field("#", description="The topic to subscribe")

    class Config:
        """Pydantic configuration"""

        extra = Extra.forbid


class MetricTypeEnum(Enum):
    """Enumeration of metric types"""

    GAUGE = "gauge"
    COUNTER = "counter"


class MetricModel(BaseModel):
    """Configuration of a metric"""

    type: MetricTypeEnum = Field(description="Metric type")
    help: str = Field("", description="Metric help text")
    timeout: int = Field(
        0,
        description=(
            "Timeout time in seconds of this metric. When the metric has not "
            "been updated for this time, it is removed from Prometheus output."
        ),
    )
    with_update_counter: bool = Field(False, description="Enable update counter metric")

    class Config:
        """Pydantic configuration"""

        extra = Extra.forbid


class TypeConfig(BaseModel):
    """Configuration of a type / device"""

    value: str = Field(
        description="The python expression to extract a value from the messsage"
    )
    labels: dict[str, str] = Field(description="The labels attached to a metric")

    class Config:
        """Pydantic configuration"""

        extra = Extra.forbid


class ParserTypeEnum(Enum):
    """Types of MQTT message parsers"""

    JSON = "json"


class MessageConfig(BaseModel):
    """Message configuration. This configures which types process which MQTT messages."""

    topics: list[str] = Field(description="The topics which receive relevant messages")
    types: list[str] = Field(description="The types that process the messages")
    parser: ParserTypeEnum = Field(
        ParserTypeEnum.JSON,
        description="The parser that converts the incoming message to a data structure.",
    )

    class Config:
        """Pydantic configuration"""

        extra = Extra.forbid


class PromqttConfig(BaseModel):
    """Configuration file data model for promqtt"""

    mqtt: MqttModel

    http: HttpServerConfig

    metrics: dict[str, MetricModel]

    types: dict[str, dict[str, TypeConfig]]

    messages: list[MessageConfig]

    class Config:
        """Pydantic configuration"""

        extra = Extra.forbid

    @root_validator
    def check_references( # pylint: disable=no-self-argument
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        """Pydantic validator to check internal references in config file"""

        typescfg = values["types"]
        metricscfg = values["metrics"]

        # Check that metrics referenced in types exist

        for type_name, metric in typescfg.items():
            for metric_name in metric.keys():
                assert metric_name in metricscfg, (
                    f"Metric '{metric_name}' not declared. "
                    f"Referenced in type '{type_name}'."
                )

        # Check that types referenced in messages exist

        msgcfgs: list[MessageConfig] = values["messages"]

        for index, msgcfg in enumerate(msgcfgs):
            for typ in msgcfg.types:
                assert typ in typescfg, (
                    f"Type '{typ}' not configured. "
                    f"Referenced in message no. {index}."
                )

        return values
