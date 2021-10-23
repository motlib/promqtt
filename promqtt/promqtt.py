'''Client for receiving messages from MQTT and parsing them and publishing them
for prometheus.'''

import json
import logging
import re

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


def _is_topic_matching(ch_topic, msg_topic):
    '''Check if the msg_topic (already split as list) matches the ch_topic (also
    split as list).'''

    if len(ch_topic) != len(msg_topic):
        return False

    result = all(
        part in ('+', msg_topic[i])
        for i, part in enumerate(ch_topic))

    return result


class MessageHandler():
    '''A message handler receives a message from MQTT, parses the contents and
    hands it over to the mapping instances.'''

    def __init__(self, topics, parser, mappings):
        self._topics = topics
        self._parser = parser
        self._mappings = mappings


    def _can_handle_topic(self, topic):
        '''Check if a topic can be handled. Checks for both literal matches and
        regex topic patterns, i.e. topics starting with the prefix 're:'.'''

        for handled_topic in self._topics:
            if handled_topic.startswith('re:'):
                regex = handled_topic[3:]
                match = re.match(regex, topic)
                if match:
                    return True
            elif topic == handled_topic:
                return True

        return False


    def handle(self, msg):
        '''Handle a message received from MQTT.

        This first checks if the handler can handle this message. If not it
        immediately returns. If yes, it parses the message payload if not
        already done so and forwards it to the mapping instances.

        '''

        if not self._can_handle_topic(msg.topic):
            return

        logger.debug(f'Handler {self} handles {msg.topic}')


        # If the data of the message has not yet been parsed, do it now.
        if msg.data is None:
            msg.parse(self._parser)

        for mapping in self._mappings:
            mapping.handle_msg_data(msg)


    def __str__(self):
        return f"MessageHandler([{', '.join(self._topics)}])"


class Mapping():
    '''A mapping takes data from a message received from MQTT, extracts a value
    and possibly also values and submits the results to the prometheus
    exporter.'''

    def __init__(self, promexp, value_exp, label_exps, metric):
        self._promexp = promexp
        self._value_exp = value_exp
        self._label_exps = label_exps
        self._metric = metric


    def handle_msg_data(self, msg):
        '''Handle a message received from MQTT'''

        try:
            value = self._value_exp.format(
                msg=msg)
        except KeyError:
            logger.error(f"Cannot apply value expression '{self._value_exp}'. Message: {msg}")
            return

        # calculate labels
        bind_labels = {
            k.format(msg=msg):
            v.format(msg=msg)
            for k,v in self._label_exps.items()}

        self._promexp.set(
            name=self._metric,
            labels=bind_labels,
            value=value)

    def __str__(self):
        return f'Mapping(metric={self._metric})'


class Message():
    '''Encapsulate data of a message received from MQTT'''

    def __init__(self, topic, payload):
        self._topic = topic
        self._topic_list = topic.split('/')
        self._payload = payload
        self._data = None

    @property
    def topic(self):
        '''Return the topic string'''
        return self._topic

    @property
    def payload(self):
        '''Return the raw message payload, i.e. a string'''
        return self._payload

    @property
    def data(self):
        '''Return the parsed data of the message, e.g. the parsed JSON
        content'''

        return self._data

    @property
    def topic_list(self):
        '''Returns the topic as a list of topic components'''
        return self._topic_list


    def parse(self, parser):
        '''Parse the message payload with the given parser / format.'''

        if parser == 'json':
            self._data = json.loads(self._payload)
        else:
            raise Exception(f"Unknown message parser '{parser}'")


    def __str__(self):
        return f'{self.topic}: {self.payload}'


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
