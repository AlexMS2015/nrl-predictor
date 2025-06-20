PROJECT=$(gcloud config get-value project)
BUCKET=nrl-data-prod
REGION=australia-southeast1
gcloud storage buckets create gs://$BUCKET --location $REGION