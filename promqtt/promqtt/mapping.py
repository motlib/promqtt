'''Represents a mapping from one MQTT topic to one Prometheus metric.'''

import logging


logger = logging.getLogger(__name__)


class Mapping():
    '''A mapping takes data from a message received from MQTT, extracts a value
    and possibly also values and submits the results to the prometheus
    exporter.'''

    def __init__(self, promexp, value_exp, label_exps, metric):
        self._promexp = promexp
        self._value_exp = value_exp
        self._label_exps = label_exps
        self._metric = metric


    def handle_msg_data(self, msg):
        '''Handle a message received from MQTT'''

        try:
            value = self._value_exp.format(
                msg=msg)
        except KeyError:
            logger.error(f"Cannot apply value expression '{self._value_exp}'. Message: {msg}")
            return

        # calculate labels
        bind_labels = {
            k.format(msg=msg):
            v.format(msg=msg)
            for k,v in self._label_exps.items()}

        self._promexp.set(
            name=self._metric,
            labels=bind_labels,
            value=value)

    def __str__(self):
        return f'Mapping(metric={self._metric})'
