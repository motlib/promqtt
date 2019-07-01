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

