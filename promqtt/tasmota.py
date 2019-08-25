import json
import logging

import paho.mqtt.client as mqtt
from ruamel.yaml import YAML


class TasmotaMQTTClient():
    def __init__(self, prom_exp, mqtt_cfg, cfgfile):
        self._prom_exp = prom_exp

        yaml = YAML(typ='safe')

        with open(cfgfile) as f:
            self._cfg = yaml.load(f)

        self._preproc_devs()
            
        self._register_measurements()
        
        prefix = mqtt_cfg['prefix']
        while prefix.endswith('/'):
            prefix = prefix[:-1]
        self._prefix = prefix.split('/')

        
        msg = 'Connecting to MQTT broker at {broker}:{port}.'
        logging.info(msg.format(**mqtt_cfg))
        self._mqttc = mqtt.Client()
        
        # register callback for received messages
        self._mqttc.on_message = self.on_mqtt_msg
        
        self._mqttc.connect(
            host=mqtt_cfg['broker'],
            port=mqtt_cfg['port'])

        
        # we subscribe for everything below the prefix
        sub_topic = '#'
        self._mqttc.subscribe(sub_topic)
        msg = "Tasmota client subscribing to '{0}'."
        logging.debug(msg.format(sub_topic))

        
    def _preproc_devs(self):
        for dev in self._cfg['devices']:
            for ch in dev['channels']:
                ch['topic'] = ch['topic'].split('/')
        
        
    def loop_forever(self):
        self._mqttc.loop_forever()
        
        
    def _register_measurements(self):
        '''Register measurements for prometheus.'''

        for name, meas in self._cfg['measurements'].items():
            msg = 'Registering measurement {0}'
            logging.debug(msg.format(name))
            self._prom_exp.register(
                name=name,
                datatype=meas['type'], 
                helpstr=meas['help'],
                timeout=meas['timeout'] if meas['timeout'] else None)
        
    
    def _is_topic_matching(self, ch_topic, msg_topic):
        print('matching', ch_topic, 'and', msg_topic)

        if len(ch_topic) != len(msg_topic):
            return False
        
        result = all(
            ((part=='+') or (part==msg_topic[i]))
            for i, part in enumerate(ch_topic))

        print('result', result)

        return result
        
    def on_mqtt_msg(self, client, obj, msg):
        '''Handle incoming MQTT message.'''

        try:
            msg_data = {
                'raw_topic': msg.topic,
                'raw_payload': msg.payload,
                'topic': msg.topic.split('/'),
            }
        
            for dev in self._cfg['devices']:
                self._handle_device(dev, msg_data)
                
        except Exception as ex:
            logging.exception('fail')
            print(ex)

            
    def _handle_device(self, dev, msg_data):
        for ch in dev['channels']:
            if self._is_topic_matching(ch['topic'], msg_data['topic']):
                self._handle_channel(dev, ch, msg_data)

            
    def _handle_channel(self, dev, ch, msg_data):
        if ch['parse'] == 'json':
            msg_data['val'] = json.loads(msg_data['raw_payload'])
        else:
            msg_data['val'] = msg_data['raw_payload']

        value = ch['value'].format(dev=dev, ch=ch, msg=msg_data)

        bind_labels = {
            k.format(dev=dev, ch=ch, msg=msg_data):
            v.format(dev=dev, ch=ch, msg=msg_data)
            for k,v in ch['labels'].items()}
        
        self._prom_exp.set(
            name=ch['measurement'],
            value=value,
            labels=bind_labels)

