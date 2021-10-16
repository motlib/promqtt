import argparse
import json
import logging
import os
import signal
import sys

from ruamel.yaml import YAML

from promqtt.__version__ import __title__, __version__
from promqtt.cfgdesc import cfg_desc
from promqtt.configer import prepare_argparser, eval_cfg
from promqtt.http import HttpServer
from promqtt.prom import PrometheusExporter
from promqtt.tasmota import TasmotaMQTTClient


logger = logging.getLogger(__name__)


def sigterm_handler(signum, stack_frame):
    '''Handle the SIGTERM signal by shutting down.'''

    logger.info('Terminating promqtt. Bye!')
    os._exit(0)


def parse_args():
    '''Set up the command-line parser and parse arguments.'''

    parser = argparse.ArgumentParser(
        description="Tasmota MQTT to Prometheus exporter.")

    prepare_argparser(cfg_desc, parser)

    return parser.parse_args()


def export_build_info(pe, title, version):
    '''Export build information for prometheus.'''

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
    '''Configure the logging.'''

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s %(levelname)s (%(threadName)s:%(name)s) %(message)s')

    logger.info(f'Starting {__title__} {__version__}')


def main():
    signal.signal(signal.SIGTERM, sigterm_handler)

    args = parse_args()

    # currently we do not load a config file
    filecfg = {}
    cfg = eval_cfg(cfg_desc, filecfg, os.environ, args)
    setup_logging(cfg['verbose'])


    # load device configuration
    yaml = YAML(typ='safe')
    with open(cfg['cfgfile']) as f:
        devcfg = yaml.load(f)


    pe = PrometheusExporter()
    export_build_info(pe, __title__, __version__)

    routes = {
        '/metrics': {
            'type': 'text/plain',
            'fct': pe.render
        },
        '/cfg_json': {
            'type': 'application/json',
            'fct': lambda: json.dumps(cfg, indent=4)
        },
        '/devcfg_json': {
            'type': 'application/json',
            'fct': lambda: json.dumps(devcfg, indent=4)
        },
    }

    httpsrv = HttpServer(http_cfg=cfg['http'], routes=routes)
    httpsrv.start_server_thread()

    tmc = TasmotaMQTTClient(pe, mqtt_cfg=cfg['mqtt'], cfg=devcfg)
    tmc.loop_forever()


if __name__ == '__main__':
    main()
