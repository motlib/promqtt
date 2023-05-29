"""Client for receiving messages from MQTT and parsing them and publishing them
for prometheus."""

import logging

from ..cfgmodel import MessageConfig, MetricModel, PromqttConfig, TypeConfig
from .mapping import Mapping
from .msghdlr import MessageHandler

logger = logging.getLogger(__name__)


class MqttPrometheusBridge:  # pylint: disable=too-few-public-methods
    """Client for receiving messages from MQTT and parsing them and publishing
    them for prometheus."""

    # Name of MQTT connection state metric
    MQTT_CONN_STATE_METRIC = "promqtt_mqtt_conn_state"

    def __init__(self, prom_exp, cfg: PromqttConfig) -> None:
        self._prom_exp = prom_exp
        self._cfg = cfg

        self._register_measurements(cfg.metrics)
        self._load_types(cfg.types)
        self._load_msg_handlers(cfg.messages)

    def _register_measurements(self, metric_cfg: dict[str, MetricModel]) -> None:
        """Register measurements for Prometheus."""

        for name, meas in metric_cfg.items():
            logger.debug(f"Registering measurement '{name}'")

            self._prom_exp.register(
                name=name,
                datatype=meas.type,
                helpstr=meas.help,
                timeout=meas.timeout,
                with_update_counter=meas.with_update_counter,
            )

    def _load_types(self, types_cfg: dict[str, dict[str, TypeConfig]]) -> None:
        """Load the device types from configuration."""

        self._types = {}

        # loop over types
        for type_name, type_cfg in types_cfg.items():
            logger.debug(f"Instanciating type '{type_name}'")

            # create list of mappings for each type
            self._types[type_name] = [
                Mapping(
                    promexp=self._prom_exp,
                    type_name=type_name,
                    metric=metric,
                    value_exp=mapping_cfg.value,
                    label_exps=mapping_cfg.labels,
                )
                for metric, mapping_cfg in type_cfg.items()
            ]

    def _load_msg_handlers(self, msg_cfg: list[MessageConfig]):
        """Load the message handlers from configuration.

        The message handlers receive messages from one or more topics and
        process the data according to the configured device types.

        """

        self._handlers = []

        for handler_cfg in msg_cfg:
            # resolve the type handlers for each message
            type_names = handler_cfg.types
            mappings = []
            for type_name in type_names:
                mappings.extend(self._types[type_name])

            topics = handler_cfg.topics

            self._handlers.append(
                MessageHandler(
                    topics=topics, parser=handler_cfg.parser, mappings=mappings
                )
            )

            logger.debug(
                f"Instanciated message handler ({', '.join(topics)}) -> "
                f"({', '.join(type_names)})"
            )

    def handle_mqtt_message(self, msg):
        """Callback function called by the MQTT client to handle incoming MQTT
        messages."""

        try:
            for msg_handler in self._handlers:
                msg_handler.handle(msg)

        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to handle MQTT message")
