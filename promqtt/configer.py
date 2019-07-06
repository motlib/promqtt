import argparse
import os

def _set_struct(cfg, name, value, sep='.'):
    parts = name.split(sep)

    # loop over all but last part
    for part in parts[:-1]:
        if part not in cfg:
            cfg[part] = {}

        cfg = cfg[part]
                    
    cfg[parts[-1]] = value


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
    
    for name,info in cfgdef.items():
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
        if (name in argvars) and (argvars[name] is not None):
            _set_struct(cfg, name, argvars[name])


def eval_env(cfgdef, cfg, env):
    for name, info in cfgdef.items():
        varname = name.upper().replace('.', '_')
        if varname in env:
            _set_struct(cfg, name, info['type'](os.environ[varname]))


def eval_cfgfile_data(cfgdef, cfg, cfg_in):
    for name, item in cfgdef.items():
        v = _get_struct(cfg_in, name)
        if v != None:
            _set_struct(cfg, name, v)

            
def eval_cfg(cfgdef, cfg_in, env, args):
    cfg = {}

    for name, item in cfgdef.items():
        _set_struct(cfg, name, item['default'])
    
    eval_cfgfile_data(cfgdef, cfg, cfg_in)
    eval_env(cfgdef, cfg, env)
    eval_args(cfgdef, cfg, args)

    return cfg
