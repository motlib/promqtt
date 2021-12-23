'''Implementation of the application configuration'''

import os

from .utils import AbstractConfig


class AppConfig(AbstractConfig): # pylint: disable=too-few-public-methods
    '''Application configuration'''

    cfg_schema = os.path.join(
        os.path.dirname(__file__), '..', 'config', 'schema.yml')
