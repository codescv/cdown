import abc
import pandas as pd
from google.cloud import bigquery
import gspread
from google.oauth2 import service_account

class BaseProvider(abc.ABC):
    """Abstract base class for all providers."""

    @abc.abstractmethod
    def get_urls(self):
        """Abstract method to get a list of URLs."""
        pass


class CsvProvider(BaseProvider):
    """Provides URLs from a CSV file."""

    def __init__(self, source, url_column):
        self.source = source
        self.url_column = url_column

    def get_urls(self):
        """Reads a CSV file and returns a list of URLs."""
        df = pd.read_csv(self.source)
        return df[self.url_column].tolist()


class BigQueryProvider(BaseProvider):
    """Provides URLs from a BigQuery table."""

    def __init__(self, source, url_column, project_id):
        self.source = source
        self.url_column = url_column
        self.project_id = project_id
        self.client = bigquery.Client(project=self.project_id)

    def get_urls(self):
        """Queries a BigQuery table and returns a list of URLs."""
        query = f"SELECT {self.url_column} FROM `{self.source}`"
        query_job = self.client.query(query)
        rows = query_job.result()
        return [row[self.url_column] for row in rows]


class GoogleSheetProvider(BaseProvider):
    """Provides URLs from a Google Sheet."""

    def __init__(self, source, url_column):
        self.source = source
        self.url_column = url_column
        # You might need to configure authentication for gspread
        # https://gspread.readthedocs.io/en/latest/oauth2.html
        gc = gspread.service_account()
        self.sheet = gc.open(self.source).sheet1


    def get_urls(self):
        """Reads a Google Sheet and returns a list of URLs."""
        records = self.sheet.get_all_records()
        df = pd.DataFrame(records)
        return df[self.url_column].tolist()


class TextProvider(BaseProvider):
    """Provides URLs from a plain text file."""

    def __init__(self, source):
        self.source = source

    def get_urls(self):
        """Reads a text file and returns a list of URLs."""
        with open(self.source, "r") as f:
            return [line.strip() for line in f if line.strip()]


def get_provider(config):
    """Factory function to get the correct provider based on config."""
    input_config = config["input"]
    provider_type = input_config["type"]

    if provider_type == "csv":
        return CsvProvider(input_config["source"], input_config["url_column"])
    elif provider_type == "bigquery":
        return BigQueryProvider(
            input_config["source"], input_config["url_column"], config["gcs"]["project_id"]
        )
    elif provider_type == "google_sheet":
        return GoogleSheetProvider(input_config["source"], input_config["url_column"])
    elif provider_type == "text":
        return TextProvider(input_config["source"])
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")

