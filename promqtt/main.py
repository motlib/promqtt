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
from .utils import StructWrapper

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

    coloredlogs.install(level=logging.DEBUG if verbose else logging.INFO)

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s %(levelname)s (%(threadName)s:%(name)s) %(message)s')

    logger.info(f'Starting {__title__} {__version__}')

    if verbose:
        logger.debug('Enabled verbose output.')


def load_config(filename):
    '''Load the configuration file.'''

    logger.info(f"Loading config file '{filename}'.")

    yaml = YAML(typ='safe')
    with open(filename, mode='r', encoding='utf-8') as fhdl:
        cfg = yaml.load(fhdl)

    return StructWrapper(cfg)


def main():
    '''Application main function'''

    # Set up logging

    verbose = bool(os.environ.get('PROMQTT_VERBOSE', ''))
    setup_logging(verbose)


    # Set up handler to terminate if we receive SIGTERM, e.g. when the user
    # presses Ctrl-C.
    signal.signal(signal.SIGTERM, sigterm_handler)

    args = parse_args()


    # load configuration

    cfgfile = os.environ.get('PROMQTT_CONFIG', 'promqtt.yml')
    cfg = load_config(cfgfile)

    promexp = PrometheusExporter()
    export_build_info(promexp, __version__)

    # Intialize and start the HTTP server

    routes = [
        Route('/metrics', 'text/plain', promexp.render),
        Route('/cfg', 'application/json', lambda: json.dumps(cfg.raw, indent=4)),
    ]

    httpsrv = HttpServer(
        netif=cfg.http_interface,
        port=cfg.http_port,
        routes=routes)
    httpsrv.start_server_thread()


    tmc = MqttPrometheusBridge(
        promexp,
        mqtt_broker=cfg.mqtt_broker,
        mqtt_port=cfg.mqtt_port,
        cfg=cfg.raw)
    tmc.loop_forever()


if __name__ == '__main__':
    main()
