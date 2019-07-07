

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
    'mqtt.prefix': {
        'type': str,
        'help': 'MQTT topic prefix to skip',
        'default': 'tasmota',
    },
    'mqtt.timeout': {
        'type': int,
        'help': 'Timeout of MQTT sensor values in seconds.',
        'default': 300,
    },
    'verbose': {
        'type': bool,
        'help': 'Verbose (debug) output.',
        'default': False
    },
}
