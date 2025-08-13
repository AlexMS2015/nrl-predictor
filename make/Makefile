include .env
export

setup: setup-local-env gcp-setup setup-gha

setup-local-env:
	poetry install
	pre-commit install

gcp-setup: create-project \
		set-project \
		enable-services \
		create-buckets \
		iam-cloud-run \
		iam-deployer

setup-gha: setup-gh-cli add-secrets-gh

########################################
# GCP setup
########################################

create-project:
	gcloud projects create $(PROJECT_ID) --name $(PROJECT_NAME)

set-project:
	gcloud config set project $(PROJECT_ID)

enable-services:
	gcloud services enable run.googleapis.com
	gcloud services enable artifactregistry.googleapis.com
	gcloud services enable secretmanager.googleapis.com

create-buckets:
	gcloud storage buckets create gs://$(DEV_BUCKET) \
		--location $(REGION) \
		--uniform-bucket-level-access
	gcloud storage buckets create gs://$(PROD_BUCKET) \
		--location $(REGION) \
		--uniform-bucket-level-access

create-docker-repo:
	gcloud artifacts repositories create $(DOCKER_REPO) \
		--repository-format=docker \
		--location=$(REGION) \
		--description="Docker repository for NRL predictor" \
		--project=$(PROJECT_ID)
	gcloud auth configure-docker $(REGION)-docker.pkg.dev

######################################
### Service accounts
######################################

iam-deployer: # deployer SA
	gcloud iam service-accounts create $(SVC_ACCT) \
		--description="Service account for deployments and scheduling" \
		--display-name="NRL deployer and scheduler"

	gcloud iam service-accounts keys create ~/.gcp/$(SVC_ACCT)-key.json \
		--iam-account=$(SVC_EMAIL)

	gcloud iam service-accounts add-iam-policy-binding $(RUN_SVC_EMAIL) \
		--member="serviceAccount:$(SVC_EMAIL)" \
		--role="roles/iam.serviceAccountUser"
	gcloud iam service-accounts add-iam-policy-binding $(SVC_EMAIL) \
		--member="serviceAccount:$(SVC_EMAIL)" \
		--role="roles/iam.serviceAccountUser"

	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member=serviceAccount:$(SVC_EMAIL) \
		--role=roles/artifactregistry.writer

	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member=serviceAccount:$(SVC_EMAIL) \
		--role=roles/run.admin

	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member=serviceAccount:$(SVC_EMAIL) \
		--role=roles/cloudscheduler.admin

iam-cloud-run: # cloud run SA
	gcloud iam service-accounts create $(RUN_SVC_ACCT) \
		--description="Service account for NRL data ingestion" \
		--display-name="NRL Data Ingest Service Account"

	gcloud iam service-accounts keys create ~/.gcp/$(RUN_SVC_ACCT)-key.json \
		--iam-account=$(RUN_SVC_EMAIL)

	gcloud storage buckets add-iam-policy-binding gs://$(DEV_BUCKET) \
		--member=serviceAccount:$(RUN_SVC_EMAIL) \
		--role=roles/storage.admin

	gcloud storage buckets add-iam-policy-binding gs://$(PROD_BUCKET) \
		--member=serviceAccount:$(RUN_SVC_EMAIL) \
		--role=roles/storage.admin

######################################
### GHA setup
######################################

setup-gh-cli:
	brew install gh
	gh auth-login

add-secrets-gh:
	gh secret set SVC_KEY < ~/.gcp/$(SVC_ACCT)-key.json

######################################
### Lint, test
######################################

lint:
	poetry run ruff check --fix
	poetry run ruff format

unit-test:
	poetry run pytest

######################################
### Auth
######################################

gcloud-auth:
	gcloud config set account $(USERNAME)

# run this locally before push and deploy to better simulate GHA environment
gcloud-auth-sa:
	gcloud auth activate-service-account --key-file=$(HOME)/.gcp/nrl-deployer-key.json


######################################
### Scraper
######################################

run-scraper-local: lint unit-test
# 	export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/$(RUN_SVC_ACCT)-key.json
	poetry run python -m scraper.scraper.run

build-scraper:
	docker buildx build -f ./Dockerfile --platform linux/amd64 -t $(SCRAPER_IMAGE) ..

run-scraper-local-docker: build
	docker run --rm \
			--env ENV=dev \
			--name scraper-container \
			-v ~/.gcp/nrl-data-ingest-key.json:/secrets/$(RUN_SVC_ACCT)-key.json \
 			-v "$$(pwd)/../logs:/app/logs" \
			-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/$(RUN_SVC_ACCT)-key.json \
			$(SCRAPER_IMAGE)

run-local-docker-it: build
	docker run -it --rm --entrypoint /bin/bash $(SCRAPER_IMAGE)

SCRAPER_IMAGE_TAG=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(DOCKER_REPO)/$(SCRAPER_IMAGE):latest
push-scraper:
	docker tag $(SCRAPER_IMAGE) $(SCRAPER_IMAGE_TAG)
	docker push $(SCRAPER_IMAGE_TAG)

deploy-dev-scraper:
	gcloud run jobs deploy $(SCRAPER_JOB_DEV) \
		--image $(SCRAPER_IMAGE_TAG) \
		--region $(REGION) \
		--memory 4Gi
		--service-account $(SCRAPER_SVC_EMAIL) \
		--set-env-vars ENV=dev

schedule-dev-scraper:
	gcloud scheduler jobs create http $(SCRAPER_SCHEDULE_NAME_DEV) \
	--location $(REGION) \
	--schedule="0 7 * 3-10 3" \
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT_ID)/locations/$(REGION)/jobs/$(SCRAPER_JOB_DEV):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-dev-scraper:
	gcloud run jobs execute nrl-scraper-dev --wait --region $(REGION)

deploy-prod-scraper:
	gcloud run jobs deploy $(SCRAPER_JOB_PROD) \
		--image $(SCRAPER_IMAGE_TAG) \
		--region $(REGION) \
		--memory 4Gi
		--service-account $(SCRAPER_SVC_EMAIL) \
		--set-env-vars ENV=prod

schedule-prod-scraper:
	gcloud scheduler jobs create http $(SCRAPER_SCHEDULE_NAME_PROD) \
	--location $(REGION) \
	--schedule="0 7 * 3-10 3" \
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT_ID)/locations/$(REGION)/jobs/$(SCRAPER_JOB_PROD):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-prod-scraper:
	gcloud run jobs execute nrl-scraper-prod --wait --region $(REGION)


######################################
### Feature engineering
######################################
