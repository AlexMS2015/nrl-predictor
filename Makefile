include src/gcp.env
export

scraper-build:
	docker buildx build -f src/scraping/Dockerfile --platform linux/amd64 -t $(SCRAPER_IMAGE) .

scraper-run-local: scraper-build
	docker run --rm \
			--env ENV=dev \
			--name scraper-container \
			-v ~/.gcp/nrl-data-ingest-key.json:/secrets/nrl-data-ingest-key.json \
			-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/nrl-data-ingest-key.json \
			$(SCRAPER_IMAGE) 

SCRAPER_IMAGE_TAG=$(REGION)-docker.pkg.dev/$(PROJECT)/$(DOCKER_REPO)/$(SCRAPER_IMAGE):latest
scraper-push: scraper-build
	docker tag $(SCRAPER_IMAGE) $(SCRAPER_IMAGE_TAG)
	docker push $(SCRAPER_IMAGE_TAG)

scraper-deploy-dev: scraper-push
	gcloud run jobs deploy $(SCRAPER_JOB_DEV) \
		--image $(SCRAPER_IMAGE_TAG) \
		--region $(REGION) \
		--service-account $(SVC_EMAIL) \
		--set-env-vars ENV=dev

scraper-deploy-prod: scraper-push
	gcloud run jobs deploy $(SCRAPER_JOB_PROD) \
		--image $(SCRAPER_IMAGE_TAG) \
		--region $(REGION) \
		--service-account $(SVC_EMAIL) \
		--set-env-vars ENV=prod

# --dry-run -> can be passed to run.py to see what would be done without actually running it