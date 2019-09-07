# promqtt [![Build Status](https://travis-ci.org/motlib/promqtt.svg?branch=master)](https://travis-ci.org/motlib/promqtt)

A small python tool listening for MQTT messages (e.g. from Tasmota devices and 
make the data available to a [Prometheus](https://prometheus.io) instance.

## Configuration

### Command-Line / Environment

This tool has two sources of configuration. Basic runtime options can be
configured via command-line options or environment variables. Start with the
`--help` option to see all available options. 

For each command-line option you can replace "." with "_", convert to upper case
and set this option as an environment variable. E.g. the command-line option 
`--http.port`  can also be set via environment variable `HTTP_PORT`. 


### Configuration file

Additionally to these basic options, you need to create a configuration file
specifying the MQTT topics and formats to listen to and how to publish them to 
Prometheus.

See the `./config` directory for an example. 

(More detailed documentation has still to be written)


## HTTP Server

The HTTP server is configured according to the command-line arguments or
environment variables. See *Configuration* section for details.

The HTTP server mainly serves one path with plain text data according to
Prometheus format. Additionally you can retrieve the active configuration.



* `/metrics`: Prometheus data
* `/cfg_json`: Active tool configuration in JSON format
* `/devcfg_cfg`: The active device configuration in JSON format


## References

* [Prometheus](https://prometheus.io)
* [Sonoff Tasmota](https://github.com/arendst/Sonoff-Tasmota)
