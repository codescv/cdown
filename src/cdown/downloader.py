import requests
import os
import time
from tqdm import tqdm
from cdown.uploader import get_gcs_object_name

def download_worker(download_queue, upload_queue, config, uploader, pbar, upload_pbar):
    """
    Worker function to download files from a queue.
    """
    download_dir = config["downloader"]["download_dir"]
    max_retries = config["downloader"]["max_retries"]
    retry_wait_time = config["downloader"]["retry_wait_time"]
    resume_enabled = config["resume"]["enabled"]
    destination_path = config["gcs"]["destination_path"]

    while True:
        url = download_queue.get()
        if url is None:
            break

        try:
            if resume_enabled and uploader and uploader.check_file_exists(url):
                tqdm.write(f"Skipping already existing file: {url}")
                upload_pbar.update(1) # Also update upload progress as it's a final state
                continue

            for attempt in range(max_retries):
                try:
                    response = requests.get(url, stream=True)
                    response.raise_for_status()
                    
                    base_name = os.path.basename(url.split("?")[0])
                    if not base_name:
                        base_name = "downloaded_file"
                    
                    temp_local_path = os.path.join(download_dir, base_name)
                    
                    with open(temp_local_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    gcs_object_name = get_gcs_object_name(url, destination_path)
                    upload_queue.put({"local_path": temp_local_path, "gcs_object_name": gcs_object_name, "source_url": url})
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_wait_time)
                    else:
                        tqdm.write(f"Failed to download {url} after {max_retries} retries: {e}")
                        upload_pbar.update(1) # Also update upload progress as it's a final state
        finally:
            pbar.update(1)
            download_queue.task_done()
