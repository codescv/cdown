import requests
import tempfile
import os
import time
import yt_dlp
from tqdm import tqdm
from cdown.uploader import get_gcs_object_name


def _is_youtube_url(url):
    """Checks if a URL is a YouTube URL."""
    return "youtube.com" in url or "youtu.be" in url

def _download_youtube_video(url, download_dir, cookies_file=None):
    """Downloads a YouTube video using yt-dlp."""
    
    temp_template = os.path.join(download_dir, '%(id)s.%(ext)s')
    
    ydl_opts = {
        'outtmpl': temp_template,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': True,
    }

    if cookies_file:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8", suffix=".txt") as fp_named:
            with open(cookies_file) as f:
                fp_named.write(f.read())
            ydl_opts['cookiefile'] = fp_named.name
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info is None:
            raise yt_dlp.utils.DownloadError("Failed to extract video information.")
        
        downloaded_path = ydl.prepare_filename(info)

    final_filename = f"{info.get('title', 'youtube_video')}.mp4"
    final_path = os.path.join(download_dir, final_filename)
    
    if os.path.exists(final_path) and final_path != downloaded_path:
        video_id = info.get('id', 'unknown_id')
        base, ext = os.path.splitext(final_filename)
        final_path = os.path.join(download_dir, f"{base}_{video_id}{ext}")

    os.rename(downloaded_path, final_path)
    return final_path

def _download_standard_file(url, download_dir):
    """Downloads a standard file using requests."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    base_name = os.path.basename(url.split("?")[0])
    if not base_name:
        base_name = "downloaded_file"
    
    temp_local_path = os.path.join(download_dir, base_name)
    
    with open(temp_local_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    return temp_local_path

def download_worker(download_queue, upload_queue, config, uploader, pbar, upload_pbar):
    """
    Worker function to download files from a queue.
    It delegates to the appropriate downloader based on URL.
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
                if uploader:
                    upload_pbar.update(1)
                continue

            for attempt in range(max_retries):
                try:
                    if _is_youtube_url(url):
                        temp_local_path = _download_youtube_video(url, download_dir, config["downloader"].get("cookies_file"))
                    else:
                        temp_local_path = _download_standard_file(url, download_dir)
                    
                    if uploader:
                        gcs_object_name = get_gcs_object_name(url, destination_path)
                        upload_queue.put({"local_path": temp_local_path, "gcs_object_name": gcs_object_name, "source_url": url})
                    else:
                        # If no uploader, we're done with this file.
                        # The file remains in the local download directory.
                        pass
                    break  # Success
                except (requests.exceptions.RequestException, yt_dlp.utils.DownloadError) as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_wait_time)
                    else:
                        tqdm.write(f"Failed to download {url} after {max_retries} retries: {e}")
                        if uploader:
                            upload_pbar.update(1)
        finally:
            pbar.update(1)
            download_queue.task_done()
