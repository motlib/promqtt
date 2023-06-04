"""Application main implementation"""

import json
import logging
import os
import signal
import sys
from pathlib import Path

import yaml
from logfmter import Logfmter

from .cfgmodel import MetricTypeEnum, PromqttConfig
from .httpsrv import HttpServer, Route
from .metadata import APPNAME, VERSION
from .promexp import PrometheusExporter
from .promqtt import MqttClient, MqttPrometheusBridge
from .utils import str_to_bool

logger = logging.getLogger(__name__)


def sigterm_handler(signum: int, stack_frame) -> None:
    """Handle the SIGTERM signal by shutting down."""

    del signum
    del stack_frame

    logger.info("Terminating promqtt. Bye!")
    sys.exit(0)


def export_build_info(promexp: PrometheusExporter, version: str) -> None:
    """Export build information for prometheus."""

    promexp.register(
        name="promqtt_build_info",
        datatype=MetricTypeEnum.GAUGE,
        helpstr="Version info",
    )

    promexp.set(name="promqtt_build_info", value=1, labels={"version": version})


def setup_logging(verbose: bool) -> None:
    """Configure the logging."""

    handler = logging.StreamHandler()

    keys = ["when", "at"]
    if verbose:
        keys.append("code")

    handler.setFormatter(
        Logfmter(
            keys=keys, mapping={"at": "levelname", "when": "asctime", "code": "name"}
        )
    )

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        handlers=[handler],
    )

    logger.info(f"Starting {APPNAME} {VERSION}")


def load_config(filename: Path) -> PromqttConfig:
    """Load the configuration file."""

    logger.info(f"Loading config file '{filename}'.")

    with open(filename, mode="r", encoding="utf-8") as fhdl:
        data = yaml.safe_load(fhdl)
        cfg = PromqttConfig.parse_obj(data)

    return cfg


def main():
    """Application main function"""

    # Set up logging

    verbose = str_to_bool(os.environ.get("PROMQTT_VERBOSE", ""))
    setup_logging(verbose)

    # Set up handler to terminate if we receive SIGTERM, e.g. when the user
    # presses Ctrl-C.
    signal.signal(signal.SIGTERM, sigterm_handler)

    # load configuration

    cfgfile = Path(os.environ.get("PROMQTT_CONFIG", "promqtt.yml"))
    cfg = load_config(cfgfile)

    promexp = PrometheusExporter()
    export_build_info(promexp, VERSION)

    # Intialize and start the HTTP server

    routes = [
        Route("/metrics", "text/plain", promexp.render),
        Route("/cfg", "application/json", lambda: json.dumps(cfg.dict(), indent=4)),
    ]

    httpsrv = HttpServer(cfg=cfg.http, routes=routes)
    httpsrv.start_server_thread()

    tmc = MqttPrometheusBridge(promexp, cfg=cfg)

    mqttclient = MqttClient(promexp, cfg.mqtt, tmc)
    mqttclient.loop_forever()


if __name__ == "__main__":
    main()
