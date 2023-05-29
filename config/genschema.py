'''Utility script to generate JSON schema file for promqtt config model

Usage: pipenv run python -m config.genschema

'''

from promqtt.cfgmodel import PromqttConfig

SCHEMA_FILE = 'config/promqtt.schema.json'

def main():
    '''Generate schema file'''

    with open(SCHEMA_FILE, 'w', encoding='utf-8') as fhdl:
        fhdl.write(PromqttConfig.schema_json())

if __name__ == '__main__':
    main()
