include ../gcp.env
export

# should run this before any gcloud commands to simulate the GHA environment:
# gcloud auth activate-service-account --key-file=$HOME/.gcp/nrl-deployer-key.json

lint:
	poetry run ruff check --fix
	poetry run ruff format

unit-test:
	poetry run pytest

run-local: lint test
	poetry install
	export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
	poetry run python -m scraper.run

build:
	docker buildx build -f ./Dockerfile --platform linux/amd64 -t $(SCRAPER_IMAGE) ..

run-local-docker: build
# where do the logs go?
	docker run --rm \
			--env ENV=dev \
			--name scraper-container \
			-v ~/.gcp/nrl-data-ingest-key.json:/secrets/nrl-data-ingest-key.json \
 			-v "$$(pwd)/../logs:/app/logs" \
			-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/nrl-data-ingest-key.json \
			$(SCRAPER_IMAGE)

run-local-docker-it: build
	docker run -it --rm --entrypoint /bin/bash $(SCRAPER_IMAGE)

# run this locally before push and deploy to better simulate GHA environment
gcloud-auth:
	gcloud auth activate-service-account --key-file=$HOME/.gcp/nrl-deployer-key.json

SCRAPER_IMAGE_TAG=$(REGION)-docker.pkg.dev/$(PROJECT)/$(DOCKER_REPO)/$(SCRAPER_IMAGE):latest
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
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT)/locations/$(REGION)/jobs/$(SCRAPER_JOB_DEV):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-dev:
	gcloud run jobs execute nrl-scraper-dev --wait --region $(REGION)

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
	--uri="https://run.googleapis.com/v2/projects/$(PROJECT)/locations/$(REGION)/jobs/$(SCRAPER_JOB_PROD):run" \
	--http-method POST \
	--oauth-service-account-email $(SVC_EMAIL)

run-prod:
	gcloud run jobs execute nrl-scraper-prod --wait --region $(REGION)

# --dry-run -> can be passed to run.py to see what would be done without actually running it
