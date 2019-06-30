import logging
from datetime import datetime
from threading import Thread, Lock
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

class PrometheusExporter(BaseHTTPRequestHandler):

    def __init__(self, http_iface, http_port):
        self._prom = {}
        self._lock = Lock()
        self._http_iface = http_iface
        self._http_port = http_port

        
    def reg(self, name, datatype, helpstr, timeout=None):
        with self._lock:
            if name not in self._prom:
                self._prom[name] = {'help': helpstr, 'type': datatype, 'data':{}, 'timeout': None}
            else:
                raise Exception('Measurement already registered')

    
    def set(self, name, labels, value):
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
            data[namestr] = {'value': value}

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
        msg = 'Starting http server on {0}:{1}.'
        logging.info(msg.format(self._http_iface, self._http_port))
        
        httpd = ThreadingHTTPServer(
            (self._http_iface, self._http_port),
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
            self.wfile.write(b'Please use /metrics path.')

