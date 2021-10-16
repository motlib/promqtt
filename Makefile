
.PHONY: pylint
pylint:
	pipenv run pylint \
	  --rcfile .pylintrc \
	  --output-format=colorized \
	  promqtt


.PHONY: pytest
pytest:
	pipenv run pytest --verbose
