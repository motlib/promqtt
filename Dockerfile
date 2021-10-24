FROM python:3.7

# We later need to use `test` command, which is not well supported in sh, so we
# change to bash.
SHELL ["/bin/bash", "-c"]

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
        PIPENV_COLORBLIND=true \
        PIPENV_NOSPIN=true \
        PIPENV_DOTENV_LOCATION=config/${ENV}.env

# We store the application in /app
RUN mkdir /app
WORKDIR /app

RUN pip install pipenv

COPY Pipfile /app
COPY Pipfile.lock /app

# Install virtual environment from Pipfile.lock. Fail if Pipfile.lock is out of
# date (--deploy). Install development dependencies if we build for `dev`
# environment (--dev).
RUN \
        if [ "$ENV" == "dev" ]; then echo "Building for dev environment"; fi \
        && apt-get update \
        && apt-get install --yes python3-dev \
        && pipenv install $(test "${ENV} == dev" && echo --dev) --deploy --ignore-pipfile \
        && apt-get purge --yes python3-dev \
        && apt-get --purge --yes autoremove \
        && rm -rf /var/lib/apt/lists/*

# Copy the whole application source over. We should have a `.gitignore` file in
# the project to e.g. prevent the .git directory from coming over.
COPY . /app

# Default command to run
CMD ["pipenv", "run", "python", "-m", "promqtt"]
