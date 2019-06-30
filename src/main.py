import json
import logging
import os
import signal
import sys
import traceback
import time

import paho.mqtt.client as mqtt

from prom import PrometheusExporter
from tasmota_mqtt import TasmotaMQTTClient



#def handle_sensor(nodename, payload):
#    data = json.loads(payload)
#
#    if 'BME280' in data:
#        pe.set(
#            name='tasmota_temperature',
#            value=data['BME280']['Temperature'],
#            labels={'node': nodename, 'sensor': 'BME280'})
#        pe.set(
#            name='tasmota_rel_humidity',
#            value=data['BME280']['Humidity'],
#            labels={'node': nodename, 'sensor': 'BME280'})
#        pe.set(
#            name='tasmota_pressure',
#            value=data['BME280']['Pressure'],
#            labels={'node': nodename, 'sensor': 'BME280'})
#    else:
#        print('Unsupported sensor.')
#
#def handle_state(nodename, payload):
#    data = json.loads(payload)
#    
#    pe.set(
#        name='tasmota_vcc',
#        value=data['Vcc'],
#        labels={'node': nodename})
#    pe.set(
#        name='tasmota_wifi_rssi',
#        value=data['Wifi']['RSSI'],
#        labels={'node': nodename})
    
# Define event callbacks
#def on_connect(client, userdata, flags, rc):
#    print("rc: " + str(rc))

#def on_message(client, obj, msg):
#
#    tparts = msg.topic.split('/')
#    #tasmota/tele/sens-br1/SENSOR
#    # {"Time":"2019-06-29T14:27:51","BME280":{"Temperature":25.5,"Humidity":76.0,"Pressure":991.2},"PressureUnit":"hPa","TempUnit":"C"}
#    try:
#        if tparts[0] == 'tasmota' and tparts[1] == 'tele' and tparts[3] == 'SENSOR':
#            handle_sensor(nodename=tparts[2], payload=msg.payload)
#
#        #tasmota/tele/sens-br1/STATE
#        #b'{"Time":"2019-06-29T15:27:51","Uptime":"13T05:21:05","Vcc":2.818,"SleepMode":"Dynamic","Sleep":50,"LoadAvg":19,
#        # "Wifi":{"AP":1,"SSId":"ChaosWLAN","BSSId":"7C:DD:90:D4:30:43","Channel":7,"RSSI":96,"LinkCount":2,"Downtime":"5T14:55:50"}}'
#        elif tparts[0] == 'tasmota' and tparts[1] == 'tele' and tparts[3] == 'STATE':
#            handle_state(nodename=tparts[2], payload=msg.payload)
#        
#            
#    except Exception as e:
#        print('EX:', e)
#        traceback.print_exc()
#    
#    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

#def on_publish(client, obj, mid):
#    print("mid: " + str(mid))
#
#def on_subscribe(client, obj, mid, granted_qos):
#    print("Subscribed: " + str(mid) + " " + str(granted_qos))
#
#def on_log(client, obj, level, string):
#    print('LOG:', string)


def sigterm_handler(signum, stack_frame):
    logging.info('Terminating promqtt. Bye!')
    sys.exit(0)

    
def main():
    logfmt = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logfmt)
    logging.info('Starting promqtt.')    

    signal.signal(signal.SIGTERM, sigterm_handler)
    
    pe = PrometheusExporter(http_iface='0.0.0.0', http_port=8000)
    pe.start_server_thread()

    mqttc = mqtt.Client()
    mqttc.connect('npi2', 1883)
    
    tmc = TasmotaMQTTClient(mqttc, pe, prefix=['tasmota'])

    logging.debug('Start to run mqtt loop.')
    mqttc.loop_forever()

    

if __name__ == '__main__':
    main()

