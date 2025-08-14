from google.cloud import storage
from loguru import logger


class GCSClient:
    """
    A client for interacting with Google Cloud Storage.

    Provides methods to upload and download files to and from a specified GCS bucket.
    """

    def __init__(self, bucket: str):
        self.client = storage.Client(project="nrl-predictor-463403")
        self.bucket = self.client.bucket(bucket)

    def upload_to_gcs(self, src_file: str, dest_blob: str) -> None:
        """Uploads a file to Google Cloud Storage."""
        blob = self.bucket.blob(dest_blob)
        logger.info(f"Uploading to {blob}")
        blob.upload_from_filename(src_file)

    def download_from_gcs(self, src_blob: str, dest_file: str) -> None:
        """Downloads a file from Google Cloud Storage."""
        blob = self.bucket.blob(src_blob)
        logger.info(f"Downloading from {blob}")
        blob.download_to_filename(dest_file)

    def get_blobs(self, prefix):
        return self.client.list_blobs(self.bucket, prefix=prefix)
