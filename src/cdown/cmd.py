import argparse

def parse_args():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(description="A tool for downloading files and uploading them to GCS.")
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the configuration file.",
    )
    return parser.parse_args()
