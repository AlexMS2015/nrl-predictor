source ../gcp.env

gcloud scheduler jobs create http $SCRAPER_SCHEDULE_NAME_DEV \
  --location $REGION \
  --schedule="0 7 * 3-10 3" \
  --uri="https://run.googleapis.com/v2/projects/${PROJECT}/locations/${REGION}/jobs/${SCRAPER_JOB_DEV}:run" \
  --http-method POST \
  --oauth-service-account-email $SVC_EMAIL