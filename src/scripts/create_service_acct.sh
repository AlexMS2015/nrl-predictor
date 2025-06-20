PROJECT=$(gcloud config get-value project)
BUCKET=nrl-data-dev
REGION=australia-southeast1
SVC_ACCT=nrl-data-ingest
SVC_PRINCIPAL=${SVC_ACCT}@${PROJECT_ID}.iam.gserviceaccount.com

# gcloud storage buckets create gs://$BUCKET --location $REGION