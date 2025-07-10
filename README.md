# cdown: A Multi-threaded Cloud Downloader

`cdown` is a powerful and configurable multi-threaded downloader written in Python. It can read a list of URLs from various sources, download the files concurrently, and upload them to Google Cloud Storage. The GCS object name is a hash of the source URL, ensuring that a URL is only ever downloaded and stored once.

## Features

*   **Concurrent Downloading and Uploading**: Downloads and uploads multiple files in parallel to maximize throughput.
*   **Idempotent**: By hashing the source URL to create the GCS object name, `cdown` ensures that a file from a given URL is only downloaded once.
*   **Resumable**: Can resume a previous run and automatically skips files that already exist in the destination.
*   **Multiple Input Sources**: Reads URLs from:
    *   CSV files
    *   BigQuery tables
    *   Google Sheets
    *   Plain text files
*   **Configurable**: All aspects of the downloader can be configured through a `config.yaml` file.
*   **Error Handling**: Retries downloads on failure with configurable wait times.

## Installation

You can install `cdown` directly from its GitHub repository using `uv`:

```bash
uv tool install git+https://github.com/codescv/cdown.git
```

## Usage

Once installed, you can run the downloader from the command line:

```bash
cdown --config /path/to/your/config.yaml
```

### Command-Line Options

*   `--config`: Specifies the path to the configuration file. Defaults to `config.yaml` in the current directory.

### Configuration

The downloader is configured using a YAML file. Here is an overview of the available options:

```yaml
# Input configuration
input:
  type: "csv" # Options: "csv", "bigquery", "google_sheet", "text"
  source: "path/to/your/input.csv" # Path to file, BigQuery table ID, or Google Sheet name
  url_column: "url" # Required for "csv", "bigquery", and "google_sheet" types

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

For Google Sheets, you may also need to configure OAuth 2.0. Please refer to the [gspread authentication documentation](https://docs.gspread.org/en/latest/oauth2.html) for detailed instructions.

## Development

To work on `cdown` locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/codescv/cdown.git
    cd cdown
    ```

2.  **Create and activate a virtual environment using `uv`:**
    ```bash
    uv sync
    source .venv/bin/activate
    ```
    This should automatically install the cdown script in the virtual env.

3.  **Run the tool:**
    ```bash
    cdown --config config.yaml
    ```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
