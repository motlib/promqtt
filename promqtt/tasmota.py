'''Client for receiving messages from MQTT and parsing them and publishing them
for prometheus.'''

import json
import logging

import paho.mqtt.client as mqtt
from promqtt.device_loader import prepare_devices


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


class TasmotaMQTTClient():
    '''Client for receiving messages from MQTT and parsing them and publishing
    them for prometheus.'''

    def __init__(self, prom_exp, mqtt_cfg, cfg):
        self._prom_exp = prom_exp

        self._cfg = cfg

        prepare_devices(cfg)

        self._register_measurements()

        logger.info(
            f'Connecting to MQTT broker at {mqtt_cfg["broker"]}:{mqtt_cfg["port"]}.')

        self._mqttc = mqtt.Client()

        # register callback for received messages
        self._mqttc.on_message = self.on_mqtt_msg

        self._mqttc.connect(
            host=mqtt_cfg['broker'],
            port=mqtt_cfg['port'])

        logger.info('Connection to MQTT broker established.')

        # Currently we subscribe to everything and later filter out the messages
        # we are interested in.
        sub_topic = '#'
        self._mqttc.subscribe(sub_topic)

        logger.debug(f"MQTT client subscribing to '{sub_topic}'.")


    def loop_forever(self):
        '''Run infinite loop to receive messages from MQTT broker'''

        self._mqttc.loop_forever()


    def _register_measurements(self):
        '''Register measurements for prometheus.'''

        for name, meas in self._cfg['measurements'].items():
            logger.debug(f'Registering measurement {name}')
            self._prom_exp.register(
                name=name,
                datatype=meas['type'],
                helpstr=meas['help'],
                timeout=meas['timeout'] if meas['timeout'] else None)




    def on_mqtt_msg(self, client, obj, msg):
        '''Handle incoming MQTT message.'''

        del client
        del obj

        try:
            msg_data = {
                'raw_topic': msg.topic,
                'raw_payload': msg.payload,
                'topic': msg.topic.split('/'),
            }

            for dev in self._cfg['devices'].values():
                self._handle_device(dev, msg_data)

        except Exception: # pylint: disable=broad-except
            logger.exception('Failed to handle MQTT message')


    def _handle_device(self, dev, msg_data):
        for channel in dev['channels'].values():
            if _is_topic_matching(channel['topic'], msg_data['topic']):
                try:
                    self._handle_channel(dev, channel, msg_data)
                except Exception: # pylint: disable=broad-except
                    logger.exception(
                        f"Failed to handle device '{dev['_dev_name']}', "
                        f"channel '{channel['_ch_name']}'.")


    def _handle_channel(self, dev, channel, msg_data):
        # Step 1: parse value
        if channel['parse'] == 'json':
            value = json.loads(msg_data['raw_payload'])
        else:
            value = msg_data['raw_payload']

        # Step 2: Extract value from payload (e.g. a specific value from JSON
        # structure) by string formatting
        try:
            value = channel['value'].format(
                dev=dev,
                channel=channel,
                msg=msg_data,
                value=value)
        except KeyError:
            logger.exception(
                f"Failed to process value access in device '{dev['_dev_name']}', "
                f"channel '{channel['_ch_name']}', expression '{channel['value']}' "
                f"for payload '{msg_data['raw_payload']}'.")
            return

        # Step 3: map string values to numeric values
        if 'map' in channel:
            if value in channel['map']:
                value = channel['map'][value]
            else:
                value = float('nan')

        # Step 4: scale
        if ('factor' in channel) or ('offset' in channel):
            try:
                value = (float(value)
                              * channel.get('factor', 1.0)
                              + channel.get('offset', 0.0))
            except Exception: # pylint: disable=broad-except
                # generate "not a number" value
                value = float('nan')

        # legacy
        msg_data['val'] = value

        bind_labels = {
            k.format(dev=dev, channel=channel, msg=msg_data):
            v.format(dev=dev, channel=channel, msg=msg_data)
            for k,v in channel['labels'].items()}

        measurement = channel['measurement'].format(
            dev=dev,
            channel=channel,
            msg=msg_data,
            value=value)

        self._prom_exp.set(
            name=measurement,
            value=value,
            labels=bind_labels)
