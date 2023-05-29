"""Implementation of the threaded HTTP server"""

import logging
from http.server import ThreadingHTTPServer
from threading import Thread

from .config import HttpServerConfig
from .reqhdlr import RouteHttpRequestHandler
from .route import Route

logger = logging.getLogger(__name__)


class HttpServer:
    """Implementation of the HTTP server"""

    def __init__(self, cfg: HttpServerConfig, routes: list[Route]) -> None:
        self._routes = routes
        self._cfg = cfg

    @property
    def routes(self) -> list[Route]:
        """Return the routes"""

        return self._routes

    def _run_http_server(self) -> None:
        """Start the http server to serve the prometheus data. This function
        does not return."""

        httpd = ThreadingHTTPServer(
            (self._cfg.interface, self._cfg.port), RouteHttpRequestHandler
        )

        # we attach our own instance to the server object, so that the request
        # handler later can access it.
        httpd.srv = self  # type: ignore

        httpd.serve_forever()

    def start_server_thread(self) -> None:
        """Create a thread to run the http server serving the prometheus data."""

        logger.info(f"Starting http server on {self._cfg.interface}:{self._cfg.port}.")

        srv_thread = Thread(
            target=self._run_http_server, name="http_server", daemon=True
        )
        srv_thread.start()
