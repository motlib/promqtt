#!/usr/bin/env bash
#
# Build the `qa` container.
#

docker build \
       --tag promqtt:qa \
       --build-arg ENV=dev \
       .
