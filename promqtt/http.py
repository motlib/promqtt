import logging
from threading import Thread

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


logger = logging.getLogger(__name__)


class PromHttpRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in self.server.srv.routes:
            route = self.server.srv.routes[self.path]

            self.send_response(200)
            self.send_header('Content-type', route['type'])
            self.end_headers()

            self.wfile.write(route['fct']().encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'URL not found. Please use /metrics path.')


class HttpServer():
    def __init__(self, http_cfg, routes):
        self._http_cfg = http_cfg
        self._routes = routes


    @property
    def routes(self):
        return self._routes


    def _run_http_server(self):
        '''Start the http server to serve the prometheus data. This function
        does not return.'''

        httpd = ThreadingHTTPServer(
            (self._http_cfg['interface'], self._http_cfg['port']),
            PromHttpRequestHandler)

        # we attach our own instance to the server object, so that the request
        # handler later can access it.
        httpd.srv = self

        httpd.serve_forever()


    def start_server_thread(self):
        '''Create a thread to run the http server serving the prometheus data.'''

        logger.info(
            "Starting http server on "
            f"{self._http_cfg['interface']}:{self._http_cfg['port']}.")

        srv_thread = Thread(
            target=self._run_http_server,
            name='http_server',
            daemon=True)
        srv_thread.start()
