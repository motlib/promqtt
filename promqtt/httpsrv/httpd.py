"""Implementation of the threaded HTTP server"""

import logging
from http.server import ThreadingHTTPServer
from threading import Thread

from .reqhdlr import RouteHttpRequestHandler

logger = logging.getLogger(__name__)


class HttpServer:
    """Implementation of the HTTP server"""

    def __init__(self, netif, port, routes):
        self._netif = netif
        self._port = port
        self._routes = routes

    @property
    def routes(self):
        """Return the routes"""

        return self._routes

    def _run_http_server(self):
        """Start the http server to serve the prometheus data. This function
        does not return."""

        httpd = ThreadingHTTPServer((self._netif, self._port), RouteHttpRequestHandler)

        # we attach our own instance to the server object, so that the request
        # handler later can access it.
        httpd.srv = self

        httpd.serve_forever()

    def start_server_thread(self):
        """Create a thread to run the http server serving the prometheus data."""

        logger.info(f"Starting http server on {self._netif}:{self._port}.")

        srv_thread = Thread(
            target=self._run_http_server, name="http_server", daemon=True
        )
        srv_thread.start()
