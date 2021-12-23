'''Config wrapper'''

import logging
import os

from ruamel.yaml import YAML
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class Wrapper():
    '''Wrapper class that wrapps a configuration structure or parts of it and either
    returns another Wrapper instance for sub-structures or a plain value.

    '''

    def __init__(self, cls, struct):
        self._cls = cls
        self._struct = struct


    def get(self, name):
        '''Get a configuration value.'''

        # first make sure that we have loaded the right config
        self._cls.ensure_config()

        # We return the underlying data structure when accessing the 'raw'
        # attribute.
        if name == 'raw':
            return self._struct

        data = self._struct[name]

        if isinstance(data, (dict, list)):
            return Wrapper(self._cls, data)

        return data


    def __getattr__(self, name):
        '''Attribute based access'''

        return self.get(name)


    def __getitem__(self, key):
        '''Index based access'''

        return self.get(key)


    def __str__(self):
        return f'Wrapper({self._struct})'


class ConfigMetaClass(type):
    '''Metaclass for configuration objects.'''

    def load_config(cls):
        '''Load the yaml configuration file'''

        yaml = YAML(typ='safe')

        with open(cls.cfg_filename, mode='r', encoding='utf-8') as fhdl:
            cfgdata = yaml.load(fhdl)

        if cls.cfg_schema:
            with open(cls.cfg_schema, mode='r', encoding='utf-8') as fhdl:
                schema = yaml.load(fhdl)

            try:
                validate(
                    instance=cfgdata,
                    schema=schema)
            except ValidationError as ve:
                path = '/'.join((str(e) for e in ve.path))
                logger.error(
                    f"Element '{path}': {ve.message}")

        cls._cfg = Wrapper(cls, cfgdata)

        cls._loaded_filename = cls.cfg_filename
        cls._loaded_filedate = os.path.getmtime(cls.cfg_filename)

        logger.debug(f"Loaded config '{cls.cfg_filename}' for '{cls.__name__}'.")


    def needs_reload(cls):
        '''Returns true if the config needs to be (re-)loaded'''

        if not cls._cfg:
            logger.debug(f"Config '{cls.cfg_filename}' not yet loaded.")
            return True

        if cls._loaded_filename != cls.cfg_filename:
            logger.debug(
                f"Config changed from '{cls._loaded_filename}' to "
                f"'{cls.cfg_filename}.")
            return True

        if cls.cfg_autoreload:
            filedate = os.path.getmtime(cls.cfg_filename)
            if filedate > cls._loaded_filedate:
                logger.debug("Config '{cls.cfg_filename}' is modified")
                return True

        return False


    def ensure_config(cls):
        '''Helper method that loads the config when it is needed'''

        # pylint: disable=no-value-for-parameter
        if cls.needs_reload():
            cls.load_config()


    def __getattr__(cls, name):
        '''Attribute access function'''

        # pylint: disable=no-value-for-parameter
        cls.ensure_config()
        return cls._cfg[name]


class AbstractConfig(metaclass=ConfigMetaClass): # pylint: disable=too-few-public-methods
    '''Base class for config classes'''

    # The internal configuration data structure
    _cfg = None

    # The loaded config filename
    _loaded_filename = None

    # Default value for the auto-reload flag
    cfg_autoreload = False

    # Default value for the filename
    cfg_filename = None

    # Schema file
    cfg_schema = None
