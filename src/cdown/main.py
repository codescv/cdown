import os
from queue import Queue
from threading import Thread
from cdown.config import load_config
from cdown.input_provider import get_provider
from cdown.downloader import download_worker
from cdown.uploader import Uploader, upload_worker
from cdown.cmd import parse_args
from tqdm import tqdm

def main():
    """Main function to run the downloader."""
    args = parse_args()
    config = load_config(args.config)

    provider = get_provider(config)
    urls = list(set(provider.get_urls()))
    
    if not urls:
        print("No URLs to process.")
        return

    download_queue = Queue()
    upload_queue = Queue()

    uploader = Uploader(
        config["gcs"]["project_id"],
        config["gcs"]["bucket_name"],
        config["gcs"]["destination_path"],
    )

    downloader_config = config["downloader"]
    num_download_threads = downloader_config["max_threads"]
    num_upload_threads = config.get("uploader", {}).get("max_threads", num_download_threads)

    # Create download directory safely
    download_dir = downloader_config["download_dir"]
    os.makedirs(download_dir, exist_ok=True)

    with tqdm(total=len(urls), desc="Downloading") as download_pbar, \
         tqdm(total=len(urls), desc="Uploading") as upload_pbar:

        # Create and start download workers
        download_threads = []
        for _ in range(num_download_threads):
            thread = Thread(target=download_worker, args=(download_queue, upload_queue, config, uploader, download_pbar, upload_pbar))
            thread.start()
            download_threads.append(thread)

        # Create and start upload workers
        upload_threads = []
        for _ in range(num_upload_threads):
            thread = Thread(target=upload_worker, args=(upload_queue, uploader, upload_pbar))
            thread.start()
            upload_threads.append(thread)

        # Populate the download queue
        for url in urls:
            download_queue.put(url)

        # Wait for all downloads to complete
        download_queue.join()

        # Signal download workers to stop
        for _ in range(num_download_threads):
            download_queue.put(None)

        # Wait for all uploads to complete
        upload_queue.join()

        # Signal upload workers to stop
        for _ in range(num_upload_threads):
            upload_queue.put(None)

        # Wait for all threads to finish
        for thread in download_threads:
            thread.join()
        for thread in upload_threads:
            thread.join()
    
    print("Execution complete.")

if __name__ == "__main__":
    main()
