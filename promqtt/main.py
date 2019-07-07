import argparse
import json
import logging
import os
import signal
import sys

import paho.mqtt.client as mqtt

from promqtt.__version__ import __title__, __version__
from promqtt.prom import PrometheusExporter
from promqtt.tasmota import TasmotaMQTTClient

from promqtt.configer import prepare_argparser, eval_cfg


cfgdef = {
    'http.interface': {
        'type': str,
        'help': 'Interface to bind the http server to.',
        'default': '127.0.0.1',
    },
    'http.port': {
        'type': int,
        'help': 'TCP port for the http server.',
        'default': 8086,
    },
    'mqtt.broker': {
        'type': str,
        'help': 'MQTT broker hostname',
        'default': 'mqtt',
    },
    'mqtt.port': {
        'type': str,
        'help': 'MQTT broker port number',
        'default': 1883,
    },
    'mqtt.prefix': {
        'type': str,
        'help': 'MQTT topic prefix to skip',
        'default': 'tasmota',
    },
    'verbose': {
        'type': bool,
        'help': 'Verbose (debug) output.',
        'default': False
    },
}


def sigterm_handler(signum, stack_frame):
    logging.info('Terminating promqtt. Bye!')
    os._exit(0)
    

def parse_args():
    parser = argparse.ArgumentParser(
        description="Tasmota MQTT to Prometheus exporter.")
    
    prepare_argparser(cfgdef, parser)

    return parser.parse_args()


def export_build_info(pe, title, version):
    pe.reg(
        name='tasmota_build_info',
        datatype='gauge',
        helpstr='Version info',
        timeout=None)

    pe.set(
        name='tasmota_build_info',
        value='1',
        labels={'version': version})

def setup_logging(verbose):
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='[%(levelname)s] (%(threadName)s) %(message)s')
    
    logging.info('Starting {0} {1}'.format(
        __title__,
        __version__))    
    
    
def main():
    args = parse_args()

    filecfg = {}
    cfg = eval_cfg(cfgdef, filecfg, os.environ, args)
    
    setup_logging(cfg['verbose'])
    
    signal.signal(signal.SIGTERM, sigterm_handler)

    pe = PrometheusExporter(
        http_iface=cfg['http']['interface'],
        http_port=cfg['http']['port'])
    export_build_info(pe, __title__, __version__)
    pe.start_server_thread()

    msg = 'Connecting to MQTT broker at {broker}:{port}.'
    logging.info(msg.format(**cfg['mqtt']))
    mqttc = mqtt.Client()
    mqttc.connect(
        host=cfg['mqtt']['broker'],
        port=cfg['mqtt']['port'])

    tmc = TasmotaMQTTClient(mqttc, pe, prefix=cfg['mqtt']['prefix'])

    logging.debug('Start to run mqtt loop.')
    mqttc.loop_forever()
    
if __name__ == '__main__':
    main()
