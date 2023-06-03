FROM python:3.11-alpine

# Create a group and user to run our app
ARG APP_USER=appuser
RUN addgroup -S ${APP_USER} && adduser -S ${APP_USER} -G ${APP_USER}

# This is the target environment, either dev or prod
ARG ENV

# Set up options for pip, pipenv and python
ENV PYTHONFAULTHANDLER=1 \
        PYTHONUNBUFFERED=1 \
        PYTHONHASHSEED=random \
        PIP_NO_CACHE_DIR=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1 \
        PIP_DEFAULT_TIMEOUT=100 \
        PIPENV_HIDE_EMOJIS=true \
        PIPENV_NOSPIN=true

#RUN set -ex \
#        && RUN_DEPS="" \
#        && apk add --no-cache $RUN_DEPS

# We store the application in /app
RUN mkdir /app
WORKDIR /app

COPY Pipfile /app
COPY Pipfile.lock /app

RUN set -ex \
        && BUILD_DEPS="" \
        && apk add --no-cache --virtual .build-deps $BUILD_DEPS \
        && pip install --upgrade pipenv \
        \
        && pipenv sync --system \
        \
        && apk del .build-deps

# Copy the whole application source over. We should have a `.gitignore` file in
# the project to e.g. prevent the .git directory from coming over.
COPY . /app

# Default command to run
ENTRYPOINT ["python", "-u", "-m", "promqtt"]
