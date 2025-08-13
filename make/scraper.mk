include .env
export

include make/test.mk

run-local: lint unit-test
# 	export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/$(RUN_SVC_ACCT)-key.json
	poetry run python -m scraper.run

IMAGE=$(SCRAPER_IMAGE)
CONTAINER_NAME=scraper-container
JOB_DEV=$(SCRAPER_JOB_DEV)
JOB_PROD=$(SCRAPER_JOB_PROD)
SCHEDULE_NAME_DEV=$(SCRAPER_SCHEDULE_NAME_DEV)
SCHEDULE_NAME_PROD=$(SCRAPER_SCHEDULE_NAME_PROD)

include make/cloud_run_job.mk
