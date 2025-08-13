include .env
export

include make/test.mk

######################################
### Scraper
######################################

run-local: lint unit-test
# 	export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/$(RUN_SVC_ACCT)-key.json
	poetry run python -m scraper.scraper.run

build:
	docker buildx build -f scraper/Dockerfile --platform linux/amd64 -t $(SCRAPER_IMAGE) .

run-local-docker: build
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
push:
	docker tag $(SCRAPER_IMAGE) $(SCRAPER_IMAGE_TAG)
	docker push $(SCRAPER_IMAGE_TAG)

deploy-dev:
	gcloud run jobs deploy $(SCRAPER_JOB_DEV) \
		--image $(SCRAPER_IMAGE_TAG) \
		--region $(REGION) \
		--memory 4Gi
		--service-account $(SCRAPER_SVC_EMAIL) \
		--set-env-vars ENV=dev

schedule-dev:
	gcloud scheduler jobs create http $(SCRAPER_SCHEDULE_NAME_DEV) \
	--location $(REGION) \
	--schedule="0 7 * 3-10 3" \
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT_ID)/locations/$(REGION)/jobs/$(SCRAPER_JOB_DEV):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-dev:
	gcloud run jobs execute nrl-dev --wait --region $(REGION)

deploy-prod:
	gcloud run jobs deploy $(SCRAPER_JOB_PROD) \
		--image $(SCRAPER_IMAGE_TAG) \
		--region $(REGION) \
		--memory 4Gi
		--service-account $(SCRAPER_SVC_EMAIL) \
		--set-env-vars ENV=prod

schedule-prod:
	gcloud scheduler jobs create http $(SCRAPER_SCHEDULE_NAME_PROD) \
	--location $(REGION) \
	--schedule="0 7 * 3-10 3" \
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT_ID)/locations/$(REGION)/jobs/$(SCRAPER_JOB_PROD):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-prod:
	gcloud run jobs execute nrl-prod --wait --region $(REGION)
