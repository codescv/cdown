import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_file(url, download_dir, max_retries, retry_wait_time):
    """Downloads a single file with retries."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            file_name = os.path.basename(url.split("?")[0])
            local_path = os.path.join(download_dir, file_name)
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return url, local_path, None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_wait_time)
            else:
                return url, None, e

def download_files(urls, download_dir, max_threads, max_retries, retry_wait_time):
    """Downloads multiple files in parallel using a thread pool."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {
            executor.submit(download_file, url, download_dir, max_retries, retry_wait_time): url
            for url in urls
        }
        for future in as_completed(future_to_url):
            yield future.result()
