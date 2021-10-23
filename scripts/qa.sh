#!/usr/bin/env bash

docker run \
       --name promqtt \
       --rm \
       --env PROMQTT_VERBOSE=1 \
       promqtt:qa \
       $*
