import os
from cdown.config import load_config
from cdown.input_provider import get_provider
from cdown.downloader import download_and_process_files
from cdown.uploader import Uploader
from cdown.cmd import parse_args
from tqdm import tqdm

def main():
    """Main function to run the downloader."""
    args = parse_args()
    config = load_config(args.config)

    provider = get_provider(config)
    urls = list(set(provider.get_urls()))

    uploader = Uploader(
        config["gcs"]["project_id"],
        config["gcs"]["bucket_name"],
        config["gcs"]["destination_path"],
    )

    def upload_and_cleanup(url, local_path):
        """Callback function to upload a file and then delete it."""
        try:
            uploader.upload_file(local_path, url)
        except Exception as e:
            tqdm.write(f"Failed to upload {url}: {e}")
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    downloader_config = config["downloader"]
    uploader_for_check = uploader if config["resume"]["enabled"] else None
    
    download_and_process_files(
        urls,
        downloader_config["download_dir"],
        downloader_config["max_threads"],
        downloader_config["max_retries"],
        downloader_config["retry_wait_time"],
        uploader=uploader_for_check,
        callback=upload_and_cleanup,
    )

if __name__ == "__main__":
    main()
