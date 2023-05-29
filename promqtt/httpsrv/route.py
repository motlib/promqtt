"""Implementation of the HTTP server to serve prometheus data."""

from typing import Callable


class Route:
    """Represents a route, i.e. a URL path and the corresponding function to
    generate the web server response."""

    def __init__(self, path: str, content_type: str, handler: Callable[[], str]):
        self._path = path
        self._content_type = content_type
        self._handler = handler

    @property
    def content_type(self) -> str:
        """Return the content type of the route."""
        return self._content_type

    @property
    def handler(self) -> Callable[[], str]:
        """Return the handler function"""
        return self._handler

    def can_handle(self, path: str) -> bool:
        """Return true if this route can handle the given path"""
        return path == self._path
