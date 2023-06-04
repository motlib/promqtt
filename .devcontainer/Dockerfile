FROM python:3.11-alpine

ENV \
    EDITOR="code -w" \
    PIPENV_VENV_IN_PROJECT=1

RUN apk add --no-cache bash git less ncurses openssh \
    \
    && python -m pip install --upgrade pip pipenv
