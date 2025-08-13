include .env
export

include make/gcp.mk
include make/gha.mk

setup: setup-local-env gcp-setup # setup-gha

setup-local-env:
	poetry install
	pre-commit install

gcp-setup: create-project \
		set-project \
		enable-services \
		create-buckets \
		iam-cloud-run \
		iam-deployer

# setup-gha: setup-gh-cli add-secrets-gh

######################################
### Auth
######################################

# gcloud-auth:
# 	gcloud config set account $(USERNAME)

# # run this locally before push and deploy to better simulate GHA environment
# gcloud-auth-sa:
# 	gcloud auth activate-service-account --key-file=$(HOME)/.gcp/nrl-deployer-key.json
