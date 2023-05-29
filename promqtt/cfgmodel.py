'''Configuration file datamodel'''

from pydantic import BaseModel, Field, Extra, root_validator
from enum import Enum
from typing import Any


class MqttModel(BaseModel):
    '''MQTT broker settings'''

    broker: str = Field(description="The hostname of the MQTT broker")
    port: int = Field(1883, description="The MQTT port to connect to.")
    topic: str = Field('#', description="The topic to subscribe")

class HttpModel(BaseModel):
    '''HTTP server related settings'''

    interface: str = Field("0.0.0.0", description="Interface address to listen on")

    port: int = Field(8086, description="Port number")

class MetricTypeEnum(Enum):
    GAUGE = 'gauge'
    COUNTER = 'counter'


class MetricModel(BaseModel):
    type: str = Field(description="Metric type")
    help: str = Field('', description="Metric help text")
    timeout: int = Field(0, description="Timeout time in seconds of this metric. When the metric has not been updated for this time, it is removed from Prometheus output.")
    with_update_counter: bool = Field(False, description="Enable update counter metric")

class TypeConfig(BaseModel):
    value: str = Field(description="The python expression to extract a value from the messsage")
    labels: dict[str, str] = Field(description="The labels attached to a metric")

class ParserTypeEnum(Enum):
    JSON = 'json'


class MessageConfig(BaseModel):
    '''Message configuration. This configures which types process which MQTT messages.'''

    topics: list[str] = Field(description="The topics which receive relevant messages")
    types: list[str] = Field(description="The types that process the messages")
    parser: ParserTypeEnum = Field(ParserTypeEnum.JSON, description="The parser that converts the incoming message to a data structure.")

class PromqttConfig(BaseModel):
    '''Configuration file data model for promqtt'''

    mqtt: MqttModel

    http: HttpModel

    metrics: dict[str, MetricModel]

    types: dict[str, dict[str, TypeConfig]]

    messages: list[MessageConfig]

    class Config:
        extra = Extra.forbid

    @root_validator
    def check_references(cls, values: dict[str, Any]) -> dict[str, Any]:

        typescfg = values['types']
        metricscfg = values['metrics']

        # Check that metrics referenced in types exist

        for type_name, metric in typescfg.items():
            for metric_name, metric_cfg in metric.items():
                assert metric_name in metricscfg, f"Metric '{metric_name}' not declared. Referenced in type '{type_name}'."

        # Check that types referenced in messages exist

        msgcfgs: list[MessageConfig] = values['messages']

        for index, msgcfg in enumerate(msgcfgs):
            for typ in msgcfg.types:
                assert typ in typescfg, f"Type '{typ}' not configured. Referenced in message no. {index}."

        return values
