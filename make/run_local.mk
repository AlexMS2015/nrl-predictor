include make/test.mk

scraper-run-local: lint unit-test
	poetry run python -m feature_eng.run

feat-eng-run-local: lint unit-test
	poetry run python -m scraper.run
