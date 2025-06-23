source ../gcp.env
gcloud storage buckets create gs://$DEV_BUCKET --location $REGION
gcloud storage buckets create gs://$PROD_BUCKET --location $REGION