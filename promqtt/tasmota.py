import json
import logging

import paho.mqtt.client as mqtt


class TasmotaMQTTClient():
    def __init__(self, prom_exp, mqtt_cfg):
        self._prom_exp = prom_exp

        self._timeout = mqtt_cfg['timeout']
        msg = 'Setting MQTT timeout to {timeout}s.'
        logging.debug(msg.format(**mqtt_cfg))
        
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
        sub_topic = prefix + '/#'
        self._mqttc.subscribe(sub_topic)
        msg = "Tasmota client subscribing to '{0}'."
        logging.debug(msg.format(sub_topic))

        
    def loop_forever(self):
        self._mqttc.loop_forever()
        
        
    def _register_measurements(self):
        '''Register measurements for prometheus.'''

        # tele_SENSOR
        self._prom_exp.register(
            name='tasmota_temperature',
            datatype='gauge',
            helpstr='Temperature in degree celsius',
            timeout=self._timeout)
        
        self._prom_exp.register(
            name='tasmota_pressure',
            datatype='gauge',
            helpstr='Air pressure in millibar',
            timeout=self._timeout)
        
        self._prom_exp.register(
            name='tasmota_rel_humidity',
            datatype='gauge',
            helpstr='Relative humidity in percent',
            timeout=self._timeout)

        # tele_STATE
        self._prom_exp.register(
            name='tasmota_vcc',
            datatype='gauge',
            helpstr='Supply voltate of tasmota node',
            timeout=self._timeout)

        self._prom_exp.register(
            name='tasmota_wifi_rssi',
            datatype='gauge',
            helpstr='Relative wifi signal strength indicator',
            timeout=self._timeout)
        
        self._prom_exp.register(
            name='tasmota_power',
            datatype='gauge',
            helpstr='Power state of sonoff switch.',
            timeout=self._timeout)

        
    def _handle_data(self, area, info, node_name, payload):
        '''Try to find a handler function to process received message.'''
        
        fctname = '_handle_{area}_{info}'.format(area=area, info=info)
        
        if hasattr(self, fctname):
            try:
                fct = getattr(self, fctname)
                fct(node_name, payload)
            except Exception as ex:
                logging.exception("MQTT handler failure in '{0}'.".format(fctname))
        else:
            logging.debug("No handler '{0}' available.".format(fctname))
            
        
    def on_mqtt_msg(self, client, obj, msg):
        '''Handle incoming MQTT message.'''
        
        tparts = msg.topic.split('/')

        # check for the expected prefix
        for i,name in enumerate(self._prefix):
            if tparts[i] != name:
                return

        # discard prefix
        tparts = tparts[len(self._prefix):]

        area = tparts[0] # stats, tele, ...
        node_name = tparts[1] # the node name
        info = tparts[2] # SENSOR, STATE, ...

        self._handle_data(area, info, node_name, msg.payload)

        
    def _handle_tele_SENSOR(self, node_name, payload):
        data = json.loads(payload)

        #tasmota/tele/sens-br1/SENSOR
        # {"Time":"2019-06-29T14:27:51","BME280":{"Temperature":25.5,
        #  "Humidity":76.0,"Pressure":991.2
        # },"PressureUnit":"hPa","TempUnit":"C"}
        if 'BME280' in data:
            self._prom_exp.set(
                name='tasmota_temperature',
                value=data['BME280']['Temperature'],
                labels={'node': node_name, 'sensor': 'BME280'})
            self._prom_exp.set(
                name='tasmota_rel_humidity',
                value=data['BME280']['Humidity'],
                labels={'node': node_name, 'sensor': 'BME280'})
            self._prom_exp.set(
                name='tasmota_pressure',
                value=data['BME280']['Pressure'],
                labels={'node': node_name, 'sensor': 'BME280'})
        else:
            msg = "Recevied message for unsupported sensor from node '{0}'."
            logging.warning(msg.format(node_name))

            
    def _handle_tele_STATE(self, node_name, payload):
        #tasmota/tele/sens-br1/STATE
        #b'{"Time":"2019-06-29T15:27:51","Uptime":"13T05:21:05","Vcc":2.818,
        #   "SleepMode":"Dynamic","Sleep":50,"LoadAvg":19,
        #   "Wifi":{"AP":1,"SSId":"ChaosWLAN","BSSId":"7C:DD:90:D4:30:43",
        #     "Channel":7,"RSSI":96,"LinkCount":2,"Downtime":"5T14:55:50"}}'
        data = json.loads(payload)
    
        self._prom_exp.set(
            name='tasmota_vcc',
            value=data['Vcc'],
            labels={'node': node_name})
        self._prom_exp.set(
            name='tasmota_wifi_rssi',
            value=data['Wifi']['RSSI'],
            labels={'node': node_name})
        
        if 'POWER' in data:
            value = 1 if data['POWER'] == 'ON' else 0
            self._prom_exp.set(
                name='tasmota_power',
                value=value,
                labels={'node': node_name})
                   
