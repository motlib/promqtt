import argparse
import os

cfgdef = {
    'http.interface': {
        'type': str,
        'help': 'Interface to bind the http server to.',
    },
}


def _set_struct(cfg, name, value, sep='.'):
    parts = name.split(sep)

    for part in parts:
        if part in cfg:
            cfg = cfg[part]
        else:
            cfg[part] = {}

    cfg[part] = value


def _get_struct(cfg, name, sep='.', default=None):
    parts = name.split(sep)
    
    for part in parts:
        if part in cfg:
            cfg = cfg[part]
        else:
            return None

    return cfg
    

def prepare_argparser(cfgdef, parser=None):
    if parser == None:
        parser = argparse.ArgumentParser()
    
    for name,info in cfgdef:
        parser.add_argument(
            '--' + name,
            required=False,
            default=None,
            help=info['help'],
            type=info['type'])

    return parser


def eval_args(cfgdef, cfg, args):
    argvars = vars(args)
    
    for name, info in cfgdef.items():
        if name in argvars:
            update_struct(cfg, name, argvars[name])


def eval_env(cfgdef, cfg, env):

    for name, info in cfgdef.items():
        varname = name.upper().replace('.', '_')
        if varname in env:
            update_struct(cfg, name, os.environ[varname])l


def eval_cfgfile_data(cfgdef, cfg, cfg_in):
    for name, item in cfgdef.items():
        v = _get_struct(cfg_in, name)
        if v != None:
            _set_struct(cfg, name, v)

def eval(cfgdef, cfg, cfg_in, env, args):
    eval_cfgfile_data(cfgdef, cfg, cfg_in)
    eval_env(cfg_dev, cfg, env)
    eval_args(cfgdef, cfg, args)
