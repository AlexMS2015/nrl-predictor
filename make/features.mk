include .env
export

include make/test.mk

######################################
### Feature engineering
######################################

run-local: lint unit-test
# 	export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/$(RUN_SVC_ACCT)-key.json
	poetry run python -m feature_eng.feature_eng.run
