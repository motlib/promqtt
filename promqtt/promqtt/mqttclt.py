'''Client for receiving messages from MQTT and parsing them and publishing them
for prometheus.'''

import logging

import paho.mqtt.client as mqtt

from .msg import Message


logger = logging.getLogger(__name__)


class MqttClient():
    '''Client for receiving messages from MQTT.'''

    # Name of MQTT connection state metric
    MQTT_CONN_STATE_METRIC = 'promqtt_mqtt_conn_state'


    def __init__(self, prom_exp, cfg, promqtt):
        self._prom_exp = prom_exp
        self._cfg = cfg
        self._promqtt = promqtt

        # register metric for MQTT connection state
        self._prom_exp.register(
            name=MqttClient.MQTT_CONN_STATE_METRIC,
            datatype='gauge',
            helpstr='Connection state of the connection to the MQTT broker')

        self._setup_mqtt_client()


    @property
    def broker(self):
        '''Return the broker hostname'''

        return self._cfg['mqtt/broker']


    @property
    def port(self):
        '''Return the broker TCP port'''
        return self._cfg['mqtt/port']


    @property
    def topic(self):
        '''Return the main topic to subscribe to.'''
        return self._cfg['mqtt/topic']


    def _setup_mqtt_client(self):
        '''Configure MQTT client and establish connection'''

        logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}.")

        self._mqttc = mqtt.Client()

        # register callbacks
        self._mqttc.on_message = self._on_message
        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_disconnect = self._on_disconnect

        self._mqttc.connect(host=self.broker, port=self.port)
        logger.info(
            f'Connection to MQTT broker {self.broker}:{self.port} established.')


    def loop_forever(self):
        '''Run infinite loop to receive messages from MQTT broker'''

        self._mqttc.loop_forever()


    def _on_message(self, client, obj, msg):
        '''Callback function called by the MQTT client to handle incoming MQTT
        messages.'''

        del client
        del obj

        msg = Message(msg.topic, msg.payload)
        logger.debug(f"Received message: {msg}")

        self._promqtt.handle_mqtt_message(msg)


    def _on_connect(self, client, userdata, flags, result):
        '''Callback function called by the MQTT client to inform about establishing a
        connection to a broker.'''

        del client
        del userdata
        del flags

        logger.info(
            f"Connected to {self.broker}:{self.port} "
            f"with result {result} ({mqtt.error_string(result)})")

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self._mqttc.subscribe(self.topic)
        logger.debug(f"Subscribed to '{self.topic}'.")

        self._prom_exp.set(
            name=MqttClient.MQTT_CONN_STATE_METRIC,
            labels={'broker': self.broker, 'port': self.port},
            value=1)


    def _on_disconnect(self, client, userdata, result):
        '''Callback function called by the MQTT client when the connection to a broker
        is terminated.'''

        del client
        del userdata

        logger.info(
            f"Disconnected from {self.broker}:{self.port} "
            f"with result {result} ({mqtt.error_string(result)})")

        self._prom_exp.set(
            name=MqttClient.MQTT_CONN_STATE_METRIC,
            labels={'broker': self.broker, 'port': self.port},
            value=0)
