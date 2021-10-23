#!/usr/bin/env bash

docker build \
       --tag promqtt:qa \
       --build-arg ENV=dev \
       .
