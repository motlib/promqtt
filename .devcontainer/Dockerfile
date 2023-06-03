FROM python:3.11-alpine

ENV EDITOR="code -w"

RUN apk add --no-cache bash git less openssh \
    \
    && python -m pip install --upgrade pip pipenv
