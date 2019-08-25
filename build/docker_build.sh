#!/usr/bin/env bash

pipenv lock -r > requirements.txt

docker build --tag promqtt:latest .
