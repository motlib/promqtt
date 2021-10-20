#!/usr/bin/env bash

TAG=$(date "+%Y%m%d-%H%M%S")-$(git describe --always)

docker build \
       --build-arg ENV=production \
       --tag promqtt:${TAG} \
       --tag promqtt:latest \
       .
