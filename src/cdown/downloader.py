import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_file(url, download_dir, max_retries, retry_wait_time, callback=None):
    """Downloads a single file with retries and executes a callback on success."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Create a temporary file path
            temp_local_path = os.path.join(download_dir, os.path.basename(url.split("?")[0]))
            
            with open(temp_local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if callback:
                callback(url, temp_local_path)
            
            return url, temp_local_path, None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_wait_time)
            else:
                return url, None, e

def download_and_process_files(urls, download_dir, max_threads, max_retries, retry_wait_time, callback=None):
    """Downloads multiple files in parallel and processes them using a callback."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {
            executor.submit(download_file, url, download_dir, max_retries, retry_wait_time, callback): url
            for url in urls
        }
        for future in as_completed(future_to_url):
            _, _, error = future.result()
            if error:
                url = future_to_url[future]
                print(f"Failed to download {url} after {max_retries} retries.")
