from threading import Lock


class PrometheusExporter():

    def __init__(self):
        self._prom = {}
        self._lock = Lock()
    
    def reg(self, name, datatype, helpstr):
        with self._lock:
            if name not in self._prom:
                self._prom[name] = {'help': helpstr, 'type': datatype, 'data':{}}
            else:
                raise Exception('Measurement already registered')

    
    def set(self, name, labels, value):
        labelstr = ','.join(
            ['{0}="{1}"'.format(k, labels[k]) for k in sorted(labels.keys())]
        )
        
        namestr = '{name}{{{labels}}}'.format(
            name=name,
            labels=labelstr)
            
        if name not in self._prom:
            raise Exception('unknown measurement')

        with self._lock:
            data = self._prom[name]['data']
            data[namestr] = {'value': value}
         
    
    def render():
        lines = []

        with self._lock:
            for k in self._prom.keys():
                # do not output items without values
                if len(self._prom[k]['data']) == 0:
                       continue
                
                lines.append('HELP {k} {h}'.format(k=k, h=self._prom[k]['help']))
                lines.append('TYPE {k} {t}'.format(k=k, t=self._prom[k]['type']))
        
                data = self._prom[k]['data']
                for i in data.keys():
                    lines.append('{n} {v}'.format(n=i, v=data[i]['value']))
    
        return '\n'.join(lines)
    
