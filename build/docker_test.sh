#!/usr/bin/env bash

docker run --name promqtt --rm -e MQTT_BROKER=npi2 -e VERBOSE=1 promqtt:latest 
