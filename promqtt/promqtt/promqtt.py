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

    def __init__(self, prom_exp, mqtt_broker, mqtt_port, cfg):
        self._prom_exp = prom_exp

        self._register_measurements(cfg['metrics'])
        self._load_types(cfg['types'])
        self._load_msg_handlers(cfg['messages'])

        logger.info(
            f'Connecting to MQTT broker at {mqtt_broker}:{mqtt_port}.')

        self._mqttc = mqtt.Client()

        # register callback for received messages
        self._mqttc.on_message = self.on_mqtt_msg

        self._mqttc.connect(host=mqtt_broker, port=mqtt_port)

        logger.info('Connection to MQTT broker established.')

        # Currently we subscribe to everything and later filter out the messages
        # we are interested in.
        sub_topic = '#'
        self._mqttc.subscribe(sub_topic)

        logger.debug(f"MQTT client subscribing to '{sub_topic}'.")


    def _register_measurements(self, metric_cfg):
        '''Register measurements for prometheus.'''

        for name, meas in metric_cfg.items():
            logger.debug(f"Registering measurement '{name}'")
            self._prom_exp.register(
                name=name,
                datatype=meas['type'],
                helpstr=meas['help'],
                timeout=meas.get('timeout', None))



    def _load_types(self, types_cfg):
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


    def on_mqtt_msg(self, client, obj, msg):
        '''Handle incoming MQTT message.'''

        del client
        del obj

        try:
            msg = Message(msg.topic, msg.payload)
            logger.debug(f"Received message: {msg}")

            for msg_handler in self._handlers:
                msg_handler.handle(msg)

        except Exception: # pylint: disable=broad-except
            logger.exception('Failed to handle MQTT message')
