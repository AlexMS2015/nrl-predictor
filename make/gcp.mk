include .env
export

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
		--display-name="NRL Cloud Run Service Account"

	gcloud iam service-accounts keys create ~/.gcp/$(RUN_SVC_ACCT)-key.json \
		--iam-account=$(RUN_SVC_EMAIL)

	gcloud storage buckets add-iam-policy-binding gs://$(DEV_BUCKET) \
		--member=serviceAccount:$(RUN_SVC_EMAIL) \
		--role=roles/storage.admin

	gcloud storage buckets add-iam-policy-binding gs://$(PROD_BUCKET) \
		--member=serviceAccount:$(RUN_SVC_EMAIL) \
		--role=roles/storage.admin
