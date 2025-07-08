from google.cloud import storage
import os

class Uploader:
    """Handles uploading files to Google Cloud Storage."""

    def __init__(self, project_id, bucket_name, destination_path):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.destination_path = destination_path
        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(self, local_path, source_url):
        """Uploads a file to GCS."""
        file_name = os.path.basename(source_url.split("?")[0])
        gcs_path = os.path.join(self.destination_path, file_name)
        blob = self.bucket.blob(gcs_path)

        blob.upload_from_filename(local_path)
        return f"gs://{self.bucket_name}/{gcs_path}"

    def check_file_exists(self, source_url):
        """Checks if a file already exists in GCS to avoid re-downloading."""
        file_name = os.path.basename(source_url.split("?")[0])
        gcs_path = os.path.join(self.destination_path, file_name)
        blob = self.bucket.blob(gcs_path)
        return blob.exists()
