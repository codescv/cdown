import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def download_file(url, download_dir, max_retries, retry_wait_time, uploader=None, callback=None):
    """
    Downloads a single file with retries.
    If an uploader is provided, checks for existence before downloading.
    Executes a callback on successful download.
    """
    if uploader and uploader.check_file_exists(url):
        return url, None, "skipped"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            temp_local_path = os.path.join(download_dir, os.path.basename(url.split("?")[0]))
            
            with open(temp_local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if callback:
                callback(url, temp_local_path)
            
            return url, temp_local_path, None
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_wait_time)
            else:
                return url, None, e

def download_and_process_files(urls, download_dir, max_threads, max_retries, retry_wait_time, uploader=None, callback=None):
    """Downloads multiple files in parallel and processes them using a callback."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {
            executor.submit(download_file, url, download_dir, max_retries, retry_wait_time, uploader, callback): url
            for url in urls
        }
        for future in tqdm(as_completed(future_to_url), total=len(urls), desc="Processing URLs"):
            url, _, result = future.result()
            if result == "skipped":
                pass
            elif result is not None:
                tqdm.write(f"Failed to download {url} after {max_retries} retries: {result}")
