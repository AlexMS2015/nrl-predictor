source ../gcp.env

gcloud iam service-accounts create $SVC_ACCT \
    --description="Service account for NRL data ingestion" \
    --display-name="NRL Data Ingest Service Account"

gcloud iam service-accounts add-iam-policy-binding $SVC_EMAIL \
  --member="user:$USERNAME" \
  --role="roles/iam.serviceAccountUser"

gcloud project add-iam-policy-binding $PROJECT \
    --member=serviceAccount:$SVC_EMAIL \
    --role=roles/run.jobsExecutor

gcloud storage buckets add-iam-policy-binding gs://$DEV_BUCKET \
    --member=serviceAccount:$SVC_EMAIL \
    --role=roles/storage.admin

gcloud storage buckets update gs://$PROD_BUCKET \
    --uniform-bucket-level-access

gcloud storage buckets add-iam-policy-binding gs://$PROD_BUCKET \
    --member=serviceAccount:$SVC_EMAIL \
    --role=roles/storage.admin