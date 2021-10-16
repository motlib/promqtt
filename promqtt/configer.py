'''Automatic configuration handling. Uses a config specification and generates a
dict structure with configuration values populated from command-line,
environment variables and possibly a configiration file.'''

import argparse
import os

def _set_struct(cfg, name, value, sep='.'):
    '''Parses a "path" string to locate the specified path in a dictionary to
    set a value.

    E.g. name='root.sub.val', value=foo => {'root': {'sub': {'val': 'foo'}}}'''

    parts = name.split(sep)

    # loop over all but last part
    for part in parts[:-1]:
        if part not in cfg:
            cfg[part] = {}

        cfg = cfg[part]

    cfg[parts[-1]] = value


def _get_struct(cfg, name, sep='.'):
    '''Retrieve configuration sub-structure'''

    parts = name.split(sep)

    for part in parts:
        if part in cfg:
            cfg = cfg[part]
        else:
            return None

    return cfg


def prepare_argparser(cfgdef, parser=None):
    '''Generate the argument parser to parse command-line arguments according
    to the configuration descriptor.'''

    if parser is None:
        parser = argparse.ArgumentParser()

    for name,info in cfgdef.items():
        parser.add_argument(
            '--' + name,
            required=False,
            default=None,
            help=info['help'],
            type=info['type'])

    return parser


def eval_args(cfgdef, cfg, args):
    '''Get data from command-line arguments'''

    argvars = vars(args)

    for name in cfgdef:
        if (name in argvars) and (argvars[name] is not None):
            _set_struct(cfg, name, argvars[name])


def eval_env(cfgdef, cfg, env):
    '''Get data from environment variable'''

    for name, info in cfgdef.items():
        varname = name.upper().replace('.', '_')
        if varname in env:
            _set_struct(cfg, name, info['type'](os.environ[varname]))


def eval_cfgfile_data(cfgdef, cfg, cfg_in):
    '''Get data from configuration file'''

    for name in cfgdef:
        value = _get_struct(cfg_in, name)
        if value is not None:
            _set_struct(cfg, name, value)


def eval_cfg(cfgdef, cfg_in, env, args):
    '''Evaluate all sources for configuration data'''

    cfg = {}

    for name, item in cfgdef.items():
        _set_struct(cfg, name, item['default'])

    eval_cfgfile_data(cfgdef, cfg, cfg_in)
    eval_env(cfgdef, cfg, env)
    eval_args(cfgdef, cfg, args)

    return cfg
