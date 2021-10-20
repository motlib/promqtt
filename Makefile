# Makefile to run development tools

.PHONY: all
all: pylint pytest


.PHONY: pylint
pylint:
	pipenv run pylint \
	  --rcfile .pylintrc \
	  --output-format=colorized \
	  promqtt


.PHONY: pytest
pytest:
	mkdir -p ./build/cov
	pipenv run pytest \
	  --cov=promqtt \
	  --cov-report=html:./build/cov \
	  --verbose
