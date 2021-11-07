'''Client for receiving messages from MQTT and parsing them and publishing them
for prometheus.'''

import logging

import paho.mqtt.client as mqtt

from .msg import Message
from .msghdlr import MessageHandler
from .mapping import Mapping


logger = logging.getLogger(__name__)


class MqttPrometheusBridge():
    '''Client for receiving messages from MQTT and parsing them and publishing
    them for prometheus.'''

    # Name of MQTT connection state metric
    MQTT_CONN_STATE_METRIC = 'promqtt_mqtt_conn_state'


    def __init__(self, prom_exp, cfg):
        self._prom_exp = prom_exp
        self._cfg = cfg

        self._register_measurements(cfg['metrics'])
        self._load_types(cfg['types'])
        self._load_msg_handlers(cfg['messages'])

        # register metric for MQTT connection state
        self._prom_exp.register(
            name=MqttPrometheusBridge.MQTT_CONN_STATE_METRIC,
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


    def _register_measurements(self, metric_cfg):
        '''Register measurements for Prometheus.'''

        for name, meas in metric_cfg.items():
            logger.debug(f"Registering measurement '{name}'")

            self._prom_exp.register(
                name=name,
                datatype=meas['type'],
                helpstr=meas['help'],
                timeout=meas.get('timeout', None),
                with_update_counter=meas.get('with_update_counter', False))


    def _load_types(self, types_cfg):
        '''Load the device types from configuration.'''

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
                    value_exp=mapping_cfg['value'],
                    label_exps=mapping_cfg['labels'])
                for metric, mapping_cfg in type_cfg.items()
            ]


    def _load_msg_handlers(self, msg_cfg):
        '''Load the message handlers from configuration.

        The message handlers receive messages from one or more topics and
        process the data according to the configured device types.

        '''

        self._handlers = []

        for handler_cfg in msg_cfg:
            # resolve the type handlers for each message
            type_names = handler_cfg['types']
            mappings = []
            for type_name in type_names:
                mappings.extend(self._types[type_name])

            topics = handler_cfg['topics']

            self._handlers.append(
                MessageHandler(
                    topics=topics,
                    parser=handler_cfg['parser'],
                    mappings=mappings))

            logger.debug(
                f"Instanciated message handler ({', '.join(topics)}) -> "
                f"({', '.join(type_names)})")


    def loop_forever(self):
        '''Run infinite loop to receive messages from MQTT broker'''

        self._mqttc.loop_forever()


    def _on_message(self, client, obj, msg):
        '''Callback function called by the MQTT client to handle incoming MQTT
        messages.'''

        del client
        del obj

        try:
            msg = Message(msg.topic, msg.payload)
            logger.debug(f"Received message: {msg}")

            for msg_handler in self._handlers:
                msg_handler.handle(msg)

        except Exception: # pylint: disable=broad-except
            logger.exception('Failed to handle MQTT message')


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
            name=MqttPrometheusBridge.MQTT_CONN_STATE_METRIC,
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
            name=MqttPrometheusBridge.MQTT_CONN_STATE_METRIC,
            labels={'broker': self.broker, 'port': self.port},
            value=0)
