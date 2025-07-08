# cdown: A Multi-threaded Cloud Downloader

`cdown` is a powerful and configurable multi-threaded downloader written in Python. It can read a list of URLs from various sources, download the files concurrently, and upload them to Google Cloud Storage. It also keeps a mapping of the downloaded files and their corresponding GCS URIs.

## Features

*   **Multi-threaded Downloading**: Downloads multiple files concurrently to speed up the process.
*   **Resumable**: Can resume downloads and avoid re-downloading files that already exist in the destination.
*   **Multiple Input Sources**: Reads URLs from:
    *   CSV files
    *   BigQuery tables
    *   Google Sheets
    *   Plain text files
*   **Flexible Output Mapping**: Stores the mapping between source URLs and GCS URIs in:
    *   CSV files
    *   BigQuery tables
    *   Google Sheets
*   **Configurable**: All aspects of the downloader can be configured through a `config.yaml` file.
*   **Error Handling**: Retries downloads on failure with configurable wait times.

## Installation

The project is managed using `uv`.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cdown
    ```

2.  **Create a virtual environment:**
    ```bash
    uv venv
    ```

3.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

4.  **Install the project and its dependencies:**
    ```bash
    uv pip install -e .
    ```

## Configuration

The downloader is configured using the `config.yaml` file. Here is an overview of the available options:

```yaml
# Input configuration
input:
  type: "csv" # Options: "csv", "bigquery", "google_sheet", "text"
  source: "path/to/your/input.csv" # Path to file, BigQuery table ID, or Google Sheet name
  url_column: "url" # For CSV, BigQuery, Google Sheet

# Output configuration (for mapping)
output:
  type: "csv" # Options: "csv", "bigquery", "google_sheet"
  destination: "path/to/your/mapping.csv" # Path to file, BigQuery table ID, or Google Sheet name
  source_column: "source_url"
  gcs_column: "gcs_uri"

# GCS Uploader configuration
gcs:
  project_id: "your-gcp-project-id"
  bucket_name: "your-gcs-bucket-name"
  destination_path: "downloads/" # Optional: a prefix in the bucket

# Downloader configuration
downloader:
  max_threads: 8
  max_retries: 3
  retry_wait_time: 5 # in seconds
  download_dir: "/tmp/cdown_downloads" # Temporary local directory for downloads

# Resume functionality
resume:
  enabled: true
```

### Authentication

To use Google Cloud services (BigQuery, Google Cloud Storage, Google Sheets), you need to be authenticated. The recommended way is to use Application Default Credentials (ADC). You can set this up by running:

```bash
gcloud auth application-default login
```

For Google Sheets, you may need to enable the Google Sheets API in your GCP project and configure OAuth 2.0.

## Usage

Once you have configured `config.yaml`, you can run the downloader using the following command:

```bash
cdown
```

The script will read the URLs from your specified source, download them, upload them to GCS, and save the mappings to your specified destination.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
