'''Prometheus exporter'''

from datetime import datetime
import logging
from threading import Lock


logger = logging.getLogger(__name__)


class PrometheusExporterException(Exception):
    '''Base class for all exceptions generated by the PrometheusExporter.'''


class UnknownMeasurementException(PrometheusExporterException):
    '''Raised when you try to set a value for a measurement not registered
    yet.'''


class PrometheusExporter():
    '''Manage all measurements and provide the htp interface for interfacing with
    Prometheus.'''

    def __init__(self):
        self._prom = {}
        self._lock = Lock()


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
                    'timeout': timeout}
            else:
                raise PrometheusExporterException(
                    'Measurement already registered')


    def set(self, name, labels, value, fmt='{0}'):
        '''Set a value for exporting.

        :param str name: The name of the value to set. This name must have been
          registered already by calling `register()`.
        :param dict labels: The labels to attach to this name.
        :param value: The value to set. Automatically converted to string.
        :param fmt: The string format to use to convert value to a string.
          Default: '{0}'. '''

        labelstr = ','.join(
            [f'{k}="{labels[k]}"' for k in sorted(labels.keys())]
        )

        # Values for unknown measuresments cause raising an exception
        if name not in self._prom:
            raise UnknownMeasurementException(
                f"Cannot set not registered measurement '{name}'.")

        namestr = f'{name}{{{labelstr}}}'

        with self._lock:
            data = self._prom[name]['data']

            if value is not None:
                data[namestr] = {'value': fmt.format(value)}
                data[namestr]['timestamp'] = self._get_time()
            else:
                # we remove the item when passing None as value
                if namestr in data:
                    del data[namestr]

        logger.debug(f'Set prom value {namestr} = {value}')


    def _get_time(self): # pylint: disable=no-self-use
        '''Return the current time as a datetime object.

        Wrapped in a function, so it can be stubbed for testing.'''

        return datetime.now()


    def _check_timeout(self):
        '''Remove all data which has timed out (i.e. is not valid anymore).'''
        to_delete = []

        # loop over all measurements
        for meas in self._prom.values():
            timeout = meas['timeout']

            if (timeout is None) or (timeout == 0):
                continue

            data = meas['data']
            now = self._get_time()

            # first loop to find timed out items
            for item_name, item in data.items():
                if (now - item['timestamp']).total_seconds() >= timeout:
                    to_delete.append(item_name)

            # second loop to remove them
            for item_name in to_delete:
                del data[item_name]
                logger.debug(f"Removed timed out item '{item_name}'.")

            to_delete.clear()


    def render(self):
        '''Render the current data to Prometheus format. See
        https://prometheus.io/docs/instrumenting/exposition_formats/ for details.

        :returns: String with output suitable for consumption by Prometheus over
          HTTP. '''

        lines = []

        with self._lock:

            self._check_timeout()

            for key, val in self._prom.items():
                # do not output items without values
                if len(val['data']) == 0:
                    continue

                helptext = val['help']
                lines.append(f'# HELP {key} {helptext}')

                typename = val['type']
                lines.append(f'# TYPE {key} {typename}')

                data = val['data']
                for i in data:
                    value = data[i]['value']
                    lines.append(f'{i} {value}')

        return '\n'.join(lines)