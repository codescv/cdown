from google.cloud import storage
import os
import hashlib
from tqdm import tqdm

def get_gcs_object_name(source_url, destination_path):
    """Calculates the GCS object name from the source URL."""
    url_hash = hashlib.sha256(source_url.encode("utf-8")).hexdigest()
    return os.path.join(destination_path, url_hash)

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
        gcs_path = get_gcs_object_name(source_url, self.destination_path)
        return f"gs://{self.bucket_name}/{gcs_path}"

    def upload_file(self, local_path, gcs_object_name):
        """Uploads a file to a specific GCS object path."""
        blob = self.bucket.blob(gcs_object_name)
        if not blob.exists():
            blob.upload_from_filename(local_path)
        
        return f"gs://{self.bucket_name}/{gcs_object_name}"

    def check_file_exists(self, source_url):
        """Checks if a file already exists in GCS to avoid re-downloading."""
        gcs_object_name = get_gcs_object_name(source_url, self.destination_path)
        blob = self.bucket.blob(gcs_object_name)
        return blob.exists()

def upload_worker(upload_queue, uploader, pbar):
    """Worker function to upload files from a queue."""
    while True:
        item = upload_queue.get()
        if item is None:
            break
        
        local_path = item["local_path"]
        gcs_object_name = item["gcs_object_name"]
        source_url = item["source_url"]

        try:
            if gcs_object_name:
                uploader.upload_file(local_path, gcs_object_name)
        except Exception as e:
            tqdm.write(f"Failed to upload {source_url}: {e}")
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)
            pbar.update(1)
            upload_queue.task_done()
