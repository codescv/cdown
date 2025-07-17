# cdown: A Multi-threaded Cloud Downloader

`cdown` is a powerful and configurable multi-threaded downloader written in Python. It can read a list of URLs from various sources, download the files concurrently, and optionally upload them to Google Cloud Storage. It now supports downloading from YouTube.

## Features

*   **YouTube Support**: Downloads videos from YouTube using `yt-dlp`.
*   **Concurrent Downloading and Uploading**: Downloads and uploads multiple files in parallel to maximize throughput.
*   **Idempotent**: By hashing the source URL to create the GCS object name, `cdown` ensures that a file from a given URL is only downloaded once.
*   **Resumable**: Can resume a previous run and automatically skips files that already exist in the destination.
*   **Multiple Input Sources**: Reads URLs from CSV files, BigQuery tables, Google Sheets, or plain text files.
*   **Flexible Configuration**: Configure via a `config.yaml` file, environment variables, or a combination of both. Ideal for local and cloud environments like Google Cloud Run.
*   **Error Handling**: Retries downloads on failure with configurable wait times.

## Installation

You can install `cdown` directly from its GitHub repository using `uv`:

```bash
uv tool install git+https://github.com/codescv/cdown.git
```

## Usage

### Command-Line Options

*   `--config`: Specifies the path to the configuration file. Defaults to `config.yaml` in the current directory.

```bash
cdown --config /path/to/your/config.yaml
```

### Configuration

`cdown` uses a hierarchical configuration system with the following priority:

1.  **Environment Variables** (Highest priority)
2.  **`config.yaml` file**
3.  **Default values** (Lowest priority)

This allows you to set base configurations in a file and override them for specific environments (like Docker or Google Cloud Run) using environment variables.

#### Environment Variables

Environment variables must be prefixed with `CDOWN_`.

**Examples:**
*   `gcs.project_id` becomes `CDOWN_GCS_PROJECT_ID`
*   `downloader.max_threads` becomes `CDOWN_DOWNLOADER_MAX_THREADS`

#### `config.yaml`

Here is an overview of the available options in the `config.yaml` file:

```yaml
# Input configuration
input:
  type: "csv" # Options: "csv", "bigquery", "google_sheet", "text"
  source: "path/to/your/input.csv" # Path to file, BQ table, or Google Sheet
  url_column: "url" # Required for "csv", "bigquery", and "google_sheet"

# GCS Uploader configuration (optional)
# If project_id and bucket_name are not provided, upload is disabled.
gcs:
  project_id: "your-gcp-project-id"
  bucket_name: "your-gcs-bucket-name"
  destination_path: "downloads/"

# Downloader configuration
downloader:
  max_threads: 8
  max_retries: 3
  retry_wait_time: 5 # in seconds
  download_dir: "/tmp/cdown_downloads"
  cookies_file: "/path/to/your/cookies.txt" # Optional: Path to a cookies file for yt-dlp

# Uploader configuration
uploader:
  max_threads: 8

# Resume functionality
resume:
  enabled: true
```

### Authentication

To use Google Cloud services (BigQuery, GCS, Google Sheets), you need to be authenticated. The recommended way is to use Application Default Credentials (ADC).

```bash
gcloud auth application-default login
```

## Running on Google Cloud Run

This project includes a `Dockerfile` for easy containerization, which is ideal for deployment on services like Google Cloud Run.

1.  **Create Artifact Registry Repo:**
    ```bash
    gcloud artifacts repositories create cdown --project=your-gcp-project --location=us-central1 --repository-format=docker
    ```

2.  **Build the Image**
    ```bash
    gcloud builds submit --config cloudbuild.yaml --project=your-gcp-project
    ```

3.  **Run with Cloud Run**
Now you can run with a [Cloud Run Job](https://pantheon.corp.google.com/run/jobs/create).
Use enviroment varibles to override the input and output etc.


## Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/codescv/cdown.git
    cd cdown
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    uv sync
    source .venv/bin/activate
    ```

3.  **Run the tool:**
    ```bash
    cdown --config config.yaml
    ```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
