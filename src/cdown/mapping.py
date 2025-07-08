import abc
import pandas as pd
from google.cloud import bigquery
import gspread
import os

class BaseMapping(abc.ABC):
    """Abstract base class for all mappings."""

    @abc.abstractmethod
    def save_mapping(self, source_url, gcs_uri):
        """Abstract method to save a mapping."""
        pass

    @abc.abstractmethod
    def get_existing_mappings(self):
        """Abstract method to get existing mappings to support resuming."""
        pass


class CsvMapping(BaseMapping):
    """Saves mappings to a CSV file."""

    def __init__(self, destination, source_column, gcs_column):
        self.destination = destination
        self.source_column = source_column
        self.gcs_column = gcs_column
        if not os.path.exists(self.destination):
            df = pd.DataFrame(columns=[self.source_column, self.gcs_column])
            df.to_csv(self.destination, index=False)


    def save_mapping(self, source_url, gcs_uri):
        """Appends a new mapping to the CSV file."""
        df = pd.DataFrame([{self.source_column: source_url, self.gcs_column: gcs_uri}])
        df.to_csv(self.destination, mode="a", header=False, index=False)

    def get_existing_mappings(self):
        """Reads the CSV file and returns a set of GCS URIs."""
        if not os.path.exists(self.destination):
            return set()
        df = pd.read_csv(self.destination)
        return set(df[self.gcs_column].tolist())


class BigQueryMapping(BaseMapping):
    """Saves mappings to a BigQuery table."""

    def __init__(self, destination, source_column, gcs_column, project_id):
        self.destination = destination
        self.source_column = source_column
        self.gcs_column = gcs_column
        self.project_id = project_id
        self.client = bigquery.Client(project=self.project_id)
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        """Creates the BigQuery table if it doesn't exist."""
        schema = [
            bigquery.SchemaField(self.source_column, "STRING", mode="REQUIRED"),
            bigquery.SchemaField(self.gcs_column, "STRING", mode="REQUIRED"),
        ]
        table = bigquery.Table(self.destination, schema=schema)
        self.client.create_table(table, exists_ok=True)


    def save_mapping(self, source_url, gcs_uri):
        """Inserts a new mapping into the BigQuery table."""
        rows_to_insert = [{self.source_column: source_url, self.gcs_column: gcs_uri}]
        errors = self.client.insert_rows_json(self.destination, rows_to_insert)
        if errors:
            raise Exception(f"Encountered errors while inserting rows: {errors}")

    def get_existing_mappings(self):
        """Queries the BigQuery table and returns a set of GCS URIs."""
        try:
            query = f"SELECT {self.gcs_column} FROM `{self.destination}`"
            query_job = self.client.query(query)
            rows = query_job.result()
            return set(row[self.gcs_column] for row in rows)
        except Exception:
            return set()


class GoogleSheetMapping(BaseMapping):
    """Saves mappings to a Google Sheet."""

    def __init__(self, destination, source_column, gcs_column):
        self.destination = destination
        self.source_column = source_column
        self.gcs_column = gcs_column
        gc = gspread.service_account()
        self.sheet = gc.open(self.destination).sheet1
        self._create_header_if_not_exists()

    def _create_header_if_not_exists(self):
        """Creates the header row if it doesn't exist."""
        if not self.sheet.get_all_values():
            self.sheet.append_row([self.source_column, self.gcs_column])

    def save_mapping(self, source_url, gcs_uri):
        """Appends a new mapping to the Google Sheet."""
        self.sheet.append_row([source_url, gcs_uri])

    def get_existing_mappings(self):
        """Reads the Google Sheet and returns a set of GCS URIs."""
        records = self.sheet.get_all_records()
        if not records:
            return set()
        df = pd.DataFrame(records)
        return set(df[self.gcs_column].tolist())


def get_mapping(config):
    """Factory function to get the correct mapping based on config."""
    output_config = config["output"]
    mapping_type = output_config["type"]

    if mapping_type == "csv":
        return CsvMapping(
            output_config["destination"],
            output_config["source_column"],
            output_config["gcs_column"],
        )
    elif mapping_type == "bigquery":
        return BigQueryMapping(
            output_config["destination"],
            output_config["source_column"],
            output_config["gcs_column"],
            config["gcs"]["project_id"],
        )
    elif mapping_type == "google_sheet":
        return GoogleSheetMapping(
            output_config["destination"],
            output_config["source_column"],
            output_config["gcs_column"],
        )
    else:
        raise ValueError(f"Unsupported mapping type: {mapping_type}")
