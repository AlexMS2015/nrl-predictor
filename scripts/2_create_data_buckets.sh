source ../gcp.env
gcloud storage buckets create gs://$DEV_BUCKET --location $REGION
gcloud storage buckets create gs://$PROD_BUCKET --location $REGION

gcloud storage buckets update gs://$DEV_BUCKET \
    --uniform-bucket-level-access