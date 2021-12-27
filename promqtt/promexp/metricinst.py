'''Implementation of the metric instance class. This represents a single metric
value identified by its name (metric) and its labels.'''

from datetime import datetime
import logging

from .utils import _get_label_string


logger = logging.getLogger(__name__)


def _get_time():
    '''Return the current time as a datetime object.

    Wrapped in a function, so it can be stubbed for testing.'''

    return datetime.now()


class MetricInstance():
    '''Represents a single metric instance. Instances are identified by a unique
    combination of labels and a value.'''

    def __init__(self, metric, labels, value):
        self._metric = metric
        self._labels = labels
        self._label_str = _get_label_string(labels)

        self.value = value


    @property
    def value(self):
        '''Return the value'''

        return self._value


    @value.setter
    def value(self, value):
        '''Set the value'''

        self._value = value
        self._timestamp = _get_time()

        logger.debug(f'Set metric instance {self}')


    @property
    def age(self):
        '''Return the age of the metric value, i.e. when it was last set.'''

        return (_get_time() - self._timestamp).total_seconds()


    @property
    def is_timed_out(self):
        '''Return True if the metric timeout is expired'''

        if not self._metric.has_timeout:
            return False

        return self.age >= self._metric.timeout


    @property
    def label_string(self):
        '''Return the label string of this instance'''
        return self._label_str


    def __str__(self):
        return f'{self._metric.name}{{{self.label_string}}} {self.value}'
