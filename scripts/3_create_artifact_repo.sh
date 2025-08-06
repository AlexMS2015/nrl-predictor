# Create a Docker repository in Google Artifact Registry.
# You must enable artifact registry API in your GCP project before running this script.

source ../gcp.env

gcloud artifacts repositories create $DOCKER_REPO \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for NRL predictor" \
    --project=$PROJECT

# configure Docker to use the Google Cloud CLI to authenticate requests to Artifact Registry.
gcloud auth configure-docker $REGION-docker.pkg.dev
