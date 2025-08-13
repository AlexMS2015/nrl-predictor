include .env
export

include make/test.mk

build:
	docker buildx build -f $(FOLDER)/Dockerfile --platform linux/amd64 -t $(IMAGE) .

######################################
### Local
######################################

run-docker: build
	docker run --rm \
			--env ENV=dev \
			--name $(CONTAINER_NAME) \
			-v ~/.gcp/nrl-data-ingest-key.json:/secrets/$(RUN_SVC_ACCT)-key.json \
 			-v "./logs:/app/logs" \
			-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/$(RUN_SVC_ACCT)-key.json \
			$(IMAGE)

run-docker-it: build
	docker run -it --rm --entrypoint /bin/bash $(IMAGE)

run-docker-dryrun: build
	docker run --rm \
 			-v "./logs:/app/logs" \
			$(IMAGE) \
			--dry-run

######################################
### Cloud
######################################

IMAGE_TAG=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(DOCKER_REPO)/$(IMAGE):latest
push:
	docker tag $(IMAGE) $(IMAGE_TAG)
	docker push $(IMAGE_TAG)

deploy-dev:
	gcloud run jobs deploy $(JOB_DEV) \
		--image $(IMAGE_TAG) \
		--region $(REGION) \
		--memory 4Gi \
		--service-account $(RUN_SVC_EMAIL) \
		--set-env-vars ENV=dev

schedule-dev:
	gcloud scheduler jobs create http $(SCHEDULE_NAME_DEV) \
	--location $(REGION) \
	--schedule="0 9 * 3-10 3" \
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT_ID)/locations/$(REGION)/jobs/$(JOB_DEV):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-dev:
	gcloud run jobs execute $(JOB_DEV) --wait --region $(REGION)

deploy-prod:
	gcloud run jobs deploy $(JOB_PROD) \
		--image $(IMAGE_TAG) \
		--region $(REGION) \
		--memory 4Gi \
		--service-account $(RUN_SVC_EMAIL) \
		--set-env-vars ENV=prod

schedule-prod:
	gcloud scheduler jobs create http $(SCHEDULE_NAME_PROD) \
	--location $(REGION) \
	--schedule="0 9 * 3-10 3" \
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT_ID)/locations/$(REGION)/jobs/$(JOB_PROD):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-prod:
	gcloud run jobs execute $(JOB_PROD) --wait --region $(REGION)
