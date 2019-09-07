

cfg_desc = {
    'http.interface': {
        'type': str,
        'help': 'Interface to bind the http server to.',
        'default': '127.0.0.1',
    },
    'http.port': {
        'type': int,
        'help': 'TCP port for the http server.',
        'default': 8086,
    },
    'mqtt.broker': {
        'type': str,
        'help': 'MQTT broker hostname',
        'default': 'mqtt',
    },
    'mqtt.port': {
        'type': str,
        'help': 'MQTT broker port number',
        'default': 1883,
    },
    'verbose': {
        'type': bool,
        'help': 'Verbose (debug) output.',
        'default': False
    },
    'cfgfile': {
        'type': str,
        'help': 'Device configuration file',
        'default': 'promqtt.yml',
    }
}
