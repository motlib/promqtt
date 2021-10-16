'''Implementation of the HTTP server to serve prometheus data.'''

import logging




class Route():
    def __init__(self, path, content_type, handler):
        self._path = path
        self._content_type = content_type
        self._handler = handler


    @property
    def content_type(self):
        '''Return the content type of the route.'''
        return self._content_type


    @property
    def handler(self):
        '''Return the handler function'''
        return self._handler


    def can_handle(self, path):
        '''Return true if this route can handle the given path'''
        return path == self._path
