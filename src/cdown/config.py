import yaml
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _get_default_config():
    """Returns the default configuration dictionary."""
    return {
        "input": {
            "type": "text",
            "source": "urls.txt",
            "url_column": "url"
        },
        "gcs": {
            "project_id": None,
            "bucket_name": None,
            "destination_path": "downloads/"
        },
        "downloader": {
            "max_threads": 4,
            "max_retries": 3,
            "retry_wait_time": 5,
            "download_dir": "/tmp/cdown_downloads",
            "cookies_file": None
        },
        "uploader": {
            "max_threads": 4
        },
        "resume": {
            "enabled": True
        }
    }

def _override_with_env_vars(config, prefix="CDOWN"):
    """Recursively overrides config with environment variables."""
    for key, value in config.items():
        if isinstance(value, dict):
            _override_with_env_vars(value, prefix=f"{prefix}_{key.upper()}")
        else:
            env_var = f"{prefix}_{key.upper()}"
            if env_var in os.environ:
                env_value = os.environ[env_var]
                # Attempt to cast to the same type as the default value
                try:
                    original_type = type(value)
                    if original_type == bool:
                        config[key] = env_value.lower() in ('true', '1', 't')
                    elif original_type == int:
                        config[key] = int(env_value)
                    elif original_type == float:
                        config[key] = float(env_value)
                    else:
                        config[key] = env_value
                except (ValueError, TypeError):
                    config[key] = env_value


def load_config(config_path="config.yaml"):
    """
    Loads configuration from multiple sources with a defined priority:
    1. Environment variables (highest priority)
    2. config.yaml file (if it exists)
    3. Hard-coded defaults (lowest priority)
    """
    config = _get_default_config()

    # 2. Override with config.yaml if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    # Deep merge yaml_config into default config
                    for key, value in yaml_config.items():
                        if isinstance(value, dict) and isinstance(config.get(key), dict):
                            config[key].update(value)
                        else:
                            config[key] = value
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.warning(f"Could not load or parse {config_path}: {e}")
    else:
        logger.info("No config file found, using defaults and environment variables.")

    # 3. Override with environment variables
    _override_with_env_vars(config)
    
    return config
