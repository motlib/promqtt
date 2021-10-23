#!/usr/bin/env bash

docker build \
       --tag promqtt:dev \
       --build-arg ENV=dev \
       .

docker run \
       --name promqtt \
       --rm \
       --env PROMQTT_VERBOSE=1 \
       -it \
       -v $(pwd):/app \
       promqtt:dev \
       $*
