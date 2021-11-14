'''Represents a mapping from one MQTT topic to one Prometheus metric.'''

import logging


logger = logging.getLogger(__name__)


class Mapping():
    '''A mapping takes data from a message received from MQTT, extracts a value and
    possibly also label values and submits the results to the prometheus
    exporter.

    '''

    def __init__(self, promexp, type_name, value_exp, label_exps, metric): # pylint: disable=too-many-arguments
        self._type_name = type_name
        self._promexp = promexp
        self._value_exp = value_exp
        self._label_exps = label_exps
        self._metric = metric


    def handle_msg_data(self, msg):
        '''Handle a message received from MQTT'''

        # calculate value

        try:
            value = self._value_exp.format(
                msg=msg)
        except Exception as ex: # pylint: disable=broad-except
            # We only print a debug log, as we want the message handling to be
            # fault tolerant. Message contents sometimes change over time and
            # not every member is available all the time. To issues are to be
            # expected
            logger.debug(
                f"{self}: Cannot apply value expression '{self._value_exp}' "
                f"for message {msg}: {ex}")
            return


        # calculate labels

        labels = {}
        label_fault = False

        for name_exp, value_exp in self._label_exps.items():
            try:
                label_name = name_exp.format(msg=msg)
                label_value = value_exp.format(msg=msg)

                labels[label_name] = label_value
            except Exception as ex: # pylint: disable=broad-except

                # We only print a debug log, as we want the message handling to
                # be fault tolerant. Message contents sometimes change over time
                # and not every member is available all the time. To issues are
                # to be expected
                logger.debug(
                    f"{self}: Cannot apply label expression '{self._value_exp}' "
                    f"for message {msg}: {ex}")

                label_fault = True

        # if at least one label had a fault, we return
        if label_fault:
            return


        # Hand over metric data to prometheus exporter

        self._promexp.set(
            name=self._metric,
            labels=labels,
            value=value)

    def __str__(self):
        return f'Mapping(type={self._type_name}, metric={self._metric})'