'''Application main implementation'''

import json
import logging
import os
import signal
import sys

import coloredlogs

from .__version__ import __title__, __version__
from .httpsrv import HttpServer, Route
from .promexp import PrometheusExporter
from .promqtt import MqttPrometheusBridge
from .utils import str_to_bool, AbstractConfig


logger = logging.getLogger(__name__)


class AppConfig(AbstractConfig): # pylint: disable=too-few-public-methods
    '''Application configuration'''

    cfg_schema = 'schema.yml'


def sigterm_handler(signum, stack_frame):
    '''Handle the SIGTERM signal by shutting down.'''

    del signum
    del stack_frame

    logger.info('Terminating promqtt. Bye!')
    sys.exit(0)


def export_build_info(promexp, version):
    '''Export build information for prometheus.'''

    promexp.register(
        name='promqtt_build_info',
        datatype='gauge',
        helpstr='Version info',
        timeout=None)

    promexp.set(
        name='promqtt_build_info',
        value='1',
        labels={'version': version})


def setup_logging(verbose):
    '''Configure the logging.'''

    coloredlogs.install(
        level=logging.DEBUG if verbose else logging.INFO,
        fmt='%(asctime)s %(levelname)s (%(threadName)s:%(name)s) %(message)s')

    logger.info(f'Starting {__title__} {__version__}')

    if verbose:
        logger.debug('Enabled verbose output.')


def main():
    '''Application main function'''

    # Set up logging
    verbose = str_to_bool(os.environ.get('PROMQTT_VERBOSE', ''))
    setup_logging(verbose)


    # Set up handler to terminate if we receive SIGTERM, e.g. when the user
    # presses Ctrl-C.
    signal.signal(signal.SIGTERM, sigterm_handler)


    # load configuration
    cfgfile = os.environ.get('PROMQTT_CONFIG', 'promqtt.yml')
    AppConfig.cfg_filename = cfgfile

    promexp = PrometheusExporter()
    export_build_info(promexp, __version__)


    # Intialize and start the HTTP server
    routes = [
        Route(
            '/metrics',
            'text/plain',
            promexp.render),
        Route(
            '/cfg',
            'application/json',
            lambda: json.dumps(AppConfig.raw, indent=4)),
    ]

    httpsrv = HttpServer(
        netif=AppConfig.http.interface,
        port=AppConfig.http.port,
        routes=routes)
    httpsrv.start_server_thread()


    tmc = MqttPrometheusBridge(
        promexp,
        cfg=AppConfig.raw)
    tmc.loop_forever()


if __name__ == '__main__':
    main()
