from datetime import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import logging
from threading import Thread, Lock

class PrometheusExporter(BaseHTTPRequestHandler):

    def __init__(self, http_cfg):
        self._prom = {}
        self._lock = Lock()
        self._http_cfg = http_cfg

        
    def register(self, name, datatype, helpstr, timeout=None):
        '''Register a name for exporting. This must be called before calling 
        `set()`.

        :param str name: The name to register.
        :param str type: One of gauge or counter.
        :param str helpstr: The help information / comment to include in the 
          output.
        :param int timeout: Timeout in seconds for any value. Before rendering, 
          values which are updated longer ago than this value, are removed.'''
        
        with self._lock:
            if name not in self._prom:
                self._prom[name] = {
                    'help': helpstr,
                    'type': datatype,
                    'data':{},
                    'timeout': None}
            else:
                raise Exception('Measurement already registered')

    
    def set(self, name, labels, value, fmt='{0}'):
        '''Set a value for exporting. 

        :param str name: The name of the value to set. This name have been 
          registered already by calling `register()`.
        :param dict labels: The labels to attach to this name.
        :param value: The value to set. Automatically converted to string.
        :param fmt: The string format to use to convert value to a string. 
          Default: '{0}'. '''

        labelstr = ','.join(
            ['{0}="{1}"'.format(k, labels[k]) for k in sorted(labels.keys())]
        )
        
        if name not in self._prom:
            logging.error("Cannot set unknown measurement '{0}'.".format(name))
            return

        namestr = '{name}{{{labels}}}'.format(
            name=name,
            labels=labelstr)
            
        with self._lock:
            data = self._prom[name]['data']
            data[namestr] = {'value': fmt.format(value)}

        logging.debug('Set prom value {0} = {1}'.format(
            namestr, value))

        
    def _check_timeout(self):
        '''Remove all data which has timed out (not valid anymore).'''
        to_delete = []
        
        for k in self._prom.keys():
            to = self._prom[k]['timeout']
            if to != None:
                data = self._prom[k]['data']
                for i in data.keys():
                    if (datetime.now() - i['timestamp']).total_seconds() > to:
                        to_delete.append(i)

                for i in to_delete:
                    del data[i]
                    logging.debug("Removed timed out item '{0}'.".format(i)) 
                    
                to_delete.clear()

        
    def render(self):
        '''Render the current data to Prometheus format.

        :returns: String with output suitable for consumption by Prometheus over 
          HTTP. '''
        
        lines = []

        with self._lock:

            self._check_timeout()
            
            for k in self._prom.keys():
                data = self._prom[k]['data']
                            
                # do not output items without values
                if len(self._prom[k]['data']) == 0:
                       continue
                
                lines.append('# HELP {k} {h}'.format(
                    k=k,
                    h=self._prom[k]['help']))
                lines.append('# TYPE {k} {t}'.format(
                    k=k,
                    t=self._prom[k]['type']))
        
                for i in data.keys():
                    lines.append('{n} {v}'.format(
                        n=i, v=data[i]['value']))
    
        return '\n'.join(lines)


    def _run_http_server(self):
        msg = 'Starting http server on {interface}:{port}.'
        logging.info(msg.format(**self._http_cfg))
        
        httpd = ThreadingHTTPServer(
            (self._http_cfg['interface'], self._http_cfg['port']),
            PromHttpRequestHandler)
        httpd.prom = self
        httpd.serve_forever()

        
    def start_server_thread(self):
        srv_thread = Thread(
            target=self._run_http_server,
            name='http_server',
            daemon=True)
        srv_thread.start()

        
class PromHttpRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            prom = self.server.prom
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(prom.render().encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'URL not found. Please use /metrics path.')

