include .env
export

include make/test.mk

######################################
### Local
######################################

run-local: lint unit-test
# 	export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/$(RUN_SVC_ACCT)-key.json
	poetry run python -m feature_eng.feature_eng.run

build:
	docker buildx build -f feature_eng/Dockerfile --platform linux/amd64 -t $(FEATENG_IMAGE) .

run-local-docker: build
	docker run --rm \
			--env ENV=dev \
			--name feateng-container \
			-v ~/.gcp/nrl-data-ingest-key.json:/secrets/$(RUN_SVC_ACCT)-key.json \
 			-v "$$(pwd)/../logs:/app/logs" \
			-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/$(RUN_SVC_ACCT)-key.json \
			$(FEATENG_IMAGE)

run-local-docker-it: build
	docker run -it --rm --entrypoint /bin/bash $(FEATENG_IMAGE)


######################################
### Cloud
######################################

FEATENG_IMAGE_TAG=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(DOCKER_REPO)/$(FEATENG_IMAGE):latest
push:
	docker tag $(FEATENG_IMAGE) $(FEATENG_IMAGE_TAG)
	docker push $(FEATENG_IMAGE_TAG)

deploy-dev:
	gcloud run jobs deploy $(FEATENG_JOB_DEV) \
		--image $(FEATENG_IMAGE_TAG) \
		--region $(REGION) \
		--memory 4Gi \
		--service-account $(RUN_SVC_EMAIL) \
		--set-env-vars ENV=dev

schedule-dev:
	gcloud scheduler jobs create http $(FEATENG_SCHEDULE_NAME_DEV) \
	--location $(REGION) \
	--schedule="0 9 * 3-10 3" \
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT_ID)/locations/$(REGION)/jobs/$(FEATENG_JOB_DEV):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-dev:
	gcloud run jobs execute nrl-dev --wait --region $(REGION)

deploy-prod:
	gcloud run jobs deploy $(FEATENG_JOB_PROD) \
		--image $(FEATENG_IMAGE_TAG) \
		--region $(REGION) \
		--memory 4Gi \
		--service-account $(RUN_SVC_EMAIL) \
		--set-env-vars ENV=prod

schedule-prod:
	gcloud scheduler jobs create http $(FEATENG_SCHEDULE_NAME_PROD) \
	--location $(REGION) \
	--schedule="0 9 * 3-10 3" \
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT_ID)/locations/$(REGION)/jobs/$(FEATENG_JOB_PROD):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-prod:
	gcloud run jobs execute nrl-prod --wait --region $(REGION)
