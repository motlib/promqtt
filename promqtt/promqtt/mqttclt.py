"""Client for receiving messages from MQTT and parsing them and publishing them
for prometheus."""

import logging

import paho.mqtt.client as mqtt

from ..cfgmodel import MqttModel
from .msg import Message

logger = logging.getLogger(__name__)


class MqttClient: # pylint: disable=too-few-public-methods
    """Client for receiving messages from MQTT."""

    # Name of MQTT connection state metric
    MQTT_CONN_STATE_METRIC = "promqtt_mqtt_conn_state"

    def __init__(self, prom_exp, cfg: MqttModel, promqtt) -> None:
        self._prom_exp = prom_exp
        self._cfg: MqttModel = cfg
        self._promqtt = promqtt

        # register metric for MQTT connection state
        self._prom_exp.register(
            name=MqttClient.MQTT_CONN_STATE_METRIC,
            datatype="gauge",
            helpstr="Connection state of the connection to the MQTT broker",
        )

        self._setup_mqtt_client()

    def _setup_mqtt_client(self) -> None:
        """Configure MQTT client and establish connection"""

        logger.info(
            f"Connecting to MQTT broker at {self._cfg.broker}:{self._cfg.port}."
        )

        self._mqttc = mqtt.Client()

        # register callbacks
        self._mqttc.on_message = self._on_message
        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_disconnect = self._on_disconnect

        self._mqttc.connect(host=self._cfg.broker, port=self._cfg.port)
        logger.info(
            f"Connection to MQTT broker {self._cfg.broker}:{self._cfg.port} established."
        )

    def loop_forever(self) -> None:
        """Run infinite loop to receive messages from MQTT broker"""

        self._mqttc.loop_forever()

    def _on_message(self, client, obj, msg) -> None:
        """Callback function called by the MQTT client to handle incoming MQTT
        messages."""

        del client
        del obj

        msg = Message(msg.topic, msg.payload)
        logger.debug(f"Received message: {msg}")

        self._promqtt.handle_mqtt_message(msg)

    def _on_connect(self, client, userdata, flags, result) -> None:
        """Callback function called by the MQTT client to inform about establishing a
        connection to a broker."""

        del client
        del userdata
        del flags

        logger.info(
            f"Connected to {self._cfg.broker}:{self._cfg.port} "
            f"with result {result} ({mqtt.error_string(result)})"
        )

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self._mqttc.subscribe(self._cfg.topic)
        logger.debug(f"Subscribed to '{self._cfg.topic}'.")

        self._prom_exp.set(
            name=MqttClient.MQTT_CONN_STATE_METRIC,
            labels={"broker": self._cfg.broker, "port": self._cfg.port},
            value=1,
        )

    def _on_disconnect(self, client, userdata, result) -> None:
        """Callback function called by the MQTT client when the connection to a broker
        is terminated."""

        del client
        del userdata

        logger.info(
            f"Disconnected from {self._cfg.broker}:{self._cfg.port} "
            f"with result {result} ({mqtt.error_string(result)})"
        )

        self._prom_exp.set(
            name=MqttClient.MQTT_CONN_STATE_METRIC,
            labels={"broker": self._cfg.broker, "port": self._cfg.port},
            value=0,
        )
