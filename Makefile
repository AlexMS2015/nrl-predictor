scraper-build-docker:
	docker build -f src/scraping/Dockerfile -t scraper-image .
	
scraper-run-docker: scraper-build-docker
	docker run --rm scraper-image --env-file .env --name scraper-container

# --dry-run -> can be passed to run.py to see what would be done without actually running it