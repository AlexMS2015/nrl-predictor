include src/gcp.env
export

scraper-build-local:
	docker build -f src/scraping/Dockerfile -t $(SCRAPER_IMAGE) .

# for local testing in dev
scraper-run-local: # scraper-build-local
	docker run --rm \
			--env ENV=dev \
			--name scraper-container \
			-v ~/.gcp/nrl-data-ingest-key.json:/secrets/nrl-data-ingest-key.json \
			-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/nrl-data-ingest-key.json \
			$(SCRAPER_IMAGE) 

scraper-build-cloud:
	docker buildx build -f src/scraping/Dockerfile --platform linux/amd64 -t $(SCRAPER_IMAGE) .

SCRAPER_IMAGE_TAG=$(REGION)-docker.pkg.dev/$(PROJECT)/$(DOCKER_REPO)/$(SCRAPER_IMAGE):latest
scraper-push: scraper-build-cloud
	docker tag $(SCRAPER_IMAGE) $(SCRAPER_IMAGE_TAG)
	docker push $(SCRAPER_IMAGE_TAG)

# scraper-combine-env-dev:
# 	cat gcp.env gcp-dev.env > gcp-combined.env

# scraper-combine-env-prod:
# 	cat src/scraper.env src/scraper-prod.env > src/scraper-combined-dev.env

# scraper-env-yaml:
# # Create a YAML file from the environment variables
# # This is used to pass environment variables to the Cloud Run service
# 	grep -v '^\s*#' src/scraper-combined.env | grep -v '^\s*$$' | \
# 	awk -F= '{ \
# 		gsub(/^[ \t]+|[ \t]+$$/, "", $$1); \
# 		gsub(/^[ \t]+|[ \t]+$$/, "", $$2); \
# 		gsub(/"/, "\\\"", $$2); \
# 		print $$1 ": \"" $$2 "\"" \
# 	}' > src/scraper-env.yaml

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