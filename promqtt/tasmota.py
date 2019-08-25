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
        types = self._cfg['types']

        # push down type settings to type channels
        for typename, typ in self._cfg['types'].items():
            for name, val in typ.items():
                if not isinstance(val, dict):
                    for chname, ch in typ['channels'].items():
                        if (name not in ch):
                            ch[name] = typ[name]

        # inverit from types to devices
        for devname, dev in self._cfg['devices'].items():
            for devtype in dev['types']:
                typ = types[devtype]
                
                # update channels from type to device
                for chname, ch in typ['channels'].items():
                    if chname not in dev['channels']:
                        dev['channels'][chname] = ch

                for name, val in typ.items():
                    # all value types can be inherited, but no structures
                    if not isinstance(val, dict) and (name not in dev):
                        dev[name] = val
                        
        
        # push down device settings to channels
        for dev in self._cfg['devices'].values():
            for name, val in dev.items():
                if not isinstance(val, dict):
                    for ch in dev['channels'].values():
                        if (name not in ch):
                            ch[name] = dev[name]

        # split topic strings
        for devname, dev in self._cfg['devices'].items():
            for ch in dev['channels'].values():
                ch['topic'] = ch['topic'].split('/')


        # put name as key / value pair to devices and channels
        for devname, dev in self._cfg['devices'].items():
            dev['_dev_name'] = devname
            
            for chname, ch in dev['channels'].items():
                ch['_ch_name'] = chname
                

        import pprint
        pprint.pprint(self._cfg['devices'])
                
        #import sys
        #sys.exit(0)

        
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
        '''Check if the msg_topic (already split as list) matches the ch_topic (also
        split as list).'''
        
        if len(ch_topic) != len(msg_topic):
            return False
        
        result = all(
            ((part=='+') or (part==msg_topic[i]))
            for i, part in enumerate(ch_topic))

        return result

    
    def on_mqtt_msg(self, client, obj, msg):
        '''Handle incoming MQTT message.'''

        try:
            msg_data = {
                'raw_topic': msg.topic,
                'raw_payload': msg.payload,
                'topic': msg.topic.split('/'),
            }
        
            for dev in self._cfg['devices'].values():
                self._handle_device(dev, msg_data)
                
        except Exception as ex:
            logging.exception('fail')
            print(ex)

            
    def _handle_device(self, dev, msg_data):
        for ch in dev['channels'].values():
            if self._is_topic_matching(ch['topic'], msg_data['topic']):
                try:
                    self._handle_channel(dev, ch, msg_data)
                except Exception as ex:
                    print('failing')
                    print('ch', ch)
                    print('msg', msg_data)

            
    def _handle_channel(self, dev, ch, msg_data):
        if ch['parse'] == 'json':
            msg_data['val'] = json.loads(msg_data['raw_payload'])
        else:
            msg_data['val'] = msg_data['raw_payload']

        bind_value = ch['value'].format(dev=dev, ch=ch, msg=msg_data)

        bind_labels = {
            k.format(dev=dev, ch=ch, msg=msg_data):
            v.format(dev=dev, ch=ch, msg=msg_data)
            for k,v in ch['labels'].items()}

        bind_measurement = ch['measurement'].format(dev=dev, ch=ch, msg=msg_data)
        
        self._prom_exp.set(
            name=bind_measurement,
            value=bind_value,
            labels=bind_labels)

