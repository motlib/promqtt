FROM python:3.11

RUN \
    apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install git \
    \
    && python -m pip install --upgrade pip pipenv

