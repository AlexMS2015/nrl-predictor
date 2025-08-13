######################################
### Lint, test
######################################

lint:
	poetry run ruff check --fix
	poetry run ruff format

unit-test:
	poetry run pytest
