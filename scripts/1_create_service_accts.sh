source ../gcp.env

######################################
### Service account for deployments
######################################

gcloud iam service-accounts create $SVC_ACCT \
    --description="Service account for deployments and scheduling" \
    --display-name="NRL deployer and scheduler"

gcloud iam service-accounts keys create ~/.gcp/${SVC_ACCT}-key.json \
    --iam-account=$SVC_EMAIL

# impersonation
gcloud iam service-accounts add-iam-policy-binding $SCRAPER_SVC_EMAIL \
  --member="serviceAccount:$SVC_EMAIL" \
  --role="roles/iam.serviceAccountUser"
gcloud iam service-accounts add-iam-policy-binding $SVC_EMAIL \
  --member="serviceAccount:$SVC_EMAIL" \
  --role="roles/iam.serviceAccountUser"

# artifact registry
gcloud projects add-iam-policy-binding $PROJECT \
    --member=serviceAccount:$SVC_EMAIL \
    --role=roles/artifactregistry.writer

# cloud run jobs
gcloud projects add-iam-policy-binding $PROJECT \
    --member=serviceAccount:$SVC_EMAIL \
    --role=roles/run.admin

# cloud scheduler
gcloud projects add-iam-policy-binding $PROJECT \
    --member=serviceAccount:$SVC_EMAIL \
    --role=roles/cloudscheduler.admin

######################################
### Service account for scraper jobs
######################################

gcloud iam service-accounts create $SCRAPER_SVC_ACCT \
    --description="Service account for NRL data ingestion" \
    --display-name="NRL Data Ingest Service Account"

gcloud iam service-accounts keys create ~/.gcp/${SCRAPER_SVC_ACCT}-key.json \
    --iam-account=$SCAPER_SVC_EMAIL

gcloud storage buckets add-iam-policy-binding gs://$DEV_BUCKET \
    --member=serviceAccount:$SCRAPER_SVC_EMAIL \
    --role=roles/storage.admin

gcloud storage buckets add-iam-policy-binding gs://$PROD_BUCKET \
    --member=serviceAccount:$SCRAPER_SVC_EMAIL \
    --role=roles/storage.admin
