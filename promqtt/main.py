'''Application main implementation'''

import argparse
import json
import logging
import os
import signal
import sys

import coloredlogs
from ruamel.yaml import YAML

from .__version__ import __title__, __version__
from .cfgdesc import cfg_desc
from .configer import prepare_argparser, eval_cfg
from .httpsrv import HttpServer, Route
from .promexp import PrometheusExporter
from .promqtt import MqttPrometheusBridge


logger = logging.getLogger(__name__)


def sigterm_handler(signum, stack_frame):
    '''Handle the SIGTERM signal by shutting down.'''

    del signum
    del stack_frame

    logger.info('Terminating promqtt. Bye!')
    sys.exit(0)


def parse_args():
    '''Set up the command-line parser and parse arguments.'''

    parser = argparse.ArgumentParser(
        description="Tasmota MQTT to Prometheus exporter.")

    prepare_argparser(cfg_desc, parser)

    return parser.parse_args()


def export_build_info(promexp, version):
    '''Export build information for prometheus.'''

    promexp.register(
        name='tasmota_build_info',
        datatype='gauge',
        helpstr='Version info',
        timeout=None)

    promexp.set(
        name='tasmota_build_info',
        value='1',
        labels={'version': version})


def setup_logging(verbose):
    '''Configure the logging.'''

    coloredlogs.install()

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s %(levelname)s (%(threadName)s:%(name)s) %(message)s')

    logger.info(f'Starting {__title__} {__version__}')

def setup_http_server():
    routes = [
        Route('/metrics', 'text/plain', promexp.render),
        Route('/cfg', 'application/json', lambda: json.dumps(cfg, indent=4)),
        Route('/devcfg', 'application/json', lambda: json.dumps(devcfg, indent=4)),
    ]

    httpsrv = HttpServer(
        netif=cfg['http']['interface'],
        port=cfg['http']['port'],
        routes=routes)
    httpsrv.start_server_thread()



def main():
    '''Application main function'''

    # Set up handler to terminate if we receive SIGTERM, e.g. when the user
    # presses Ctrl-C.
    signal.signal(signal.SIGTERM, sigterm_handler)

    args = parse_args()

    # currently we do not load a config file
    filecfg = {}
    cfg = eval_cfg(cfg_desc, filecfg, os.environ, args)
    setup_logging(cfg['verbose'])

    # load device configuration
    yaml = YAML(typ='safe')
    with open(cfg['cfgfile'], mode='r', encoding='utf-8') as fhdl:
        devcfg = yaml.load(fhdl)

    promexp = PrometheusExporter()
    export_build_info(promexp, __version__)

    # Intialize and start the HTTP server
    setup_http_server()

    tmc = MqttPrometheusBridge(promexp, mqtt_cfg=cfg['mqtt'], cfg=devcfg)
    tmc.loop_forever()


if __name__ == '__main__':
    main()
