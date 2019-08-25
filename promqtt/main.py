import argparse
import json
import logging
import os
import signal
import sys

from promqtt.__version__ import __title__, __version__
from promqtt.prom import PrometheusExporter
from promqtt.tasmota import TasmotaMQTTClient

from promqtt.configer import prepare_argparser, eval_cfg
from promqtt.cfgdesc import cfg_desc


def sigterm_handler(signum, stack_frame):
    logging.info('Terminating promqtt. Bye!')
    os._exit(0)
    

def parse_args():
    parser = argparse.ArgumentParser(
        description="Tasmota MQTT to Prometheus exporter.")
    
    prepare_argparser(cfg_desc, parser)

    return parser.parse_args()


def export_build_info(pe, title, version):
    pe.register(
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
    
    # currently we do not load a config file
    filecfg = {}
    cfg = eval_cfg(cfg_desc, filecfg, os.environ, args)
    
    setup_logging(cfg['verbose'])
    
    signal.signal(signal.SIGTERM, sigterm_handler)

    pe = PrometheusExporter(http_cfg=cfg['http'])
    export_build_info(pe, __title__, __version__)
    pe.start_server_thread()

    tmc = TasmotaMQTTClient(pe, mqtt_cfg=cfg['mqtt'], cfgfile=cfg['cfgfile'])
    tmc.loop_forever()
    
if __name__ == '__main__':
    main()
