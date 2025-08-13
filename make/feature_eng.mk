include .env
export

include make/test.mk

run-local: lint unit-test
# 	export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/$(RUN_SVC_ACCT)-key.json
	poetry run python -m feature_eng.run

IMAGE=$(FEATENG_IMAGE)
CONTAINER_NAME=feateng-container
JOB_DEV=$(FEATENG_JOB_DEV)
JOB_PROD=$(FEATENG_JOB_PROD)
SCHEDULE_NAME_DEV=$(FEATENG_SCHEDULE_NAME_DEV)
SCHEDULE_NAME_PROD=$(FEATENG_SCHEDULE_NAME_PROD)

include make/cloud_run_job.mk
