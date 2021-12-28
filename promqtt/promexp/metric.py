'''Implementation of a metric. A metric is identified by its name and carries a
list of metric instances.'''

from .metricinst import MetricInstance
from .utils import _get_label_string


class Metric():
    '''Represents a Prometheus metric, i.e. a metric name with its helptext and type
    information.'''

    def __init__(self, name, datatype, helpstr, timeout=None, with_update_counter=False): # pylint: disable=too-many-arguments
        self._name = name
        self._datatype = datatype
        self._helpstr = helpstr
        self._timeout = timeout
        self._instances = {}
        self._with_update_counter = with_update_counter


    @property
    def name(self):
        '''Return the metric name'''
        return self._name


    @property
    def datatype(self):
        '''Return the metric datatype (gauge, counter, ...)'''
        return self._datatype

    @property
    def helptext(self):
        '''Return the metric help text'''

        return self._helpstr

    @property
    def timeout(self):
        '''Return the timeout in seconds for this metric. Metric instances are removed
        from the metric after the timeout is expired.'''

        return self._timeout


    @property
    def with_update_counter(self):
        '''Returns true if this metric has an associated update counter metric.'''

        return self._with_update_counter


    def set(self, labels, value):
        '''Set a value for a metric instance'''

        labelstr = _get_label_string(labels)

        # If we do not know this instance yet
        if labelstr not in self._instances:

            # we do not add new metrics without assigned value
            if value is None:
                return

            # we don't know this instance yet, so we create a new one
            self._instances[labelstr] = MetricInstance(
                metric=self,
                labels=labels,
                value=value)

        # we already know this instance
        else:

            # if the value is None, we remove it
            if value is None:
                del self._instances[labelstr]
            else:
                # we know this instance, so we update its value
                instance = self._instances[labelstr]
                instance.value = value


    def get(self, labels):
        '''Return the last stored value of a metric instance. Returns None if
        the instance does not exist.'''

        labelstr = _get_label_string(labels)

        # If we do not know this instance yet
        if labelstr not in self._instances:
            return None

        inst = self._instances[labelstr]
        return inst.value


    def inc(self, labels):
        '''Increases the value of the metric instance by one. '''

        val = self.get(labels)

        if val is None:
            val = 0

        val += 1

        self.set(labels, val)


    @property
    def has_timeout(self):
        '''Return true if this metric has an timeout assigned.'''

        return (self.timeout is not None) and (self.timeout > 0)


    def check_timeout(self):
        '''Check all metric instances for timeout and remove the timed out instances.'''

        # find all timed out metric instances
        to_delete = [
            labelstr
            for labelstr, instance in self._instances.items()
            if instance.is_timed_out
        ]

        # remove the metric instances
        for labelstr in to_delete:
            del self._instances[labelstr]


    def render_iter(self):
        '''Return an iterator returning separate lines in Prometheus format'''

        yield f'# HELP {self.name} {self.helptext}'
        yield f'# TYPE {self.name} {self.datatype}'

        yield from (str(instance) for instance in self._instances.values())


    def render(self):
        '''Render the metric to Prometheus format'''

        return '\n'.join(self.render_iter())


    def __str__(self):
        return self._name
