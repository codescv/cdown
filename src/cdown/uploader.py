from google.cloud import storage
import os
import hashlib

def _calculate_hash(url):
    """Calculates the SHA256 hash of a URL."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

class Uploader:
    """Handles uploading files to Google Cloud Storage."""

    def __init__(self, project_id, bucket_name, destination_path):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.destination_path = destination_path
        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    def get_gcs_uri(self, source_url):
        """Returns the GCS URI for a given source URL."""
        url_hash = _calculate_hash(source_url)
        gcs_path = os.path.join(self.destination_path, url_hash)
        return f"gs://{self.bucket_name}/{gcs_path}"

    def upload_file(self, local_path, source_url):
        """Uploads a file to GCS using the hash of the source_url as the name."""
        gcs_uri = self.get_gcs_uri(source_url)
        gcs_path = gcs_uri.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(gcs_path)

        if not blob.exists():
            blob.upload_from_filename(local_path)
        
        return gcs_uri

    def check_file_exists(self, source_url):
        """Checks if a file already exists in GCS to avoid re-downloading."""
        gcs_uri = self.get_gcs_uri(source_url)
        gcs_path = gcs_uri.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(gcs_path)
        return blob.exists()
