import os
from cdown.config import load_config
from cdown.input_provider import get_provider
from cdown.downloader import download_files
from cdown.uploader import Uploader
from cdown.cmd import parse_args

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

    if config["resume"]["enabled"]:
        print("Resume enabled. Checking for existing files in GCS.")
        urls_to_download = [
            url for url in urls if not uploader.check_file_exists(url)
        ]
        print(f"Found {len(urls) - len(urls_to_download)} existing files. Skipping them.")
    else:
        urls_to_download = urls

    downloader_config = config["downloader"]
    download_results = download_files(
        urls_to_download,
        downloader_config["download_dir"],
        downloader_config["max_threads"],
        downloader_config["max_retries"],
        downloader_config["retry_wait_time"],
    )

    for url, local_path, error in download_results:
        if error:
            print(f"Failed to download {url}: {error}")
            continue

        print(f"Downloaded {url} to {local_path}")

        try:
            gcs_uri = uploader.upload_file(local_path, url)
            print(f"Uploaded {local_path} to {gcs_uri}")
        except Exception as e:
            print(f"Failed to upload {url}: {e}")
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

if __name__ == "__main__":
    main()
