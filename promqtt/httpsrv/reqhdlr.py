"""Handler for a single HTTP request"""

from http.server import BaseHTTPRequestHandler


class RouteHttpRequestHandler(BaseHTTPRequestHandler):
    """Request handler serving the prometheus data"""

    def find_route(self):
        """Find a suitable route to handle the request. If no route can be found,
        return None."""

        for route in self.server.srv.routes:  # type: ignore
            if route.can_handle(self.path):
                return route

        return None

    def do_GET(self) -> None:  # pylint: disable=invalid-name
        """Handler for GET requests"""

        route = self.find_route()

        if route is not None:
            self.send_response(200)
            self.send_header("Content-type", f"{route.content_type}; charset=utf-8")
            self.end_headers()

            response = route.handler()

            self.wfile.write(response.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"URL not found. Please use /metrics path.")
