# promqtt

[![Run QA tasks in Docker](https://github.com/motlib/promqtt/actions/workflows/qa.yml/badge.svg)](https://github.com/motlib/promqtt/actions/workflows/qa.yml)

`promqtt` is a python application, which can receive messages from a MQTT
broker, extract data from the mesages and publish the result in a format
suitable for [Prometheus]. This can be used e.q. in
combination with `zigbee2mqtt` to receive information from Zigbee based sensors,
publish it to Prometheus and show the results in
nice [Grafana] dashboards.

## Configuration

The best way to start the application is by building a docker container from the
included `Dockerfile`. The container processes to environment variables for
configuration:

* `PROMQTT_CONFIG`: Path to the configuration file
* `PROMQTT_VERBOSE`: Set to 1 to enable verbose logging

### Configuration file

You need to create a configuration file specifying the MQTT topics and formats
to listen to and how to publish them to Prometheus.

In general, the file contains the following sections:

* `mqtt`: Connection information for the MQTT broker
* `http`: Configuration of the embedded HTTP server to provide information in
  prometheus format.
* `metrics`: Definition of the metrics to publish to prometheus
* `types`: As many zigbee devices publish information in a similar format, you
  have to declare types in the configuration to describe this common structure.
* `messages`: This section maps messages received from MQTT to device types.

See the `./config` directory for an example.


## References

* [Prometheus](https://prometheus.io)
* [Grafana](https://www.grafana.com)
* [Sonoff Tasmota](https://github.com/arendst/Sonoff-Tasmota)
